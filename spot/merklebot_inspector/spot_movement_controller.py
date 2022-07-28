import argparse
import math
import os
import time
import traceback

from bosdyn.api import robot_state_pb2
from bosdyn.api.graph_nav import graph_nav_pb2
from bosdyn.api.graph_nav import map_pb2
from bosdyn.api.graph_nav import nav_pb2
import bosdyn.client.channel
from bosdyn.client.exceptions import ResponseError
from bosdyn.client.graph_nav import GraphNavClient
from bosdyn.client.frame_helpers import get_odom_tform_body
from bosdyn.client.lease import LeaseClient, LeaseKeepAlive, ResourceAlreadyClaimedError
from bosdyn.client.math_helpers import Quat, SE3Pose, SE2Pose
from bosdyn.client.robot_command import RobotCommandClient, RobotCommandBuilder, blocking_stand
from bosdyn.client.robot_state import RobotStateClient
from bosdyn.client.estop import EstopClient, EstopEndpoint, EstopKeepAlive

import bosdyn.client.util

class SpotMovementController:
    def __init__(self, username, password, robot_ip, upload_path):
        self.username = username
        self.password = password
        self.robot_ip = robot_ip

        sdk = bosdyn.client.create_standard_sdk('ControllingSDK')

        #ROBOT
        self._robot = sdk.create_robot(robot_ip)
        self._robot.authenticate(username, password)
        self._robot.time_sync.wait_for_sync(timeout_sec=15.0)

        #LEASE
        self._lease_client = None
        self._lease = None
        self._lease_wallet = None
        self._lease_keepalive = None

        #ESTOP
        self._estop_client = self._robot.ensure_client(EstopClient.default_service_name)
        self._estop_endpoint = EstopEndpoint(self._estop_client, 'GNClient', 9.0)
        self._estop_keepalive = None

        #CLIENTS
        self._robot_command_client = self._robot.ensure_client(RobotCommandClient.default_service_name)
        self._robot_state_client = self._robot.ensure_client(RobotStateClient.default_service_name)
        self._graph_nav_client = self._robot.ensure_client(GraphNavClient.default_service_name)

        #GRAPHNAV
        self._current_graph = None
        self._current_edges = dict()
        self._current_waypoint_snapshots = dict()
        self._current_edge_snapshots = dict()
        self._current_annotation_name_to_wp_id = dict()

        #UPLOADMAP
        self._upload_filepath = upload_path[:-1] if upload_path[-1] == "/" else upload_path

    def __enter__(self):
        self.lease_control()
        self.release_estop()
        # self._upload_graph_and_snapshots()
        self.power_on_stand_up()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._robot.logger.error("Spot powered off with " + exc_val + " exception")
        self.power_off_sit_down()
        self.return_lease()
        self.set_estop()

        return True if exc_type else False

    def release_estop(self):
        self._estop_endpoint.force_simple_setup()
        self._estop_keepalive = EstopKeepAlive(self._estop_endpoint)

    def set_estop(self):
        if self._estop_keepalive:
            try:
                self._estop_keepalive.stop()
            except:
                self._robot.logger.error("Failed to set estop")
                traceback.print_exc()
            self._estop_keepalive.shutdown()
            self._estop_keepalive = None

    def lease_control(self):
        self._lease_client = self._robot.ensure_client(LeaseClient.default_service_name)
        self._lease = self._lease_client.take()
        self._lease_wallet = self._lease_client.lease_wallet
        self._lease_keepalive = bosdyn.client.lease.LeaseKeepAlive(self._lease_client, must_acquire=True)
        self._robot.logger.info("Lease acquired")

    def return_lease(self):
        self._lease_client.return_lease(self._lease)
        self._lease_keepalive.shutdown()
        self._lease_keepalive = None

    def stand_at_height(self, body_height):
        cmd = RobotCommandBuilder.synchro_stand_command(body_height=body_height)
        self._robot_command_client.robot_command(cmd)

    def power_on_stand_up(self):
        self._robot.power_on(timeout_sec=20)
        assert self._robot.is_powered_on(), "Not powered on"
        self._robot.time_sync.wait_for_sync()
        blocking_stand(self._robot_command_client, timeout_sec=10)

    def power_off_sit_down(self):
        self._robot.power_off(cut_immediately=False)

    def get_localization_state(self):
        """Get the current localization and state of the robot."""
        state = self._graph_nav_client.get_localization_state()
        print('Got localization: \n%s' % str(state.localization))
        odom_tform_body = get_odom_tform_body(state.robot_kinematics.transforms_snapshot)
        print('Got robot state in kinematic odometry frame: \n%s' % str(odom_tform_body))

    def set_initial_localization_fiducial(self):
        """Trigger localization when near a fiducial."""
        robot_state = self._robot_state_client.get_robot_state()
        current_odom_tform_body = get_odom_tform_body(
            robot_state.kinematic_state.transforms_snapshot).to_proto()
        # Create an empty instance for initial localization since we are asking it to localize
        # based on the nearest fiducial.
        localization = nav_pb2.Localization()
        self._graph_nav_client.set_localization(initial_guess_localization=localization,
                                                ko_tform_body=current_odom_tform_body)

    def set_initial_localization_waypoint(self, destination_waypoint_id):
        """Trigger localization to a waypoint."""
        # Take the first argument as the localization waypoint.

        robot_state = self._robot_state_client.get_robot_state()
        current_odom_tform_body = get_odom_tform_body(
            robot_state.kinematic_state.transforms_snapshot).to_proto()
        # Create an initial localization to the specified waypoint as the identity.
        localization = nav_pb2.Localization()
        localization.waypoint_id = destination_waypoint_id
        localization.waypoint_tform_body.rotation.w = 1.0
        self._graph_nav_client.set_localization(
            initial_guess_localization=localization,
            # It's hard to get the pose perfect, search +/-20 deg and +/-20cm (0.2m).
            max_distance=0.2,
            max_yaw=20.0 * math.pi / 180.0,
            fiducial_init=graph_nav_pb2.SetLocalizationRequest.FIDUCIAL_INIT_NO_FIDUCIAL,
            ko_tform_body=current_odom_tform_body)

    def print_graph_waypoint_and_edge_ids(self):
        graph = self._graph_nav_client.download_graph()
        if graph is None:
            print("Empty graph.")
            return
        self._current_graph = graph
        localization_id = self._graph_nav_client.get_localization_state().localization.waypoint_id

        # Update and print waypoints and edges
        self._current_annotation_name_to_wp_id, self._current_edges = update_waypoints_and_edges(graph, localization_id)

    def _upload_graph_and_snapshots(self):
        """Upload the graph and snapshots to the robot."""
        print("Loading the graph from disk into local storage...")
        with open(self._upload_filepath + "/graph", "rb") as graph_file:
            # Load the graph from disk.
            data = graph_file.read()
            self._current_graph = map_pb2.Graph()
            self._current_graph.ParseFromString(data)
            print("Loaded graph has {} waypoints and {} edges".format(
                len(self._current_graph.waypoints), len(self._current_graph.edges)))
        for waypoint in self._current_graph.waypoints:
            # Load the waypoint snapshots from disk.
            with open(self._upload_filepath + "/waypoint_snapshots/{}".format(waypoint.snapshot_id),
                      "rb") as snapshot_file:
                waypoint_snapshot = map_pb2.WaypointSnapshot()
                waypoint_snapshot.ParseFromString(snapshot_file.read())
                self._current_waypoint_snapshots[waypoint_snapshot.id] = waypoint_snapshot
        for edge in self._current_graph.edges:
            if len(edge.snapshot_id) == 0:
                continue
            # Load the edge snapshots from disk.
            with open(self._upload_filepath + "/edge_snapshots/{}".format(edge.snapshot_id),
                      "rb") as snapshot_file:
                edge_snapshot = map_pb2.EdgeSnapshot()
                edge_snapshot.ParseFromString(snapshot_file.read())
                self._current_edge_snapshots[edge_snapshot.id] = edge_snapshot
        # Upload the graph to the robot.
        print("Uploading the graph and snapshots to the robot...")
        true_if_empty = not len(self._current_graph.anchoring.anchors)
        response = self._graph_nav_client.upload_graph(lease=self._lease.lease_proto,
                                                       graph=self._current_graph,
                                                       generate_new_anchoring=true_if_empty)
        # Upload the snapshots to the robot.
        for snapshot_id in response.unknown_waypoint_snapshot_ids:
            waypoint_snapshot = self._current_waypoint_snapshots[snapshot_id]
            self._graph_nav_client.upload_waypoint_snapshot(waypoint_snapshot)
            print("Uploaded {}".format(waypoint_snapshot.id))
        for snapshot_id in response.unknown_edge_snapshot_ids:
            edge_snapshot = self._current_edge_snapshots[snapshot_id]
            self._graph_nav_client.upload_edge_snapshot(edge_snapshot)
            print("Uploaded {}".format(edge_snapshot.id))

        # The upload is complete! Check that the robot is localized to the graph,
        # and if it is not, prompt the user to localize the robot before attempting
        # any navigation commands.
        localization_state = self._graph_nav_client.get_localization_state()
        if not localization_state.localization.waypoint_id:
            # The robot is not localized to the newly uploaded graph.
            print("\n")
            print("Upload complete! The robot is currently not localized to the map; please localize")

    def navigate_to(self, destination_waypoint_id, tform_body_goal=None):
        """Navigate to a specific waypoint."""

        # Stop the lease keep-alive and create a new sublease for graph nav.
        self._lease = self._lease_wallet.advance()
        sublease = self._lease.create_sublease()
        self._lease_keepalive.shutdown()
        nav_to_cmd_id = None
        is_finished = False
        while not is_finished:
            try:
                nav_to_cmd_id = self._graph_nav_client.navigate_to(destination_waypoint_id, 1.0,
                                                                   leases=[sublease.lease_proto],
                                                                   command_id=nav_to_cmd_id,
                                                                   destination_waypoint_tform_body_goal=tform_body_goal)
            except ResponseError as e:
                print("Error while navigating {}".format(e))
                break
            time.sleep(0.5)
            is_finished = self._check_success(nav_to_cmd_id)

        self._lease = self._lease_wallet.advance()
        self._lease_keepalive = LeaseKeepAlive(self._lease_client)

    def _check_success(self, command_id=-1):
        """Use a navigation command id to get feedback from the robot and sit when command succeeds."""
        if command_id == -1:
            # No command, so we have no status to check.
            return False
        status = self._graph_nav_client.navigation_feedback(command_id)
        if status.status == graph_nav_pb2.NavigationFeedbackResponse.STATUS_REACHED_GOAL:
            # Successfully completed the navigation commands!
            return True
        elif status.status == graph_nav_pb2.NavigationFeedbackResponse.STATUS_LOST:
            print("Robot got lost when navigating the route, the robot will now sit down.")
            return True
        elif status.status == graph_nav_pb2.NavigationFeedbackResponse.STATUS_STUCK:
            print("Robot got stuck when navigating the route, the robot will now sit down.")
            return True
        elif status.status == graph_nav_pb2.NavigationFeedbackResponse.STATUS_ROBOT_IMPAIRED:
            print("Robot is impaired.")
            return True
        else:
            # Navigation command is not complete yet.
            return False

def pretty_print_waypoints(waypoint_id, waypoint_name, localization_id):
    print("%s Waypoint name: %s id: %s" %('->' if localization_id == waypoint_id else '  ', waypoint_name, waypoint_id))


def update_waypoints_and_edges(graph, localization_id, do_print=True):
    """Update and print waypoint ids and edge ids."""
    name_to_id = dict()
    edges = dict()

    short_code_to_count = {}
    waypoint_to_timestamp = []
    for waypoint in graph.waypoints:
        # Determine the timestamp that this waypoint was created at.
        timestamp = -1.0
        try:
            timestamp = waypoint.annotations.creation_time.seconds + waypoint.annotations.creation_time.nanos / 1e9
        except:
            # Must be operating on an older graph nav map, since the creation_time is not
            # available within the waypoint annotations message.
            pass
        waypoint_to_timestamp.append((waypoint.id, timestamp, waypoint.annotations.name))

        # Add the annotation name/id into the current dictionary.
        waypoint_name = waypoint.annotations.name
        if waypoint_name:
            if waypoint_name in name_to_id:
                # Waypoint name is used for multiple different waypoints, so set the waypoint id
                # in this dictionary to None to avoid confusion between two different waypoints.
                name_to_id[waypoint_name] = None
            else:
                # First time we have seen this waypoint annotation name. Add it into the dictionary
                # with the respective waypoint unique id.
                name_to_id[waypoint_name] = waypoint.id

    # Sort the set of waypoints by their creation timestamp. If the creation timestamp is unavailable,
    # fallback to sorting by annotation name.
    waypoint_to_timestamp = sorted(waypoint_to_timestamp, key=lambda x: (x[1], x[2]))

    # Print out the waypoints name, id, and short code in an ordered sorted by the timestamp from
    # when the waypoint was created.
    if do_print:
        print('%d waypoints:' % len(graph.waypoints))
        for waypoint in waypoint_to_timestamp:
            pretty_print_waypoints(waypoint[0], waypoint[2], localization_id)

    for edge in graph.edges:
        if edge.id.to_waypoint in edges:
            if edge.id.from_waypoint not in edges[edge.id.to_waypoint]:
                edges[edge.id.to_waypoint].append(edge.id.from_waypoint)
        else:
            edges[edge.id.to_waypoint] = [edge.id.from_waypoint]
        if do_print:
            print("(Edge) from waypoint {} to waypoint {} (cost {})".format(
                edge.id.from_waypoint, edge.id.to_waypoint, edge.annotations.cost.value))

    return name_to_id, edges

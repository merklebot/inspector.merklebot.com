import time
from bosdyn.client.math_helpers import SE2Pose
# from bosdyn.api import SE2Pose
from spot_movement_controller import SpotMovementController

username = ""
password = ""
robot_ip = "192.168.50.3"
map_filepath = "/home/spot/office_maps/downloaded_graph"

dest_offset = SE2Pose(1, 0, -3.1415).to_proto()

with SpotMovementController(username, password, robot_ip, map_filepath) as ctrl:
    ctrl.print_graph_waypoint_and_edge_ids()
    ctrl.set_initial_localization_fiducial()
    ctrl.stand_at_height(body_height=0.15)
    time.sleep(10)
    ctrl.navigate_to("crass-jackal-Yc.gC6.bErDa654FhQeNZQ==")
    time.sleep(2)
    ctrl.navigate_to("dapper-donkey-G8MYulVGhykiqsbOGgyoUA==", tform_body_goal=dest_offset)


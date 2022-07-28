import bosdyn.client
import bosdyn.client.util
from bosdyn.client.image import ImageClient, build_image_request
from bosdyn.client.robot_state import RobotStateClient
from bosdyn.api import image_pb2
import cv2
import numpy as np
from scipy import ndimage
from google.protobuf.json_format import MessageToDict
import time
import base64

from spot.merklebot_inspector.settings import Settings
from spot.merklebot_inspector.spot import SpotState

sdk = bosdyn.client.create_standard_sdk('image_capture')

ROTATION_ANGLE = {
    'back_fisheye_image': 0,
    'frontleft_fisheye_image': -78,
    'frontright_fisheye_image': -102,
    'left_fisheye_image': 0,
    'right_fisheye_image': 180
}

# IMAGE_SOURCES = ["frontleft_fisheye_image", "frontright_fisheye_image", "right_fisheye_image", "back_fisheye_image",
#                  "left_fisheye_image"]
IMAGE_SOURCES = ["left_fisheye_image", "right_fisheye_image"]


class SpotDataCollector:
    def __init__(self, robot_ip, username, password):
        sdk = bosdyn.client.create_standard_sdk('image_capture')
        robot = sdk.create_robot(robot_ip)
        robot.authenticate(username, password)
        robot.sync_with_directory()
        robot.time_sync.wait_for_sync(timeout_sec=30.0)

        self.image_client = robot.ensure_client(ImageClient.default_service_name)
        self.robot_state_client = robot.ensure_client(RobotStateClient.default_service_name)

        pixel_format = image_pb2.Image.PixelFormat.PIXEL_FORMAT_GREYSCALE_U8
        self.image_request = [
            build_image_request(source, pixel_format=pixel_format)
            for source in IMAGE_SOURCES
        ]

    def get_image_sources(self):
        image_sources = self.image_client.list_image_sources()
        return image_sources

    def get_num_bytes_by_image(self, image):
        num_bytes = 1
        if image.shot.image.pixel_format == image_pb2.Image.PIXEL_FORMAT_RGB_U8:
            num_bytes = 3
        elif image.shot.image.pixel_format == image_pb2.Image.PIXEL_FORMAT_RGBA_U8:
            num_bytes = 4
        elif image.shot.image.pixel_format == image_pb2.Image.PIXEL_FORMAT_GREYSCALE_U8:
            num_bytes = 1
        elif image.shot.image.pixel_format == image_pb2.Image.PIXEL_FORMAT_GREYSCALE_U16:
            num_bytes = 2
        return num_bytes

    def get_images(self):
        image_responses = self.image_client.get_image(self.image_request)
        return image_responses

    def get_images_base64(self):
        camera_images = self.get_images()
        for image in camera_images:
            dtype = np.uint8
            extension = ".jpg"
            img = np.frombuffer(image.shot.image.data, dtype=dtype)
            img = cv2.imdecode(img, -1)
            img = ndimage.rotate(img, ROTATION_ANGLE[image.source.name])
            retval, buffer = cv2.imencode('.jpg', image)
            camera_images[image.source.name] = base64.b64encode(buffer)
        return camera_images

    def get_state(self):
        return self.robot_state_client.get_robot_state()

    def get_battery_state(self):
        return MessageToDict(self.get_state().battery_states[0])


def run_spot_data_collector(settings: Settings,
                            spot_state: SpotState):
    spot_data_collector = SpotDataCollector(settings.SPOT_IP, settings.BOSDYN_CLIENT_USERNAME,
                                            settings.BOSDYN_CLIENT_PASSWORD)
    while True:
        camera_images = spot_data_collector.get_images_base64()
        battery = spot_data_collector.get_battery_state()['chargePercentage']
        spot_state['camera_images'] = camera_images
        spot_state['battery'] = battery

        time.sleep(1 / 10)

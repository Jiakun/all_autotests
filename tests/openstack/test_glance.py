"""Test suites for Glance resource managers"""
from glanceclient.v2 import Client as GlanceClient

from unittest2 import TestCase

from sedna.openstack.glance import IMAGE_PATH, ImageManager
from sedna.openstack.common import Image

from tests.openstack.base import ResourceManagerTest


class ImageManagerTest(TestCase, ResourceManagerTest):
    """Test suite for VolumeManager"""

    def setUp(self):
        self.set_up(GlanceClient, ImageManager, Image)
        self.resource_manager.upload_image(
            self.created_resource, IMAGE_PATH)

    def build_resource(self):
        resource_name = self.rand_name("ImageManagerTest", prefix="sedna")
        return Image(name=resource_name, disk_format="qcow2",
                     container_format="bare", visibility="private")

    def tearDown(self):
        self.tear_down()

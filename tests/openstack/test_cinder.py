"""Test suites for Cinder resource managers"""
from cinderclient.v2.client import Client as CinderClient

from unittest2 import TestCase

from sedna.openstack.common import Snapshot, Volume
from sedna.openstack.cinder import SnapshotManager, VolumeManager

from tests.openstack.base import ResourceManagerTest


class VolumeManagerTest(TestCase, ResourceManagerTest):
    """Test suite for VolumeManager"""

    def __init__(self, methodName='runTest'):
        super(VolumeManagerTest, self).__init__(methodName)

    def setUp(self):
        self.set_up(CinderClient, VolumeManager, Volume)

    def tearDown(self):
        self.tear_down()

    def build_resource(self):
        resource_name = self.rand_name("VolumeManagerTest", prefix="sedna")
        size = 3
        return Volume(name=resource_name, size=size)


class SnapshotManagerTest(TestCase, ResourceManagerTest):
    """Test suite for VolumeManager"""

    def __init__(self, methodName="runTest"):
        super(SnapshotManagerTest, self).__init__(methodName=methodName)
        self.volume_manager = None

    def setUp(self):
        self.set_up(CinderClient, SnapshotManager, Snapshot)

    def tearDown(self):
        volume = self.created_resource.volume
        self.tear_down()
        self.sync_delete(self.volume_manager, volume)

    def build_resource(self):
        self.volume_manager = self.volume_manager if self.volume_manager\
            else VolumeManager(self.openstack_client)
        resource_name = self.rand_name("SnapshotManagerTest", prefix="sedna")
        size = 3
        volume = self.volume_manager.create(
            Volume(name=resource_name, size=size))
        return Snapshot(name=resource_name, volume=volume)

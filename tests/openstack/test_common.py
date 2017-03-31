""" test suite for openstack common value objects """
from unittest2 import TestCase

from sedna.openstack.common import\
    Domain, Image, Network, Port, Project, Resource, Snapshot, Subnet, User,\
    Volume, Server, Flavor


class ResourceTest(TestCase):
    """Base test case for resource value object"""

    def __init__(self, method_name='runTest'):
        super(ResourceTest, self).__init__(method_name)
        self.resource_constructor = Resource

    def testEqual(self):
        """Test case for equaling or non_equal logic"""
        user1 = self.resource_constructor("test_id1", "abc")
        user2 = self.resource_constructor("test_id1", "abc")
        user3 = self.resource_constructor("test_id2", "abc")
        self.assertEqual(user1, user2)
        self.assertTrue(user1 == user2)
        self.assertFalse(user1 != user2)
        self.assertNotEqual(user1, user3)
        self.assertTrue(user1 != user3)
        self.assertFalse(user1 == user3)


class UserTest(ResourceTest):
    """Test case for User value object"""

    def __init__(self, method_name='runTest'):
        super(UserTest, self).__init__(method_name=method_name)
        self.resource_constructor = User


class ProjectTest(ResourceTest):
    """Test case for Project value object"""

    def __init__(self, method_name="runTest"):
        super(ProjectTest, self).__init__(method_name=method_name)
        self.resource_constructor = Project


class DomainTest(ResourceTest):
    """Test case for Domain value object"""

    def __init__(self, method_name='runTest'):
        super(DomainTest, self).__init__(method_name=method_name)
        self.resource_constructor = Domain


class VolumeTest(ResourceTest):
    """Test case for Volume value object"""

    def __init__(self, method_name='runTest'):
        super(VolumeTest, self).__init__(method_name=method_name)
        self.resource_constructor = Volume


class SnapshotTest(ResourceTest):
    """Test case for snapshot value object"""
    def __init__(self, method_name="runTest"):
        super(SnapshotTest, self).__init__(method_name=method_name)
        self.resource_constructor = Snapshot


class NetworkTest(ResourceTest):
    """Test case for network value object"""

    def __init__(self, method_name="runTest"):
        super(NetworkTest, self).__init__(method_name=method_name)
        self.resource_constructor = Network


class SubnetTest(ResourceTest):
    """Test case for subnet value object"""

    def __init__(self, method_name="runTest"):
        super(SubnetTest, self).__init__(method_name=method_name)
        self.resource_constructor = Subnet


class PortTest(ResourceTest):
    """Test case for port value object"""

    def __init__(self, method_name="runTest"):
        super(PortTest, self).__init__(method_name=method_name)
        self.resource_constructor = Port


class ImageTest(ResourceTest):

    def __init__(self, method_name="runTest"):
        super(ImageTest, self).__init__(method_name=method_name)
        self.resource_constructor = Image


class FlavorTest(ResourceTest):

    def __init__(self, method_name="runTest"):
        super(FlavorTest, self).__init__(method_name=method_name)
        self.resource_constructor = Flavor


class ServerTest(ResourceTest):

    def __init__(self, method_name="runTest"):
        super(ServerTest, self).__init__(method_name=method_name)
        self.resource_constructor = Server

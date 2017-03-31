from unittest2 import TestCase
#from novaclient.v2.client import Client as NovaClient
from novaclient.client import Client as NovaClient

from glanceclient.v2 import Client as GlanceClient
from neutronclient.v2_0.client import Client as NeutronClient
from cinderclient.v2.client import Client as CinderClient

from sedna.openstack.common import Server, Flavor, Image, \
    Subnet, Network, Volume, Keypair
from sedna.openstack.nova import ServerManager, FlavorManager, KeypairManager
from tests.openstack.base import ResourceManagerTest
from sedna.openstack.glance import ImageManager, IMAGE_PATH
from sedna.openstack.neutron import NetworkManager
from sedna.openstack.neutron import SubnetManager
from sedna.openstack.cinder import VolumeManager

from sedna.openstack.util import SyncStateChecker


class ServerManagerTest(TestCase, ResourceManagerTest):
    """Test suite for ServerManager"""

    def __init__(self, method_name="runTest"):
        super(ServerManagerTest, self).__init__(methodName=method_name)
        self.nova_client = None
        self.glance_client = None
        self.neutron_client = None

        self.image_manager = None
        self.flavor_manager = None
        self.network_manager = None
        self.subnet_manager = None

        self.net_sample = None

        self.status_checker = SyncStateChecker()

    def setUp(self):
        """
        Setup revelent clients and target resource to for the test cases to use
        """
        self.openstack_client = self._init_openstack_client("NovaClient")
        self.glance_client = self._init_openstack_client(GlanceClient)
        self.neutron_client = self._init_openstack_client(NeutronClient)
        self.resource_class = Server

        self.resource_manager = ServerManager(self.openstack_client,
                                              self.glance_client,
                                              self.neutron_client)

        self.expected_resource = self.build_resource()
        self.expected_resource_name = self.expected_resource.name

        self.created_resource =\
            self.resource_manager.create(self.expected_resource)

    def test_server_and_attach_detach_volume(self):
        cinder_client = self._init_openstack_client(CinderClient)

        volume_manager = VolumeManager(cinder_client=cinder_client)
        volume_name = self.rand_name("VolumeManagerTest_volume", "sedna")
        volume = Volume(name=volume_name, size=3)
        volume_created = volume_manager.create(volume)
        self.resource_manager.create_server_volume(
            server=self.created_resource,
            volume=volume_created, cinder_client=cinder_client)
        attached_volume = cinder_client.volumes.get(volume_created.id)
        self.assertEqual(attached_volume.__dict__["status"], "in-use")
        self.resource_manager.delete_server_volume(
            server=self.created_resource,
            volume=volume_created, cinder_client=cinder_client)
        detached_volume = cinder_client.volumes.get(volume_created.id)
        self.assertEqual(detached_volume.__dict__["status"], "available")

    def test_stop_and_start(self):
        vm_state = self.resource_manager.get(self.created_resource).status
        self.assertEqual(vm_state, "ACTIVE")

        self.resource_manager.stop(self.created_resource)

        self.resource_manager.start(self.created_resource)

    def test_restart(self):
        vm_state = self.resource_manager.get(self.created_resource).status
        if vm_state == "SHUTOFF":
            self.resource_manager.start(self.created_resource)

        self.resource_manager.reboot(self.created_resource)

    def tearDown(self):
        image = self.created_resource.image
        flavor = self.created_resource.flavor
        # TODO(sy):
        # self.sync_delete(self.flavor_manager, flavor) cannot effective
        self.openstack_client.flavors.delete(flavor)
        self.sync_delete(self.image_manager, image)

        self.tear_down()
        self.sync_delete(self.subnet_manager, self.net_sample["subnet"])
        self.sync_delete(self.network_manager, self.net_sample["network"])

    def build_resource(self):
        self.flavor_manager = self.flavor_manager \
            if self.flavor_manager else FlavorManager(self.openstack_client)
        self.image_manager = self.image_manager \
            if self.image_manager else ImageManager(self.glance_client)
        self.network_manager = self.network_manager \
            if self.network_manager else NetworkManager(self.neutron_client)
        self.subnet_manager = self.subnet_manager \
            if self.subnet_manager else SubnetManager(self.neutron_client)

        image_name = self.rand_name("ImageManagerTest", prefix="sedna")
        flavor_name = self.rand_name("FlavorManagerTest", prefix="sedna")
        network_name = self.rand_name("NetworkManagerTest", prefix="sedna")
        subnet_name = self.rand_name("SubnetManagerTest", prefix="sedna")
        server_name = self.rand_name("ServerManaferTest", prefix="sedna")

        image = self.image_manager.create(Image(name=image_name,
                                                disk_format="qcow2",
                                                container_format="bare",
                                                visibility="private"))
        self.image_manager.upload_image(image, IMAGE_PATH)
        flavor = self.flavor_manager.create(Flavor(name=flavor_name,
                                                   ram=1024, disk=1, vcpus=1))
        network = self.network_manager.create(Network(name=network_name))

        subnet = self.subnet_manager.create(Subnet(name=subnet_name,
                                                   cidr="192.168.2.0/24",
                                                   network=network))
        self.net_sample = {"network": network, "subnet": subnet}
        nics_dict = {}
        nics = [nics_dict]
        nics_dict['net-id'] = network.id
        return Server(name=server_name, image=image, flavor=flavor, nics=nics)


class FlavorManagerTest(TestCase, ResourceManagerTest):
    """Test suite for FlavorManager"""

    def __init__(self, method_name="runTest"):
        super(FlavorManagerTest, self).__init__(methodName=method_name)

    def setUp(self):
        self.set_up(openstack_client_class="NovaClient",
                    manager_class=FlavorManager, resource_class=Flavor)

    def tearDown(self):
        self.resource_manager.delete(self.created_resource)

    def build_resource(self):
        resource_name = self.rand_name("FlavorManagerTest", prefix="sedna")
        return self.resource_class(
            name=resource_name, ram=1024, disk=1, vcpus=1)


class KeypairManagerTest(TestCase, ResourceManagerTest):
    """Test suite for KeypairManager"""

    def __init__(self, method_name="runTest"):
        super(KeypairManagerTest, self).__init__(methodName=method_name)

    def setUp(self):
        self.set_up(openstack_client_class="NovaClient",
                    manager_class=KeypairManager, resource_class=Keypair)

    def tearDown(self):
        self.resource_manager.delete(self.created_resource)

    def build_resource(self):
        resource_name = self.rand_name("KeypairManagerTest", prefix="sedna")
        return self.resource_class(name=resource_name)

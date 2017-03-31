import logging

from keystoneauth1.identity.v3 import Password
from keystoneauth1.session import Session

from novaclient.v2.client import Client as NovaClient
from glanceclient.v2 import Client as GlanceClient
from cinderclient.v2.client import Client as CinderClient
from neutronclient.v2_0.client import Client as NeutronClient
from keystoneclient.v3.client import Client as KeystoneClient
from sedna.openstack.client import SednaClient

from sedna.error import NoneReferenceError

from sedna.openstack.nova import ServerManager, FlavorManager, \
    KeypairManager
from tests.openstack.base import ResourceManagerTest
from sedna.openstack.glance import ImageManager, IMAGE_PATH
from sedna.openstack.neutron import NetworkManager, SubnetManager, \
    PortManager, RouterManager, FloatingipManager, LoadBalancerManager, \
    LBaaSPoolManager, ListenerManager, LBaaSHealthMonitorManager, \
    LBaaSMemberManager, SecurityGroupManager, FirewallRuleManager, \
    FirewallPolicyManager, FirewallManager, PortforwardingManager
from sedna.openstack.cinder import VolumeManager
from sedna.openstack.cinder import SnapshotManager
from sedna.openstack.keystone import UserManager
from sedna.openstack.keystone import ProjectManager
from sedna.openstack.keystone import DomainManager

import random
from time import sleep

from sedna.openstack.common import Server, Flavor, Image, Subnet,\
    Network, Port, Router, Floatingip, Volume, Snapshot, User, \
    Project, Domain, Keypair, SecurityGroup, Listener, LoadBalancer, \
    LBaaSHealthMonitor, LBaaSMember, LBaaSPool, FirewallRule, \
    FirewallPolicy, Firewall, Portforwarding


from unittest2 import TestCase
from sedna.openstack.cleaner import TargetResourcesCleaner, ListenerCleaner, \
    LBaaSHealthMonitorCleaner, LBaaSMemberCleaner, PortCleaner, \
    ServerCleaner, ImageCleaner, LBaaSPoolCleaner, SubnetCleaner, \
    LoadBalancerCleaner, RouterCleaner, FloatingipCleaner,\
    NetworkCleaner, KeypairCleaner, FlavorCleaner, SnapshotCleaner, \
    VolumeCleaner, SecurityGroupCleaner, FirewallRuleCleaner, \
    FirewallPolicyCleaner, FirewallCleaner, PortforwardingCleaner

EXTERNAL_NETWORK_ID = "0290502e-591c-49fb-8f20-64d2b7e3cca8"
prefix_name = ["sedna"]

logging.basicConfig()


class TargetResourcesCleanerTest(object):
    def __init__(self):
        self.cleaner = None
        self.manager = None
        self.created_resource = None
        self.neutron_client = None
        self.nova_client = None
        self.glance_client = None
        self.cinder_client = None

    def set_up(self, manager, resource, cleaner):
        self.manager = manager
        self.created_resource = self.manager.create(resource)
        self.cleaner = cleaner

    def test_cleanup(self):
        self.cleaner.delete_resources_with_prefix_name()
        sleep(1)
        resource_list = self.cleaner.get_resource_list_with_prefix_name()
        if self.created_resource is not None:
            for resource in resource_list:
                if self.created_resource.name == resource.name:
                    raise Exception(self.created_resource.name + "cannot be deleted.")
        else:
            raise Exception("Cannot create resource.")

        if resource_list is not None and len(resource_list) > 0:
            logging.info("%s", str(resource_list))
        else:
            pass
            # raise Exception(str(result_list))

    def tear_down(self):
        pass

    def _init_openstack_client(self, openstack_client_class):
        auth_url = "http://lb.63.qa.polex.in:35357/"
        admin_username = "admin"
        admin_password = "cb158f63cb2a0a81c798d214"
        admin_project_id = "e910148a98ff473b98ff563c510b3f22"
        admin_domain_id = "default"
        # region = "RegionOne"

        auth = Password(auth_url=auth_url + "v3",
                        username=admin_username,
                        password=admin_password,
                        project_id=admin_project_id,
                        user_domain_id=admin_domain_id
                        )

        os_session = Session(auth=auth)
        return openstack_client_class(session=os_session)

    def rand_name(self, name='', prefix=None):
        """Generate a random name that includes a random number

        :param str name: The name that you want to include
        :param str prefix: The prefix that you want to include
        :return: a random name. The format is
                 '<prefix>-<name>-<random number>'.
                 (e.g. 'prefixfoo-namebar-154876201')
        :rtype: string
        """
        randbits = str(random.randint(1, 0x7fffffff))
        rand_name = randbits
        if name:
            rand_name = name + '-' + rand_name
        if prefix:
            rand_name = prefix + '-' + rand_name
        return rand_name


"""
glance
"""


class ImageCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(ImageCleanerTest, self).__init__(method_name)
        self.glance_client = self._init_openstack_client(GlanceClient)
        self.nova_client = self._init_openstack_client(NovaClient)

    def setUp(self):
        self.set_up(
            resource=self.build_resource(),
            manager=ImageManager(glance_client=self.glance_client),
            cleaner=ImageCleaner(prefix_name,
                                 glance_client=self.glance_client,
                                 nova_client=self.nova_client))

    def build_resource(self):
        resource_name = self.rand_name("ImageCleanerTest", prefix="sedna")
        return Image(name=resource_name, disk_format="qcow2",
                     container_format="bare", visibility="private")


"""
Cinder
"""


class VolumeCleanUpTest(TestCase, TargetResourcesCleanerTest):
    # deleting requires long time, not waiting for the final result
    def __init__(self, method_name="runTest"):
        super(VolumeCleanUpTest, self).__init__(method_name)
        self.cinder_client = self._init_openstack_client(CinderClient)

    def setUp(self):
        self.set_up(
            resource=self.build_resource(),
            manager=VolumeManager(cinder_client=self.cinder_client),
            cleaner=VolumeCleaner(prefix_name, self.cinder_client))

    def build_resource(self):
        resource_name = self.rand_name("VolumeCleanerTest", prefix="sedna")
        size = 3
        return Volume(name=resource_name, size=size)


class SnapshotCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(SnapshotCleanerTest, self).__init__(method_name)
        self.cinder_client = self._init_openstack_client(CinderClient)
        self.volume_manager = VolumeManager(self.cinder_client)
        self.volume = None

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=SnapshotManager(cinder_client=self.cinder_client),
                    cleaner=SnapshotCleaner(prefix_name, self.cinder_client))

    def build_resource(self):
        volume_name = self.rand_name("SnapshotCleanerTest_Volume", prefix="sedna")
        size = 3
        self.volume = self.volume_manager.create(
            Volume(name=volume_name, size=size))
        resource_name = self.rand_name("SnapshotCleanerTest_Snapshot", prefix="sedna")
        return Snapshot(name=resource_name, volume=self.volume)

    def tearDown(self):
        self.tear_down()
        self.volume_manager.delete(self.volume)


"""
Nova
"""


class ServerCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(ServerCleanerTest, self).__init__(method_name)
        self.nova_client = self._init_openstack_client(NovaClient)
        self.glance_client = self._init_openstack_client(GlanceClient)
        self.neutron_client = self._init_openstack_client(NeutronClient)
        self.flavor_manager = FlavorManager(self.nova_client)
        self.image_manager = ImageManager(self.glance_client)
        self.network_manager = NetworkManager(self.neutron_client)
        self.subnet_manager = SubnetManager(self.neutron_client)
        self.flavor = None
        self.image = None
        self.network = None
        self.subnet = None

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=ServerManager(
                        nova_client=self.nova_client,
                        glance_client=self.glance_client,
                        neutron_client=self.neutron_client),
                    cleaner=ServerCleaner(prefix_name,
                                          nova_client=self.nova_client,
                                          glance_client=self.glance_client,
                                          neutron_client=self.neutron_client))

    def build_resource(self):
        image_name = self.rand_name("ServerCleanerTest_Image", prefix="sedna")
        flavor_name = self.rand_name("ServerCleanerTest_Flavor", prefix="sedna")
        network_name = self.rand_name("ServerCleanerTest_Net", prefix="sedna")
        subnet_name = self.rand_name("ServerCleanerTest_Subnet", prefix="sedna")
        server_name = self.rand_name("ServerCleanerTest_Server", prefix="sedna")

        self.image = self.image_manager.create(
            Image(name=image_name, disk_format="qcow2",
                  container_format="bare", visibility="private"))
        self.image_manager.upload_image(self.image, IMAGE_PATH)
        self.flavor = self.flavor_manager.create(
            Flavor(name=flavor_name, ram=1024, disk=1, vcpus=1))
        self.network = self.network_manager.create(Network(name=network_name))

        self.subnet = self.subnet_manager.create(
            Subnet(name=subnet_name, cidr="192.168.2.0/24", network=self.network))
        self.net_sample = {"network": self.network, "subnet": self.subnet}
        nics_dict = {}
        nics = [nics_dict]
        nics_dict['net-id'] = self.network.id
        return Server(name=server_name, image=self.image, flavor=self.flavor, nics=nics)

    def tearDown(self):
        self.tear_down()
        self.flavor_manager.delete(self.flavor)
        self.image_manager.delete(self.image)
        self.subnet_manager.delete(self.subnet)
        self.network_manager.delete(self.network)


class FlavorCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(FlavorCleanerTest, self).__init__(method_name)
        self.nova_client = self._init_openstack_client(NovaClient)

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=FlavorManager(os_client=self.nova_client),
                    cleaner=FlavorCleaner(prefix_name, self.nova_client))

    def build_resource(self):
        resource_name = self.rand_name("FlavorCleanerTest", prefix="sedna")
        return Flavor(name=resource_name, ram=1024, disk=1, vcpus=1)


class KeypairCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(KeypairCleanerTest, self).__init__(method_name)
        self.nova_client = self._init_openstack_client(NovaClient)

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=KeypairManager(nova_client=self.nova_client),
                    cleaner=KeypairCleaner(prefix_name, self.nova_client))

    def build_resource(self):
        resource_name = self.rand_name("KeypairCleanerTest", prefix="sedna")
        return Keypair(name=resource_name)


"""
neutron
"""


class NetworkCleanerTest(TestCase, TargetResourcesCleanerTest):
    # subnet is tested in their cases
    def __init__(self, method_name="runTest"):
        super(NetworkCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=NetworkManager(os_client=self.neutron_client),
                    cleaner=NetworkCleaner(prefix_name, self.neutron_client))

    def build_resource(self):
        resource_name = self.rand_name("NetworkCleanerTest", prefix="sedna")
        return Network(name=resource_name)


class SubnetCleanerTest(TestCase, TargetResourcesCleanerTest):
    # floatingip, loadbalancer are port are tested in their cases
    def __init__(self, method_name="runTest"):
        super(SubnetCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)
        self.network_manager = NetworkManager(self.neutron_client)
        self.network = None

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=SubnetManager(os_client=self.neutron_client),
                    cleaner=SubnetCleaner(prefix_name, self.neutron_client))

    def build_resource(self):
        network_name = self.rand_name("SubnetCleanerTest_network", "sedna")
        self.network = self.network_manager.create(Network(name=network_name))

        resource_name = self.rand_name("SubnetCleanerTest_subnet", "sedna")
        expected_cidr = "192.167.167.0/24"
        return Subnet(name=resource_name, cidr=expected_cidr,
                      network=self.network)

    def tearDown(self):
        self.tear_down()
        self.network_manager.delete(self.network)


class SecurityGroupCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(SecurityGroupCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=SecurityGroupManager(os_client=self.neutron_client),
                    cleaner=SecurityGroupCleaner(
                        prefix_name=prefix_name, neutron_client=self.neutron_client))

    def build_resource(self):
        resource_name = self.rand_name("SecurityGroupCleanerTest", "sedna")
        return SecurityGroup(name=resource_name)


class PortCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(PortCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)
        self.network_manager = NetworkManager(self.neutron_client)
        self.subnet_manager = SubnetManager(self.neutron_client)
        self.network = None
        self.subnet = None

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=PortManager(os_client=self.neutron_client),
                    cleaner=PortCleaner(prefix_name, self.neutron_client))

    def build_resource(self):
        network_name = self.rand_name("PortCleanerTest_network", "sedna")
        self.network = self.network_manager.create(Network(name=network_name))
        subnet_name = self.rand_name("PortCleanerTest_subnet", "sedna")
        cidr = "192.167.167.0/24"
        self.subnet = self.subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=self.network))

        resource_name = self.rand_name("PortCleanerTest_port", "sedna")
        return Port(name=resource_name, subnet=self.subnet)

    def tearDown(self):
        self.tear_down()
        self.subnet_manager.delete(self.subnet)
        self.network_manager.delete(self.network)


class FloatingipCleanerTest(TestCase, TargetResourcesCleanerTest):
    # NO 'name' attribute. Delete by status
    def __init__(self, method_name="runTest"):
        super(FloatingipCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=FloatingipManager(os_client=self.neutron_client),
                    cleaner=FloatingipCleaner(prefix_name, self.neutron_client))

    @staticmethod
    def build_resource():
        return Floatingip(external_net=Network(id=EXTERNAL_NETWORK_ID))


class RouterCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(RouterCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=RouterManager(os_client=self.neutron_client),
                    cleaner=RouterCleaner(prefix_name, self.neutron_client))

    def build_resource(self):
        router_name = \
            self.rand_name("RouterCleanerTest", prefix="sedna")
        return Router(name=router_name, admin_state_up=True)


class ListenerCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(ListenerCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)
        self.network_manager = NetworkManager(self.neutron_client)
        self.subnet_manager = SubnetManager(self.neutron_client)
        self.loadbalancer_manager = LoadBalancerManager(self.neutron_client)
        self.network = None
        self.subnet = None
        self.loadbalancer = None

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=ListenerManager(os_client=self.neutron_client),
                    cleaner=ListenerCleaner(prefix_name, self.neutron_client))

    def build_resource(self):
        network_name = self.rand_name("ListenerCleanerTest_network", "sedna")
        self.network = self.network_manager.create(Network(name=network_name))

        subnet_name = self.rand_name("ListenerCleanerTest_subnet", "sedna")
        cidr = "192.167.165.0/24"
        self.subnet = self.subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=self.network))

        loadbalancer_name = self.rand_name(
            "ListenerCleanerTest_loadbalancer", "sedna")
        self.loadbalancer = self.loadbalancer_manager.create(
            LoadBalancer(name=loadbalancer_name, subnet=self.subnet))

        resource_name = self.rand_name("ListenerCleanerTest_listener", "sedna")
        protocol = "HTTP"
        protocol_port = "80"
        return Listener(name=resource_name, loadbalancer=self.loadbalancer,
                        protocol=protocol, protocol_port=protocol_port)

    def tearDown(self):
        self.tear_down()
        self.loadbalancer_manager.delete(self.loadbalancer)
        self.subnet_manager.delete(self.subnet)
        self.network_manager.delete(self.network)


class LBaaSHealthMonitorCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(LBaaSHealthMonitorCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)
        self.network_manager = NetworkManager(self.neutron_client)
        self.subnet_manager = SubnetManager(self.neutron_client)
        self.loadbalancer_manager = LoadBalancerManager(self.neutron_client)
        self.pool_manager = LBaaSPoolManager(self.neutron_client)
        self.network = None
        self.subnet = None
        self.loadbalancer = None
        self.pool = None

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=LBaaSHealthMonitorManager(
                        os_client=self.neutron_client),
                    cleaner=LBaaSHealthMonitorCleaner(
                        prefix_name, self.neutron_client))

    def build_resource(self):
        network_name = self.rand_name(
            "HealthMonitorCleanerTest_network", "sedna")
        self.network = self.network_manager.create(Network(name=network_name))

        subnet_name = \
            self.rand_name("HealthMonitorCleanerTest_subnet", "sedna")
        cidr = "192.167.165.0/24"
        self.subnet = self.subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=self.network))

        loadbalancer_name = self.rand_name(
            "HealthMonitorCleanerTest_loadbalancer", "sedna")
        self.loadbalancer = self.loadbalancer_manager.create(
            LoadBalancer(name=loadbalancer_name, subnet=self.subnet))

        pool_name = self.rand_name("HealthMonitorCleanerTest_pool", "sedna")
        protocol = "HTTP"
        lb_algorithm = "ROUND_ROBIN"
        self.pool = self.pool_manager.create(LBaaSPool(
            name=pool_name, loadbalancer=self.loadbalancer, protocol=protocol,
            lb_algorithm=lb_algorithm))

        resource_name = self.rand_name(
            "HealthMonitorCleanerTest_healthmonitor", "sedna")
        delay = "3"
        max_retries = "10"
        timeout = "100"
        monitor_type = "HTTP"
        return LBaaSHealthMonitor(name=resource_name, delay=delay,
                                  max_retries=max_retries, timeout=timeout,
                                  type=monitor_type, lbaas_pool=self.pool)

    def tearDown(self):
        self.tear_down()
        self.pool_manager.delete(self.pool)
        self.loadbalancer_manager.delete(self.loadbalancer)
        self.subnet_manager.delete(self.subnet)
        self.network_manager.delete(self.network)


class LBaaSMemberCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(LBaaSMemberCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)
        self.network_manager = NetworkManager(self.neutron_client)
        self.subnet_manager = SubnetManager(self.neutron_client)
        self.loadbalancer_manager = LoadBalancerManager(self.neutron_client)
        self.pool_manager = LBaaSPoolManager(self.neutron_client)
        self.network = None
        self.subnet = None
        self.loadbalancer = None
        self.network_for_subnet = None
        self.pool = None

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=LBaaSMemberManager(
                        os_client=self.neutron_client),
                    cleaner=LBaaSMemberCleaner(
                        prefix_name, self.neutron_client))
        self.cleaner.set(self.pool.id)

    def build_resource(self):
        network_name = self.rand_name(
            "LBaaSMemberCleanerTest_network", "sedna")
        self.network = self.network_manager.create(Network(name=network_name))
        subnet_name = \
            self.rand_name("LBaaSMemberCleanerTest_subnet", "sedna")
        cidr = "192.167.165.0/24"
        self.subnet = self.subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=self.network))

        loadbalancer_name = self.rand_name(
            "LBaaSMemberCleanerTest_loadbalancer", "sedna")
        self.loadbalancer = self.loadbalancer_manager.create(
            LoadBalancer(name=loadbalancer_name, subnet=self.subnet))

        pool_name = self.rand_name("LBaaSMemberCleanerTest_pool", "sedna")
        protocol = "HTTP"
        lb_algorithm = "ROUND_ROBIN"
        self.pool = self.pool_manager.create(LBaaSPool(
            name=pool_name, loadbalancer=self.loadbalancer,
            protocol=protocol, lb_algorithm=lb_algorithm))

        # create subnet
        network_name_for_subnet = self.rand_name(
            "LBaaSMemberCleanerTest_network", "sedna")
        self.network_for_subnet = self.network_manager.create(
            Network(name=network_name_for_subnet))

        subnet_name_for_subnet = \
            self.rand_name("LBaaSMemberCleanerTest_subnet", "sedna")
        cidr = "192.167.164.0/24"
        self.subnet_for_subnet = self.subnet_manager.create(
            Subnet(name=subnet_name_for_subnet, cidr=cidr,
                   network=self.network_for_subnet))

        resource_name = self.rand_name(
            "LBaaSMemberCleanerTest_member", "sedna")
        address = "10.0.61.1"
        protocol_port = "10"
        return LBaaSMember(name=resource_name, address=address,
                           protocol_port=protocol_port, lbaas_pool=self.pool,
                           subnet=self.subnet_for_subnet)

    def tearDown(self):
        self.tear_down()
        self.pool_manager.delete(self.pool)
        self.loadbalancer_manager.delete(self.loadbalancer)
        self.subnet_manager.delete(self.subnet)
        self.network_manager.delete(self.network)
        self.subnet_manager.delete(self.subnet_for_subnet)
        self.network_manager.delete(self.network_for_subnet)


class LBaaSPoolCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(LBaaSPoolCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)
        self.network_manager = NetworkManager(self.neutron_client)
        self.subnet_manager = SubnetManager(self.neutron_client)
        self.loadbalancer_manager = LoadBalancerManager(self.neutron_client)
        self.network = None
        self.subnet = None
        self.loadbalancer = None

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=LBaaSPoolManager(
                        os_client=self.neutron_client),
                    cleaner=LBaaSPoolCleaner(prefix_name, self.neutron_client))

    def build_resource(self):
        network_name = self.rand_name("LBaaSPoolCleanerTest_network", "sedna")
        self.network = self.network_manager.create(Network(name=network_name))
        subnet_name = \
            self.rand_name("LBaaSPoolCleanerTest_subnet", "sedna")
        cidr = "192.167.165.0/24"
        self.subnet = self.subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=self.network))
        loadbalancer_name = self.rand_name(
            "LBaaSPoolCleanerTest_loadbalancer", "sedna")
        self.loadbalancer = self.loadbalancer_manager.create(
            LoadBalancer(name=loadbalancer_name, subnet=self.subnet))

        resource_name = self.rand_name(
            "LBaaSPoolCleanerTest_pool", "sedna")
        protocol = "HTTP"
        lb_algorithm = "ROUND_ROBIN"
        return LBaaSPool(name=resource_name, loadbalancer=self.loadbalancer,
                         protocol=protocol, lb_algorithm=lb_algorithm)

    def test_cleanup(self):
        self.cleaner.get_resource_list_with_prefix_name()
        self.lbaas_healthmonitor_cleaner = \
            LBaaSHealthMonitorCleaner(prefix_name, self.neutron_client)
        self.lbaas_member_cleaner = LBaaSMemberCleaner(
            prefix_name, self.neutron_client)
        self.cleaner.set(
            lbaas_healthmonitor_cleaner=self.lbaas_healthmonitor_cleaner,
            lbaas_member_cleaner=self.lbaas_member_cleaner)
        self.cleaner.delete_resources_with_prefix_name()
        result_list = self.cleaner.get_resource_list_with_prefix_name()

        if len(result_list) > 0:
            logging.info("%s", str(result_list))

    def tearDown(self):
        self.tear_down()
        self.loadbalancer_manager.delete(self.loadbalancer)
        self.subnet_manager.delete(self.subnet)
        self.network_manager.delete(self.network)


class LoadBalancerCleanerTest(TestCase, TargetResourcesCleanerTest):
    # listener and pool is tested in their cases
    def __init__(self, method_name="runTest"):
        super(LoadBalancerCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)
        self.network_manager = NetworkManager(self.neutron_client)
        self.subnet_manager = SubnetManager(self.neutron_client)
        self.network = None
        self.subnet = None

    def setUp(self):
        self.set_up(resource=self.build_resource(),
                    manager=LoadBalancerManager(
                        os_client=self.neutron_client),
                    cleaner=LoadBalancerCleaner(
                        prefix_name, self.neutron_client))

    def build_resource(self):
        network_name = self.rand_name(
            "LoadbalancerCleanerTest_network", "sedna")
        self.network = self.network_manager.create(Network(name=network_name))
        subnet_name = \
            self.rand_name("LoadbalancerCleanerTest_subnet", "sedna")
        cidr = "192.167.165.0/24"
        self.subnet = self.subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=self.network))

        resource_name = self.rand_name(
            "LoadbalancerCleanerTest_loadbalancer", "sedna")
        return LoadBalancer(name=resource_name, subnet=self.subnet)

    def tearDown(self):
        self.tear_down()
        self.subnet_manager.delete(self.subnet)
        self.network_manager.delete(self.network)


class FirewallRuleCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(FirewallRuleCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(
            resource=self.build_resource(),
            manager=FirewallRuleManager(
                os_client=self.neutron_client),
            cleaner=FirewallRuleCleaner(prefix_name, self.neutron_client))

    def build_resource(self):
        resource_name = self.rand_name(
            "FirewallRuleCleanerTest_firewallrule", "sedna")
        protocol = "TCP"
        action = "allow"
        return FirewallRule(name=resource_name, protocol=protocol, action=action)

    def tearDown(self):
        self.tear_down()


class FirewallPolicyCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(FirewallPolicyCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)
        self.firewall_rule_manager = FirewallRuleManager(self.neutron_client)

    def setUp(self):
        self.set_up(
            resource=self.build_resource(),
            manager=FirewallPolicyManager(
                os_client=self.neutron_client),
            cleaner=FirewallPolicyCleaner(prefix_name, self.neutron_client))

    def build_resource(self):
        protocol = "TCP"
        action = "allow"
        firewall_rule_name = self.rand_name(
            "FirewallPolicyCleanerTest_firewallrule", "sedna")
        self.firewall_rule = self.firewall_rule_manager.create(
            FirewallRule(name=firewall_rule_name, protocol=protocol, action=action))
        resource_name = self.rand_name(
            "FirewallPolicyCleanerTest_firewallpolicy", "sedna")
        return FirewallPolicy(name=resource_name, firewall_rules=[self.firewall_rule])

    def tearDown(self):
        self.tear_down()
        self.firewall_rule_manager.delete(self.firewall_rule)


class FirewallCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(FirewallCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)
        self.firewall_policy_manager = FirewallPolicyManager(self.neutron_client)
        self.router_manager = RouterManager(self.neutron_client)

    def setUp(self):
        self.set_up(
            resource=self.build_resource(),
            manager=FirewallManager(
                os_client=self.neutron_client),
            cleaner=FirewallCleaner(prefix_name, self.neutron_client))

    def build_resource(self):
        firewall_policy_name = self.rand_name(
            "FirewallCleanerTest_firewallpolicy", "sedna")
        self.firewall_policy = self.firewall_policy_manager.create(
            FirewallPolicy(name=firewall_policy_name))
        router_name = self.rand_name(
            "FirewallCleanerTest_router", "sedna")
        self.router = self.router_manager.create(Router(name=router_name))
        resource_name = self.rand_name(
            "FirewallCleanerTest_firewall", "sedna")
        return Firewall(name=resource_name, firewall_policy_id=self.firewall_policy.id,
                        router_ids=[self.router.id])

    def tearDown(self):
        self.tear_down()
        self.firewall_policy_manager.delete(self.firewall_policy)
        self.router_manager.delete(self.router)


class PortforwardingCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(PortforwardingCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(SednaClient)
        self.router_manager = RouterManager(self.neutron_client)

    def setUp(self):
        self.set_up(
            resource=self.build_resource(),
            manager=PortforwardingManager(
                os_client=self.neutron_client),
            cleaner=PortforwardingCleaner(prefix_name, self.neutron_client))
        self.cleaner.set(self.router.id)

    def build_resource(self):
        destination_ip = "10.0.61.1"
        destination_port = "10011"
        source_port = "10011"
        protocol = "TCP"
        router_name = self.rand_name(
            "PortforwardingCleanerTest_router", "sedna")
        self.router = self.router_manager.create(Router(name=router_name))
        self.router_manager.add_gateway_router(router=self.router,
                                               network=Network(EXTERNAL_NETWORK_ID))
        resource_name = self.rand_name(
            "PortforwardingCleanerTest_portforwarding", "sedna")
        return Portforwarding(name=resource_name, router_id=self.router.id,
                              destination_port=destination_port,
                              destination_ip=destination_ip,
                              source_port=source_port, protocol=protocol)

    def tearDown(self):
        self.tear_down()
        self.router_manager.delete(self.router)

from unittest2 import TestCase
from neutronclient.v2_0.client import Client as NeutronClient
from novaclient.v2.client import Client as NovaClient
from glanceclient.v2 import Client as GlanceClient
from sedna.openstack.client import SednaClient

from sedna.openstack.common import Network, Port, Subnet, Floatingip, \
    Router, Flavor, Image, Server, LoadBalancer, LBaaSPool, Listener, \
    LBaaSHealthMonitor, LBaaSMember, SecurityGroup, FirewallRule, \
    FirewallPolicy, Firewall, Portforwarding, VpnIkepolicy, \
    VpnIpsecpolicy, VpnService, VpnEndpointGroup, VpnIpsecSiteConnection
from sedna.openstack.neutron import NetworkManager, PortManager,\
    SubnetManager, FloatingipManager, RouterManager, LoadBalancerManager, \
    LBaaSPoolManager, ListenerManager, LBaaSHealthMonitorManager, \
    LBaaSMemberManager, SecurityGroupManager, FirewallRuleManager, \
    FirewallPolicyManager, FirewallManager, PortforwardingManager, \
    VpnIkepolicyManager, VpnIpsecpolicyManager, VpnServiceManager, \
    VpnEndpointGroupManager, VpnIpsecSiteConnectionManager
from sedna.openstack.nova import ServerManager, FlavorManager
from sedna.openstack.glance import ImageManager, IMAGE_PATH
from tests.openstack.base import ResourceManagerTest

# EXTERNAL_NETWORK_ID = "0290502e-591c-49fb-8f20-64d2b7e3cca8"
EXTERNAL_NETWORK_ID = "5e3f8d37-5b44-4ca9-8499-322f74f6d5b4"


class NetworkManagerTest(TestCase, ResourceManagerTest):
    """Test suite for NetManager"""

    def __init__(self, method_name="runTest"):
        super(NetworkManagerTest, self).__init__(methodName=method_name)

    def setUp(self):
        self.set_up(NeutronClient, NetworkManager, Network)

    def tearDown(self):
        self.tear_down()


class SubnetManagerTest(TestCase, ResourceManagerTest):
    """Test suite for SubnetManager"""

    def __init__(self, method_name="runTest"):
        super(SubnetManagerTest, self).__init__(methodName=method_name)
        self.network_manager = None

    def setUp(self):
        self.set_up(NeutronClient, SubnetManager, Subnet)

    def tearDown(self):
        self.tear_down()
        self.network_manager.delete(self.created_resource.network)

    def build_resource(self):
        self.network_manager = self.network_manager if self.network_manager \
            else NetworkManager(self.openstack_client)
        network_name = self.rand_name("SubnetManagerTest_network", "sedna")
        network = self.network_manager.create(Network(name=network_name))

        expected_subnet_name = \
            self.rand_name("SubnetManagerTest_subnet", "sedna")
        expected_cidr = "192.167.167.0/24"
        return Subnet(name=expected_subnet_name, cidr=expected_cidr,
                      network=network)

    def test_list_subnets(self):
        self.resource_manager.list()


class SecurityGroupManagerTest(TestCase, ResourceManagerTest):
    """Test suite for SecurityGroupManager"""
    def __init__(self, method_name="runTest"):
        super(SecurityGroupManagerTest, self).__init__(methodName=method_name)

    def setUp(self):
        self.set_up(NeutronClient, SecurityGroupManager, SecurityGroup)

    def build_resource(self):
        resource_name = self.rand_name("SecurityGroupManagerTest", "sedna")
        return SecurityGroup(name=resource_name)


class PortManagerTest(TestCase, ResourceManagerTest):
    """Test suite for PortManager"""

    def __init__(self, method_name="runTest"):
        super(PortManagerTest, self).__init__(methodName=method_name)
        self.subnet_manager = None
        self.network_manager = None

    def setUp(self):
        self.set_up(NeutronClient, PortManager, Port)

    def tearDown(self):
        self.tear_down()
        network = self.created_resource.subnet.network
        self.subnet_manager.delete(self.created_resource.subnet)
        self.network_manager.delete(network)

    def build_resource(self):
        self.network_manager = self.network_manager if self.network_manager \
            else NetworkManager(self.openstack_client)
        self.subnet_manager = self.subnet_manager if self.subnet_manager \
            else SubnetManager(self.openstack_client)
        network_name = self.rand_name("PortManagerTest_network", "sedna")
        network = self.network_manager.create(Network(name=network_name))

        subnet_name = \
            self.rand_name("PortManagerTest_subnet", "sedna")
        cidr = "192.167.167.0/24"
        subnet = self.subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=network))

        expected_port_name = self.rand_name("PortManagerTest_port", "sedna")
        return Port(name=expected_port_name, subnet=subnet)


class FloatingipManagerTest(TestCase, ResourceManagerTest):
    """Test suite for FloatingipManager"""

    def __init__(self, method_name="runTest"):
        super(FloatingipManagerTest, self).__init__(methodName=method_name)

    def setUp(self):
        self.set_up(NeutronClient, FloatingipManager, Floatingip)

    def tearDown(self):
        self.tear_down()

    def build_resource(self):
        return Floatingip(external_net=Network(id=EXTERNAL_NETWORK_ID))

    def test_associate_and_disassociate_floatingip(self):
        nova_client = self._init_openstack_client(NovaClient)
        glance_client = self._init_openstack_client(GlanceClient)

        flavor_manager = FlavorManager(nova_client)
        image_manager = ImageManager(glance_client)
        router_manager = RouterManager(self.openstack_client)
        port_manager = PortManager(self.openstack_client)
        network_manager = NetworkManager(self.openstack_client)
        subnet_manager = SubnetManager(self.openstack_client)
        server_manager = ServerManager(nova_client=nova_client,
                                       glance_client=glance_client,
                                       neutron_client=self.openstack_client)

        router_name = \
            self.rand_name("FloatingipManagerTest_router", prefix="sedna")
        network_name = \
            self.rand_name("FloatingipManagerTest_network", prefix="sedna")
        subnet_name = \
            self.rand_name("FloatingipManagerTest_subnet", "sedna")
        cidr = "192.167.167.0/24"
        image_name = \
            self.rand_name("FloatingipManagerTest_image", prefix="sedna")
        flavor_name = \
            self.rand_name("FloatingipManagerTest_flavor", prefix="sedna")
        server_name = \
            self.rand_name("FloatingipManaferTest_server", prefix="sedna")

        router = router_manager.create(
            Router(name=router_name, admin_state_up=True))
        network = network_manager.create(Network(name=network_name))
        subnet = subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=network))
        image = image_manager.create(Image(name=image_name,
                                           disk_format="qcow2",
                                           container_format="bare",
                                           visibility="private"))
        image_manager.upload_image(image, IMAGE_PATH)
        flavor = flavor_manager.create(Flavor(name=flavor_name,
                                              ram=1024, disk=1, vcpus=1))

        self.net_sample = {"network": network, "subnet": subnet}
        nics_dict = {}
        nics = [nics_dict]
        nics_dict['net-id'] = network.id
        server = server_manager.create(Server(name=server_name, image=image,
                                              flavor=flavor, nics=nics))
        external_network = Network(id=EXTERNAL_NETWORK_ID)
        router_manager.add_gateway_router(router=router,
                                          network=external_network)
        router_manager.add_interface_router(router=router, subnet=subnet)

        port = port_manager.list(server)[0]
        expected_floatingip_json = \
            self.openstack_client.show_floatingip(self.created_resource.id)

        self.resource_manager.associate_floatingip(
            floatingip=self.created_resource, network=network, server=server)
        associated_floatingip_json =\
            self.openstack_client.show_floatingip(self.created_resource.id)
        self.assertEquals(port.id,
                          associated_floatingip_json["floatingip"]["port_id"])
        self.resource_manager.disassociate_floatingip(
            floatingip=self.created_resource)
        disassociated_floatingip_json = \
            self.openstack_client.show_floatingip(self.created_resource.id)
        self.assertEquals(expected_floatingip_json,
                          disassociated_floatingip_json)
        router_manager.remove_interface_router(router=router, subnet=subnet)
        router_manager.remove_gateway_router(router=router)
        server_manager.delete(server)
        router_manager.delete(router)
        subnet_manager.delete(subnet)
        network_manager.delete(network)


class RouterManagerTest(TestCase, ResourceManagerTest):
    """Test suite for FloatingipManager"""

    def __init__(self, method_name="runTest"):
        super(RouterManagerTest, self).__init__(methodName=method_name)

    def setUp(self):
        self.set_up(NeutronClient, RouterManager, Router)

    def tearDown(self):
        self.tear_down()

    def build_resource(self):
        router_name = \
            self.rand_name("RouterManagerTest_router", prefix="sedna")
        return Router(name=router_name, admin_state_up=True)

    def test_add_and_remove_gateway_router(self):
        external_network = Network(id=EXTERNAL_NETWORK_ID)
        expected_router_json = \
            self.openstack_client.show_router(
                self.created_resource.id)
        updated_router_json = \
            self.resource_manager.add_gateway_router(
                self.created_resource, external_network)
        self.assertEquals(
            external_network.id,
            updated_router_json["router"]
            ["external_gateway_info"]["network_id"])
        updated_router_json = \
            self.resource_manager.remove_gateway_router(self.created_resource)
        self.assertEquals(expected_router_json, updated_router_json)

    def test_add_and_remove_interface_router(self):
        expected_router_json = \
            self.openstack_client.show_router(self.created_resource.id)

        network_manager = NetworkManager(self.openstack_client)
        subnet_manager = SubnetManager(self.openstack_client)
        network_name = self.rand_name("RouterManagerTest_network", "sedna")
        network = network_manager.create(Network(name=network_name))
        subnet_name = \
            self.rand_name("RouterManagerTest_subnet", "sedna")
        cidr = "192.168.0.0/24"
        subnet = subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=network))

        updated_resource = \
            self.resource_manager.add_interface_router(
                self.created_resource, subnet)
        self.assertEquals(subnet.id, updated_resource["subnet_id"])
        self.resource_manager.remove_interface_router(
            self.created_resource, subnet)
        updated_router_json = \
            self.openstack_client.show_router(self.created_resource.id)
        self.assertEquals(expected_router_json, updated_router_json)
        subnet_manager.delete(subnet)
        network_manager.delete(network)


class LoadbalancerManagerTest(TestCase, ResourceManagerTest):
    """Test suite for LoadbalancerManager"""

    def __init__(self, method_name="runTest"):
        super(LoadbalancerManagerTest, self).__init__(methodName=method_name)
        self.subnet_manager = None
        self.network_manager = None

    def setUp(self):
        self.set_up(NeutronClient, LoadBalancerManager, LoadBalancer)

    def tearDown(self):
        self.tear_down()
        network = self.network

        self.subnet_manager.delete(self.created_resource.subnet)
        self.network_manager.delete(network)

    def build_resource(self):
        self.network_manager = self.network_manager if self.network_manager \
            else NetworkManager(self.openstack_client)
        self.subnet_manager = self.subnet_manager if self.subnet_manager \
            else SubnetManager(self.openstack_client)
        network_name = self.rand_name(
            "LoadbalancerManagerTest_network", "sedna")
        self.network = self.network_manager.create(Network(name=network_name))

        subnet_name = \
            self.rand_name("LoadbalancerManagerTest_subnet", "sedna")
        cidr = "192.167.165.0/24"
        subnet = self.subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=self.network))

        expected_loadbalancer_name = self.rand_name(
            "LoadbalancerManagerTest_loadbalancer", "sedna")
        return LoadBalancer(name=expected_loadbalancer_name, subnet=subnet)

    def test_list_loadbalancers(self):
        self.resource_manager.list()


class LBaaSPoolManagerTest(TestCase, ResourceManagerTest):
    """Test suite for LBaaSPoolManager"""

    def __init__(self, method_name="runTest"):
        super(LBaaSPoolManagerTest, self).__init__(methodName=method_name)
        self.loadbalancer_manager = None
        self.subnet_manager = None
        self.network_manager = None

    def setUp(self):
        self.set_up(NeutronClient, LBaaSPoolManager, LBaaSPool)

    def tearDown(self):
        self.tear_down()
        network = self.network
        subnet = self.subnet

        self.loadbalancer_manager.delete(self.created_resource.loadbalancer)
        self.subnet_manager.delete(subnet)
        self.network_manager.delete(network)

    def build_resource(self):
        self.network_manager = self.network_manager if self.network_manager \
            else NetworkManager(self.openstack_client)
        self.subnet_manager = self.subnet_manager if self.subnet_manager \
            else SubnetManager(self.openstack_client)
        self.loadbalancer_manager = self.loadbalancer_manager if \
            self.loadbalancer_manager \
            else LoadBalancerManager(self.openstack_client)
        network_name = self.rand_name("LBaaSPoolManagerTest_network", "sedna")
        self.network = self.network_manager.create(Network(name=network_name))

        subnet_name = \
            self.rand_name("LBaaSPoolManagerTest_subnet", "sedna")
        cidr = "192.167.165.0/24"
        self.subnet = self.subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=self.network))

        loadbalancer_name = self.rand_name(
            "LBaaSPoolManagerTest_loadbalancer", "sedna")
        loadbalancer = self.loadbalancer_manager.create(
            LoadBalancer(name=loadbalancer_name, subnet=self.subnet))

        expected_pool_name = self.rand_name(
            "LBaaSPoolManagerTest_pool", "sedna")
        protocol = "HTTP"
        lb_algorithm = "ROUND_ROBIN"
        return LBaaSPool(name=expected_pool_name, loadbalancer=loadbalancer,
                         protocol=protocol, lb_algorithm=lb_algorithm)

    def test_list_pools(self):
        self.resource_manager.list()


class ListenerManagerTest(TestCase, ResourceManagerTest):
    """Test suite for ListenerManager"""

    def __init__(self, method_name="runTest"):
        super(ListenerManagerTest, self).__init__(methodName=method_name)
        self.loadbalancer_manager = None
        self.subnet_manager = None
        self.network_manager = None

    def setUp(self):
        self.set_up(NeutronClient, ListenerManager, Listener)

    def tearDown(self):
        self.tear_down()
        network = self.network
        subnet = self.subnet

        self.loadbalancer_manager.delete(self.created_resource.loadbalancer)
        self.subnet_manager.delete(subnet)
        self.network_manager.delete(network)

    def build_resource(self):
        self.network_manager = self.network_manager if self.network_manager \
            else NetworkManager(self.openstack_client)
        self.subnet_manager = self.subnet_manager if self.subnet_manager \
            else SubnetManager(self.openstack_client)
        self.loadbalancer_manager = self.loadbalancer_manager if \
            self.loadbalancer_manager \
            else LoadBalancerManager(self.openstack_client)
        network_name = self.rand_name("ListenerManagerTest_network", "sedna")
        self.network = self.network_manager.create(Network(name=network_name))

        subnet_name = \
            self.rand_name("ListenerManagerTest_subnet", "sedna")
        cidr = "192.167.165.0/24"
        self.subnet = self.subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=self.network))

        loadbalancer_name = self.rand_name(
            "ListenerManagerTest_loadbalancer", "sedna")
        loadbalancer = self.loadbalancer_manager.create(
            LoadBalancer(name=loadbalancer_name, subnet=self.subnet))

        expected_listener_name = self.rand_name(
            "ListenerManagerTest_listener", "sedna")
        protocol = "HTTP"
        protocol_port = "80"
        return Listener(name=expected_listener_name, loadbalancer=loadbalancer,
                        protocol=protocol, protocol_port=protocol_port)

    def test_list_listeners(self):
        self.resource_manager.list()


class LBaaSHealthMonitorManagerTest(TestCase, ResourceManagerTest):
    """Test suite for HealthMonitorManager"""

    def __init__(self, method_name="runTest"):
        super(LBaaSHealthMonitorManagerTest, self).__init__(
            methodName=method_name)
        self.pool_manager = None
        self.loadbalancer_manager = None
        self.subnet_manager = None
        self.network_manager = None

    def setUp(self):
        self.set_up(NeutronClient, LBaaSHealthMonitorManager,
                    LBaaSHealthMonitor)

    def tearDown(self):
        self.tear_down()
        network = self.network
        subnet = self.subnet
        loadbalancer = self.loadbalancer

        self.pool_manager.delete(self.created_resource.pool)
        self.loadbalancer_manager.delete(loadbalancer)
        self.subnet_manager.delete(subnet)
        self.network_manager.delete(network)

    def build_resource(self):
        self.network_manager = self.network_manager if self.network_manager \
            else NetworkManager(self.openstack_client)
        self.subnet_manager = self.subnet_manager if self.subnet_manager \
            else SubnetManager(self.openstack_client)
        self.loadbalancer_manager = self.loadbalancer_manager if \
            self.loadbalancer_manager \
            else LoadBalancerManager(self.openstack_client)
        self.pool_manager = self.pool_manager if self.pool_manager \
            else LBaaSPoolManager(self.openstack_client)

        network_name = self.rand_name(
            "HealthMonitorManagerTest_network", "sedna")
        self.network = self.network_manager.create(Network(name=network_name))

        subnet_name = \
            self.rand_name("HealthMonitorManagerTest_subnet", "sedna")
        cidr = "192.167.165.0/24"
        self.subnet = self.subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=self.network))

        loadbalancer_name = self.rand_name(
            "HealthMonitorManagerTest_loadbalancer", "sedna")
        self.loadbalancer = self.loadbalancer_manager.create(
            LoadBalancer(name=loadbalancer_name, subnet=self.subnet))

        pool_name = self.rand_name("HealthMonitorManagerTest_pool", "sedna")
        protocol = "HTTP"
        lb_algorithm = "ROUND_ROBIN"
        pool = self.pool_manager.create(LBaaSPool(
            name=pool_name, loadbalancer=self.loadbalancer, protocol=protocol,
            lb_algorithm=lb_algorithm))

        expected_healthmonitor_name = self.rand_name(
            "HealthMonitorManagerTest_healthmonitor", "sedna")
        delay = "3"
        max_retries = "10"
        timeout = "100"
        type = "HTTP"
        return LBaaSHealthMonitor(name=expected_healthmonitor_name,
                                  delay=delay, max_retries=max_retries,
                                  timeout=timeout, type=type, lbaas_pool=pool)

    def test_list_healthmonitors(self):
        self.resource_manager.list()


class LBaaSMemberManagerTest(TestCase, ResourceManagerTest):
    """Test suite for LBaaSMemberManager"""

    def __init__(self, method_name="runTest"):
        super(LBaaSMemberManagerTest, self).__init__(methodName=method_name)
        self.pool_manager = None
        self.loadbalancer_manager = None
        self.subnet_manager = None
        self.network_manager = None

    def setUp(self):
        self.set_up(NeutronClient, LBaaSMemberManager, LBaaSMember)

    def tearDown(self):
        self.tear_down()
        network = self.network
        subnet = self.subnet
        loadbalancer = self.loadbalancer

        self.pool_manager.delete(self.created_resource.pool)
        self.loadbalancer_manager.delete(loadbalancer)
        self.subnet_manager.delete(subnet)
        self.network_manager.delete(network)

        self.subnet_manager.delete(self.created_resource.subnet)
        self.network_manager.delete(self.network_for_subnet)

    def build_resource(self):
        self.network_manager = self.network_manager if self.network_manager \
            else NetworkManager(self.openstack_client)
        self.subnet_manager = self.subnet_manager if self.subnet_manager \
            else SubnetManager(self.openstack_client)
        self.loadbalancer_manager = self.loadbalancer_manager if \
            self.loadbalancer_manager \
            else LoadBalancerManager(self.openstack_client)
        self.pool_manager = self.pool_manager if self.pool_manager \
            else LBaaSPoolManager(self.openstack_client)

        network_name = self.rand_name(
            "LBaaSMemberManagerTest_network", "sedna")
        self.network = self.network_manager.create(Network(name=network_name))

        subnet_name = \
            self.rand_name("LBaaSMemberManagerTest_subnet", "sedna")
        cidr = "192.167.165.0/24"
        self.subnet = self.subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=self.network))

        loadbalancer_name = self.rand_name(
            "LBaaSMemberManagerTest_loadbalancer", "sedna")
        self.loadbalancer = self.loadbalancer_manager.create(
            LoadBalancer(name=loadbalancer_name, subnet=self.subnet))

        pool_name = self.rand_name("LBaaSMemberManagerTest_pool", "sedna")
        protocol = "HTTP"
        lb_algorithm = "ROUND_ROBIN"
        pool = self.pool_manager.create(LBaaSPool(
            name=pool_name, loadbalancer=self.loadbalancer,
            protocol=protocol, lb_algorithm=lb_algorithm))

        # create subnet
        network_name_for_subnet = self.rand_name(
            "LBaaSMemberManagerTest_network", "sedna")
        self.network_for_subnet = self.network_manager.create(
            Network(name=network_name_for_subnet))

        subnet_name_for_subnet = \
            self.rand_name("LBaaSMemberManagerTest_subnet", "sedna")
        cidr = "192.167.164.0/24"
        subnet_for_subnet = self.subnet_manager.create(
            Subnet(name=subnet_name_for_subnet, cidr=cidr,
                   network=self.network_for_subnet))

        expected_member_name = self.rand_name(
            "LBaaSMemberManagerTest_member", "sedna")
        address = "10.0.61.1"
        protocol_port = "10"
        return LBaaSMember(name=expected_member_name, address=address,
                           protocol_port=protocol_port, lbaas_pool=pool,
                           subnet=subnet_for_subnet)

    def test_list_lbaas_members(self):
        self.resource_manager.list(self.created_resource.pool.id)


class FirewallRuleManagerTest(TestCase, ResourceManagerTest):
    """Test suite for FirewallRuleManager"""
    def __init__(self, method_name="runTest"):
        super(FirewallRuleManagerTest, self).__init__(methodName=method_name)

    def setUp(self):
        self.set_up(NeutronClient, FirewallRuleManager, FirewallRule)

    def build_resource(self):
        expected_firewall_rule_name = \
            self.rand_name("FirewallRuleTest_firewallrule", "sedna")
        expected_protocol = "TCP"
        expected_action = "allow"
        return FirewallRule(
            name=expected_firewall_rule_name, protocol=expected_protocol,
            action=expected_action)

    def tearDown(self):
        self.tear_down()


class FirewallPolicyManagerTest(TestCase, ResourceManagerTest):
    """Test suite for FirewallPolicyManager"""
    def __init__(self, method_name="runTest"):
        super(FirewallPolicyManagerTest, self).__init__(methodName=method_name)
        self.firewall_rule_manager = None

    def setUp(self):
        self.set_up(NeutronClient, FirewallPolicyManager, FirewallPolicy)

    def build_resource(self):
        self.firewall_rule_manager = self.firewall_rule_manager if self.firewall_rule_manager \
            else FirewallRuleManager(self.openstack_client)
        firewall_rule_name = self.rand_name("FirewallPolicyTest_firewallrule", "sedna")
        self.firewall_rule = self.firewall_rule_manager.create(
            FirewallRule(name=firewall_rule_name, protocol="TCP", action="allow"))

        expected_firewall_policy_name = \
            self.rand_name("FirewallPolicyTest_firewallpolicy", "sedna")
        return FirewallPolicy(name=expected_firewall_policy_name,
                              firewall_rules=[self.firewall_rule])

    def test_list(self):
        resource_list = self.resource_manager.list()
        print resource_list

    def tearDown(self):
        self.tear_down()
        self.firewall_rule_manager.delete(self.firewall_rule)


class FirewallManagerTest(TestCase, ResourceManagerTest):
    """Test suite for FirewallManager"""

    def __init__(self, method_name="runTest"):
        super(FirewallManagerTest, self).__init__(methodName=method_name)
        self.firewall_policy_manager = None
        self.router_manager = None

    def setUp(self):
        self.set_up(NeutronClient, FirewallManager, Firewall)

    def build_resource(self):
        self.firewall_policy_manager = self.firewall_policy_manager if self.firewall_policy_manager \
            else FirewallPolicyManager(self.openstack_client)
        firewall_policy_name = self.rand_name("FirewallTest_firewallpolicy", "sedna")
        self.firewall_policy = self.firewall_policy_manager.create(FirewallPolicy(name=firewall_policy_name))

        self.router_manager = self.router_manager if self.router_manager \
            else RouterManager(self.openstack_client)
        router_name = self.rand_name("FirewallTest_router", "sedna")
        self.router = self.router_manager.create(Router(name=router_name))
        expected_firewall_name = \
            self.rand_name("FirewallTest_firewall", "sedna")
        return Firewall(name=expected_firewall_name,
                        firewall_policy_id=self.firewall_policy,
                        router_ids=[self.router])

    def tearDown(self):
        self.tear_down()
        self.firewall_policy_manager.delete(self.firewall_policy)
        self.router_manager.delete(self.router)


class PortforwardingManagerTest(TestCase, ResourceManagerTest):
    """Test suite for PortforwardingManager"""

    def __init__(self, method_name="runTest"):
        super(PortforwardingManagerTest, self).__init__(methodName=method_name)
        self.router_manager = None

    def setUp(self):
        self.set_up(SednaClient, PortforwardingManager, Portforwarding)

    def build_resource(self):
        self.router_manager = self.router_manager if self.router_manager \
            else RouterManager(self.openstack_client)

        router_name = self.rand_name(
            "PortforwardingManagerTest_router", "sedna")
        self.router = self.router_manager.create(Router(name=router_name))
        self.external_network = Network(id=EXTERNAL_NETWORK_ID)
        self.router_manager.add_gateway_router(self.router, self.external_network)

        portforwarding_name = self.rand_name("PortforwardingManagerTest_portforwarding", "sedna")
        destination_ip = "10.0.61.1"
        destination_port = "10011"
        source_port = "10011"
        protocol = "TCP"
        router_id = self.router.id
        return Portforwarding(name=portforwarding_name, destination_ip=destination_ip,
                              destination_port=destination_port, source_port=source_port,
                              protocol=protocol, router_id=router_id)

    def test_create_with_incorrect_type(self):
        """
        test error raising when an object of incorrect type is given to create
        """
        with self.assertRaises(TypeError):
            self.resource_manager.create(object(), self.router.id)

    def test_get_with_incorrect_type(self):
        """
        test raising error when an object of incorrect type is given to the get
        function
        """
        with self.assertRaises(TypeError):
            self.resource_manager.get(object(), self.router.id)

    def test_delete_with_incorrect_type(self):
        """
        test error raising when delete parameter's type is incorrect
        """
        with self.assertRaises(TypeError):
            self.resource_manager.delete(object(), self.router.id)

    def test_list(self):
        port_forwarding_list = self.resource_manager(self.openstack_client).list(self.router.id)
        print port_forwarding_list

    def tearDown(self):
        self.tear_down()
        self.router_manager.delete(self.router)


class VpnIkepolicyManagerTest(TestCase, ResourceManagerTest):
    """Test suite for VpnIkepolicyManager"""
    def __init__(self, method_name="runTest"):
        super(VpnIkepolicyManagerTest, self).__init__(methodName=method_name)

    def setUp(self):
        self.set_up(NeutronClient, VpnIkepolicyManager, VpnIkepolicy)

    def build_resource(self):
        expected_resource_name = \
            self.rand_name("VpnIkepolicyTest_ikepolicy", "sedna")
        return VpnIkepolicy(name=expected_resource_name)

    def tearDown(self):
        self.tear_down()


class VpnIpsecpolicyManagerTest(TestCase, ResourceManagerTest):
    """Test suite for VpnIpsecpolicyManager"""
    def __init__(self, method_name="runTest"):
        super(VpnIpsecpolicyManagerTest, self).__init__(methodName=method_name)

    def setUp(self):
        self.set_up(NeutronClient, VpnIpsecpolicyManager, VpnIpsecpolicy)

    def build_resource(self):
        expected_resource_name = \
            self.rand_name("VpnIpsecpolicyManager_ipsecpolicy", "sedna")
        return VpnIpsecpolicy(name=expected_resource_name)

    def tearDown(self):
        self.tear_down()


class VpnServiceManagerTest(TestCase, ResourceManagerTest):
    """Test suite for VpnServiceManager"""

    def __init__(self, method_name="runTest"):
        super(VpnServiceManagerTest, self).__init__(methodName=method_name)
        self.router_manager = None

    def setUp(self):
        self.set_up(NeutronClient, VpnServiceManager, VpnService)

    def build_resource(self):
        self.router_manager = self.router_manager if self.router_manager \
            else RouterManager(self.openstack_client)
        router_name = self.rand_name("VpnServiceTest_router", "sedna")
        self.router = self.router_manager.create(Router(name=router_name))
        external_net = Network(EXTERNAL_NETWORK_ID)
        self.router_manager.add_gateway_router(self.router, external_net)
        expected_vpnservice_name = \
            self.rand_name("VpnServiceTest_vpnservice", "sedna")
        return VpnService(name=expected_vpnservice_name, router_id=self.router)

    def test_get_status(self):
        status = self.resource_manager.get_status(self.created_resource)
        print status

    def test_get_external_v4_ip(self):
        external_ip = self.resource_manager.get_external_v4_ip(self.created_resource)
        print external_ip

    def tearDown(self):
        self.tear_down()
        self.router_manager.delete(self.router)


class VpnEndpointGroupManagerTest(TestCase, ResourceManagerTest):
    """Test suite for VpnEndpointGroupManager"""

    def __init__(self, method_name="runTest"):
        super(VpnEndpointGroupManagerTest, self).__init__(methodName=method_name)
        self.subnet_manager = None
        self.network_manager = None

    def setUp(self):
        self.set_up(NeutronClient, VpnEndpointGroupManager, VpnEndpointGroup)

    def build_resource(self):
        # create subnet
        network_name = self.rand_name(
            "VpnEndpointGroupTest_network", "sedna")
        self.network_manager = self.network_manager if self.network_manager \
            else NetworkManager(self.openstack_client)
        self.network = self.network_manager.create(
            Network(name=network_name))

        subnet_name = self.rand_name("VpnEndpointGroupTest_subnet", "sedna")
        cidr = "192.167.164.0/24"
        self.subnet_manager = self.subnet_manager if self.subnet_manager \
            else SubnetManager(self.openstack_client)
        self.subnet = self.subnet_manager.create(
            Subnet(name=subnet_name, cidr=cidr, network=self.network))
        expected_endpointgroup_name = \
            self.rand_name("VpnEndpointGroupTest_eg", "sedna")
        return VpnEndpointGroup(name=expected_endpointgroup_name, type="subnet",
                                endpoints=[self.subnet])

    def test_create_with_cidr(self):
        cidr = "192.167.164.0/24"
        expected_endpointgroup_name = \
            self.rand_name("VpnEndpointGroupTest_eg", "sedna")
        return VpnEndpointGroup(name=expected_endpointgroup_name, type="subnet",
                                endpoints=[cidr])

    def tearDown(self):
        self.tear_down()
        self.subnet_manager.delete(self.subnet)
        self.network_manager.delete(self.network)


class VpnIpsecSiteConnectionManagerTest(TestCase, ResourceManagerTest):
    """Test suite for VpnIpsecSiteConnectionManager"""

    def __init__(self, method_name="runTest"):
        super(VpnIpsecSiteConnectionManagerTest, self).__init__(methodName=method_name)
        self.subnet_manager = None
        self.network_manager = None
        self.router_manager = None
        self.ipsecpolicy_manager = None
        self.ikepolicy_manager = None
        self.vpnservice_manager = None
        self.endpoint_group_manager = None

    def setUp(self):
        self.set_up(NeutronClient, VpnIpsecSiteConnectionManager, VpnIpsecSiteConnection)

    def build_resource(self):
        def create_subnet(cidr):
            network_name = self.rand_name(
                "VpnconnetctionTest_network", "sedna")
            self.networks.append(self.network_manager.create(
                Network(name=network_name)))

            subnet_name = self.rand_name("VpnconnetctionTest_subnet", "sedna")
            self.subnets.append(self.subnet_manager.create(
                Subnet(name=subnet_name, cidr=cidr, network=self.networks[-1])))

        def create_router_with_external_net():
            router_name = self.rand_name("VpnconnetctionTest_router", "sedna")
            self.routers.append(self.router_manager.create(Router(name=router_name)))
            external_net = Network(EXTERNAL_NETWORK_ID)
            self.router_manager.add_gateway_router(self.routers[-1], external_net)

        def create_vpnservice(router_id):
            vpnservice_name = \
                self.rand_name("VpnconnetctionTest_vpnservice", "sedna")
            self.vpnservices.append(
                self.vpnservice_manager.create(
                    VpnService(name=vpnservice_name, router_id=router_id)))

        def create_endpoint_group(endpoints_type, endpoints):
            endpoint_group_name = \
                self.rand_name("VpnconnetctionTest_endpoint_group", "sedna")
            return self.endpoint_group_manager.create(
                VpnEndpointGroup(
                    name=endpoint_group_name, type=endpoints_type, endpoints=endpoints))

        # create ipsecpolicy
        ipsecpolicy_name = self.rand_name(
            "VpnconnetctionTest_ipsecpolicy", "sedna")
        self.ipsecpolicy_manager = self.ipsecpolicy_manager if self.ipsecpolicy_manager \
            else VpnIpsecpolicyManager(self.openstack_client)
        self.ipsecpolicy = self.ipsecpolicy_manager.create(
            VpnIpsecpolicy(name=ipsecpolicy_name))

        # create ikepolicy
        ikepolicy_name = self.rand_name(
            "VpnconnetctionTest_ikepolicy", "sedna")
        self.ikepolicy_manager = self.ikepolicy_manager if self.ikepolicy_manager \
            else VpnIkepolicyManager(self.openstack_client)
        self.ikepolicy = self.ikepolicy_manager.create(
            VpnIkepolicy(name=ikepolicy_name))

        # create subnet1, subnet2
        self.network_manager = self.network_manager if self.network_manager \
            else NetworkManager(self.openstack_client)
        self.subnet_manager = self.subnet_manager if self.subnet_manager \
            else SubnetManager(self.openstack_client)
        self.networks = []
        self.subnets = []
        cidr1 = "192.167.160.0/24"
        cidr2 = "192.167.161.0/24"
        create_subnet(cidr=cidr1)
        create_subnet(cidr=cidr2)

        # create router1, router2 vs external net
        self.router_manager = self.router_manager if self.router_manager \
            else RouterManager(self.openstack_client)
        self.routers = []
        create_router_with_external_net()
        create_router_with_external_net()
        # associate with subnets
        self.router_manager.add_interface_router(self.routers[0], self.subnets[0])
        self.router_manager.add_interface_router(self.routers[1], self.subnets[1])

        # create vpnservice1 vpnservice2
        self.vpnservice_manager = self.vpnservice_manager if self.vpnservice_manager \
            else VpnServiceManager(self.openstack_client)
        self.vpnservices= []
        for router in self.routers:
            create_vpnservice(router.id)
        # get peer id
        peer_ids = []
        peer_ids.append(self.vpnservice_manager.get_external_v4_ip(self.vpnservices[0]))
        peer_ids.append(self.vpnservice_manager.get_external_v4_ip(self.vpnservices[1]))

        # create vpn-endpoint-group local and peer
        self.endpoint_group_manager = self.endpoint_group_manager if self.endpoint_group_manager \
            else VpnEndpointGroupManager(self.openstack_client)
        self.endpoint_locals = []
        self.endpoint_locals.append(create_endpoint_group(
            endpoints_type="subnet", endpoints=[self.subnets[0]]))
        self.endpoint_locals.append(create_endpoint_group(
            endpoints_type="subnet", endpoints=[self.subnets[1]]))
        self.endpoint_peers = []
        self.endpoint_peers.append(create_endpoint_group(
            endpoints_type="cidr", endpoints=[cidr1]))
        self.endpoint_peers.append(create_endpoint_group(
            endpoints_type="cidr", endpoints=[cidr2]))

        # create vpn-connection
        expected_vpnconnection_name = \
            self.rand_name("VpnconnetctionTest_connection", "sedna")
        return VpnIpsecSiteConnection(
            name=expected_vpnconnection_name, psk="secert",
            ipsecpolicy_id=self.ipsecpolicy.id, ikepolicy_id=self.ikepolicy.id,
            peer_address=peer_ids[1], peer_id=peer_ids[1],
            peer_ep_group_id=self.endpoint_peers[1].id,
            local_ep_group_id=self.endpoint_locals[0].id,
            vpnservice_id=self.vpnservices[0].id)

    def tearDown(self):
        def delete_router(index):
            self.router_manager.remove_gateway_router(
                router=self.routers[index])
            self.router_manager.remove_interface_router(
                router=self.routers[index],
                subnet=self.subnets[index])
            self.router_manager.delete(self.routers[index])

        self.tear_down()
        self.ikepolicy_manager.delete(self.ikepolicy)
        self.ipsecpolicy_manager.delete(self.ipsecpolicy)
        for vpnservice in self.vpnservices:
            self.vpnservice_manager.delete(vpnservice)
        for endpoint in self.endpoint_locals:
            self.endpoint_group_manager.delete(endpoint)

        delete_router(0)
        delete_router(1)

        for subnet in self.subnets:
            self.subnet_manager.delete(subnet)

        for network in self.networks:
            self.network_manager.delete(network)

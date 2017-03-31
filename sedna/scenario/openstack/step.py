from keystoneclient.v3.client import Client as KeystoneClient
from novaclient.v2.client import Client as NovaClient
from glanceclient.v2 import Client as GlanceClient
from cinderclient.v2.client import Client as CinderClient
from neutronclient.v2_0.client import Client as NeutronClient

from sedna.openstack.client import SednaClient

from sedna.scenario import Step

from sedna.openstack.nova import ServerManager, FlavorManager, \
    KeypairManager
from sedna.openstack.glance import ImageManager, IMAGE_PATH
from sedna.openstack.neutron import NetworkManager, \
    PortManager, RouterManager, FloatingipManager, SecurityGroupManager,\
    LoadBalancerManager, ListenerManager, LBaaSPoolManager, \
    FirewallRuleManager, SubnetManager, PortforwardingManager, \
    FirewallPolicyManager, FirewallManager, LBaaSHealthMonitorManager, \
    LBaaSMemberManager, VpnIpsecpolicyManager, VpnIkepolicyManager, \
    VpnEndpointGroupManager, VpnServiceManager, \
    VpnIpsecSiteConnectionManager
from sedna.openstack.cinder import VolumeManager
from sedna.openstack.cinder import SnapshotManager
from sedna.openstack.keystone import UserManager
from sedna.openstack.keystone import ProjectManager
from sedna.openstack.keystone import DomainManager

from sedna.openstack.common import Server, Flavor, Image, Subnet,\
    Network, Port, Router, Floatingip, Volume, Snapshot, User, Project,\
    Domain, SecurityGroup, Keypair, LoadBalancer, Listener, LBaaSPool,\
    LBaaSHealthMonitor, LBaaSMember, FirewallRule, FirewallPolicy, \
    Firewall, VpnIpsecpolicy, VpnIkepolicy, VpnEndpointGroup, VpnService, \
    Portforwarding, VpnIpsecSiteConnection

from random import randint

class PortCreateStep(Step):
    """The class to contain context variables across port test steps"""

    def __init__(self, name):
        super(PortCreateStep, self).__init__(name)
        self.port_manager = None
        self.port = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.port_manager = PortManager(os_client=neutron_client)
        self.port = self.port_manager.create(
            Port(name=self.name, subnet=context.subnet))

        context.port = self.port

    def cleanup(self, context):
        if self.port_manager.get(self.port):
            self.port_manager.delete(self.port)
            context.port = None


class NetworkCreateStep(Step):
    """The class to contain context variables across network test steps"""

    def __init__(self, name):
        super(NetworkCreateStep, self).__init__(name)
        self.network_manager = None
        self.network = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.network_manager = NetworkManager(os_client=neutron_client)
        self.network = self.network_manager.create(Network(name=self.name))

        context.network = self.network

    def cleanup(self, context):
        if self.network_manager.get(self.network):
            self.network_manager.delete(self.network)
            context.network = None


class SubnetCreateStep(Step):
    """The class to contain context variables across subnet test steps"""

    def __init__(self, name):
        super(SubnetCreateStep, self).__init__(name)
        self.subnet_manager = None
        self.subnet = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.subnet_manager = SubnetManager(os_client=neutron_client)
        expected_cidr = "192.167." + str(randint(2, 254))\
                        + "." + str(randint(2, 254)) + "/24"
        self.subnet = \
            self.subnet_manager.create(Subnet(
                name=self.name,
                cidr=expected_cidr,
                network=context.network))

        context.subnet = self.subnet

    def cleanup(self, context):
        if self.subnet_manager.get(self.subnet):
            self.subnet_manager.delete(self.subnet)
            context.subnet = None


class RouterCreateStep(Step):
    """The class to contain context variables across router test steps"""

    def __init__(self, name):
        super(RouterCreateStep, self).__init__(name)
        self.router_manager = None
        self.router = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.router_manager = RouterManager(os_client=neutron_client)
        self.router = \
            self.router_manager.create(Router(
                name=self.name))

        context.router = self.router

    def cleanup(self, context):
        if self.router_manager.get(self.router):
            self.router_manager.delete(self.router)
            context.router = None


class RouterSetGatewayStep(Step):
    """
    The class to contain context variables across
    router setting gateway test steps
    """

    def __init__(self, name):
        super(RouterSetGatewayStep, self).__init__(name)
        self.router_manager = None

    def execute(self, context):
        self.router_manager = RouterManager(os_client=context.neutron_client)
        self.router_manager.add_gateway_router(
            router=context.router, network=context.external_net)

    def cleanup(self, context):
        if self.router_manager.get(context.router):
            self.router_manager.remove_gateway_router(context.router)


class RouterAddInterfaceStep(Step):
    """
    The class to contain context variables across
    router add interface test steps
    """
    def __init__(self, name, router_index=None, subnet_index=None):
        super(RouterAddInterfaceStep, self).__init__(name)
        self.router_manager = None
        self.router_index = router_index
        self.subnet_index = subnet_index

    def execute(self, context):
        self.router_manager = RouterManager(os_client=context.neutron_client)
        if self.router_index is None or self.subnet_index is None:
            self.router_manager.add_interface_router(
                router=context.router, subnet=context.subnet)
        else:
            self.router_manager.add_interface_router(
                router=context.routers[self.router_index],
                subnet=context.subnets[self.subnet_index])

    def cleanup(self, context):
        if self.router_index is None or self.subnet_index is None:
            if self.router_manager.get(context.router):
                self.router_manager.remove_interface_router(
                    router=context.router, subnet=context.subnet)
        else:
            if self.router_manager.get(
                    context.routers[self.router_index]):
                self.router_manager.remove_interface_router(
                    router=context.routers[self.router_index],
                    subnet=context.subnets[self.subnet_index])


class FloatingipCreateStep(Step):
    """The class to contain context variables across floatingip test steps"""

    def __init__(self, name):
        super(FloatingipCreateStep, self).__init__(name)
        self.floatingip_manager = None
        self.floatingip = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.floatingip_manager = FloatingipManager(os_client=neutron_client)
        self.floatingip = \
            self.floatingip_manager.create(Floatingip(
                name=self.name,
                external_net=context.external_net))

        context.floatingip = self.floatingip

    def cleanup(self, context):
        if self.floatingip_manager.get(self.floatingip):
            self.floatingip_manager.delete(self.floatingip)
            context.floatingip = None


class FloatingipAssociateStep(Step):
    """
    The class to contain context variables across
    floatingip associating test steps
    """

    def __init__(self, name):
        super(FloatingipAssociateStep, self).__init__(name)
        self.floatingip_manager = None

    def execute(self, context):
        self.floatingip_manager = \
            FloatingipManager(os_client=context.neutron_client)
        self.floatingip_manager.associate_floatingip(
            floatingip=context.floatingip,
            network=context.network,
            server=context.server)

    def cleanup(self, context):
        if self.floatingip_manager.get(context.floatingip):
            self.floatingip_manager.disassociate_floatingip(context.floatingip)


class ImageCreateStep(Step):
    """
    The class to contain context
    variables across Image test steps
    """

    def __init__(self, name):
        super(ImageCreateStep, self).__init__(name)
        self.image_manager = None
        self.image = None

    def execute(self, context):
        glance_client = GlanceClient(session=context.os_session)
        self.image_manager = ImageManager(glance_client=glance_client)
        self.image = self.image_manager.create(
            Image(name=self.name, disk_format="qcow2",
                  container_format="bare", visibility="private"))

        self.image_manager.upload_image(self.image, IMAGE_PATH)

        context.image = self.image

    def cleanup(self, context):
        if self.image_manager.get(self.image):
            self.image_manager.delete(self.image)
            context.image = None


class FlavorCreateStep(Step):
    """The class to contain context variables across Flavor test steps"""

    def __init__(self, name):
        super(FlavorCreateStep, self).__init__(name)
        self.flavor_manager = None
        self.flavor = None

    def execute(self, context):
        nova_client = NovaClient(session=context.os_session)
        self.flavor_manager = FlavorManager(os_client=nova_client)
        self.flavor = self.flavor_manager.create(
            Flavor(name=self.name, ram=1024, disk=1, vcpus=1))

        context.flavor = self.flavor

    def cleanup(self, context):
        if self.flavor_manager.get(self.flavor):
            self.flavor_manager.delete(self.flavor)
            context.flavor = None


class ServerCreateStep(Step):
    """The class to contain context variables across Server test steps"""

    def __init__(self, name):
        super(ServerCreateStep, self).__init__(name)
        self.server_manager = None
        self.server = None

    def execute(self, context):
        nova_client = NovaClient(session=context.os_session)
        glance_client = GlanceClient(session=context.os_session)
        neutron_client = NeutronClient(session=context.os_session)
        self.server_manager = ServerManager(nova_client=nova_client,
                                            glance_client=glance_client,
                                            neutron_client=neutron_client)
        context.nics = [{"net-id": context.network.id}]
        self.server = self.server_manager.create(
            Server(name=self.name, image=context.image,
                   flavor=context.flavor, nics=context.nics))
        context.server = self.server

    def cleanup(self, context):
        if self.server_manager.get(self.server):
            self.server_manager.delete(self.server)
            context.server = None


class CreateServerVolumeStep(Step):
    """The class to contain context variables across Server test steps"""

    def __init__(self, name):
        super(CreateServerVolumeStep, self).__init__(name)
        self.server_manager = None
        self.cinder_client = None

    def execute(self, context):
        nova_client = NovaClient(session=context.os_session)
        glance_client = GlanceClient(session=context.os_session)
        neutron_client = NeutronClient(session=context.os_session)
        self.cinder_client = CinderClient(session=context.os_session)
        self.server_manager = ServerManager(nova_client=nova_client,
                                            glance_client=glance_client,
                                            neutron_client=neutron_client)
        self.server_manager.create_server_volume(
            server=context.server, volume=context.volume,
            cinder_client=self.cinder_client
        )

    def cleanup(self, context):
        if self.server_manager.get(context.server):
            self.server_manager.delete_server_volume(
                server=context.server, volume=context.volume,
                cinder_client=self.cinder_client)


class ServerRebootStep(Step):
    """The class to contain context variables across Server test steps"""
    def __init__(self, name):
        super(ServerRebootStep, self).__init__(name)
        self.server_manager = None

    def execute(self, context):
        nova_client = NovaClient(session=context.os_session)
        glance_client = GlanceClient(session=context.os_session)
        neutron_client = NeutronClient(session=context.os_session)
        self.server_manager = ServerManager(nova_client=nova_client,
                                            glance_client=glance_client,
                                            neutron_client=neutron_client)
        self.server_manager.reboot(context.server)

    def cleanup(self, context):
        self.server_manager = None


class ServerStartStep(Step):
    """The class to contain context variables across Server test steps"""
    def __init__(self, name):
        super(ServerStartStep, self).__init__(name)
        self.server_manager = None

    def execute(self, context):
        nova_client = NovaClient(session=context.os_session)
        glance_client = GlanceClient(session=context.os_session)
        neutron_client = NeutronClient(session=context.os_session)
        self.server_manager = ServerManager(nova_client=nova_client,
                                            glance_client=glance_client,
                                            neutron_client=neutron_client)
        self.server_manager.start(context.server)

    def cleanup(self, context):
        self.server_manager = None


class ServerStopStep(Step):
    """The class to contain context variables across Server test steps"""
    def __init__(self, name):
        super(ServerStopStep, self).__init__(name)
        self.server_manager = None

    def execute(self, context):
        nova_client = NovaClient(session=context.os_session)
        glance_client = GlanceClient(session=context.os_session)
        neutron_client = NeutronClient(session=context.os_session)
        self.server_manager = ServerManager(nova_client=nova_client,
                                            glance_client=glance_client,
                                            neutron_client=neutron_client)
        self.server_manager.stop(context.server)

    def cleanup(self, context):
        self.server_manager = None


class VolumeCreateStep(Step):
    """The class to contain context variables across volume test steps"""

    def __init__(self, name):
        super(VolumeCreateStep, self).__init__(name)
        self.volume_manager = None
        self.volume = None

    def execute(self, context):
        cinder_client = CinderClient(session=context.os_session)
        self.volume_manager = VolumeManager(cinder_client=cinder_client)
        self.volume = self.volume_manager.create(
            Volume(name=self.name, size=3))
        context.volume = self.volume

    def cleanup(self, context):
        if self.volume_manager.get(self.volume):
            self.volume_manager.delete(self.volume)
            context.volume = None


class SnapshotCreateStep(Step):
    """The class to contain context variables across snapshot test steps"""

    def __init__(self, name):
        super(SnapshotCreateStep, self).__init__(name)
        self.snapshot_manager = None
        self.snapshot = None

    def execute(self, context):
        cinder_client = CinderClient(session=context.os_session)
        self.snapshot_manager = SnapshotManager(cinder_client=cinder_client)
        self.snapshot = self.snapshot_manager.create(
            Snapshot(name=self.name, volume=context.volume))
        context.snapshot = self.snapshot

    def cleanup(self, context):
        self.snapshot_manager.delete(self.snapshot)
        context.snapshot = None


class UserCreateStep(Step):
    """The class to contain context variables across user test steps"""

    def __init__(self, name):
        super(UserCreateStep, self).__init__(name)
        self.user_manager = None
        self.user = None

    def execute(self, context):
        keystone_client = KeystoneClient(session=context.os_session)
        self.user_manager = UserManager(keystone_client=keystone_client)
        self.user = self.user_manager.create(User(name=context.name))
        context.user = self.user

    def cleanup(self, context):
        self.user_manager.delete(self.user)
        context.user = None


class ProjectCreateStep(Step):
    """The class to contain context variables across project test steps"""

    def __init__(self, name):
        super(ProjectCreateStep, self).__init__(name)
        self.project_manager = None
        self.project = None

    def execute(self, context):
        keystone_client = KeystoneClient(session=context.os_session)
        self.project_manager = ProjectManager(keystone_client=keystone_client)
        self.project = self.project_manager.create(
            Project(name=context.name, domain=context.domain))
        context.project = self.project

    def cleanup(self, context):
        self.project_manager.delete(self.project)
        context.project = None


class DomainCreateStep(Step):
    """The class to contain context variables across domain test steps"""

    def __init__(self, name):
        super(DomainCreateStep, self).__init__(name)
        self.domain_manager = None
        self.domain = None

    def execute(self, context):
        keystone_client = KeystoneClient(session=context.os_session)
        self.domain_manager = DomainManager(keystone_client=keystone_client)
        self.domain = self.domain_manager.create(Domain(name=context.name))
        context.domain = self.domain

    def cleanup(self, context):
        self.domain.enabled = False
        self.domain_manager.update(self.domain)
        self.domain_manager.delete(self.domain)
        context.domain = None


class SecurityGroupCreateStep(Step):
    """"""

    def __init__(self, name):
        super(SecurityGroupCreateStep, self).__init__(name)
        self.security_group_manager = None
        self.security_group = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.security_group_manager = SecurityGroupManager(
            os_client=neutron_client)
        self.security_group = self.security_group_manager.create(
            SecurityGroup(name=context.name))
        context.security_group = self.security_group

    def cleanup(self, context):
        self.security_group_manager.delete(self.security_group)
        context.security_group = None


class KeypairStep(Step):
    """"""

    def __init__(self, name):
        super(KeypairStep, self).__init__(name)
        self.keypair_manager = None
        self.keypair = None

    def execute(self, context):
        keypair_client = NovaClient(session=context.os_session)
        self.keypair_manager = KeypairManager(nova_client=keypair_client)
        self.keypair = self.keypair_manager.create(Keypair(name=context.name))

    def cleanup(self, context):
        self.keypair_manager.delete(self.keypair)


class LoadBalancerCreateStep(Step):
    """The class to contain context variables across loadbalancer test steps"""

    def __init__(self, name, subnet_array_index=-1):
        # defult subnet_array_index=-1 means subnet is not in an array format
        super(LoadBalancerCreateStep, self).__init__(name)
        self.loadbalancer_manager = None
        self.loadbalancer = None
        self.subnet_array_index = subnet_array_index

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.loadbalancer_manager = LoadBalancerManager(
            os_client=neutron_client)
        # get the subnet for the loadbalancer
        if self.subnet_array_index == -1:
            subnet = context.subnet
        else:
            subnet = context.subnets[self.subnet_array_index]
        self.loadbalancer = \
            self.loadbalancer_manager.create(LoadBalancer(
                name=self.name,
                subnet=subnet))
        context.loadbalancer = self.loadbalancer

    def cleanup(self, context):
        if self.loadbalancer_manager.get(self.loadbalancer):
            self.loadbalancer_manager.delete(self.loadbalancer)
            context.loadbalancer = None


class LBaaSPoolCreateStep(Step):
    def __init__(self, name):
        super(LBaaSPoolCreateStep, self).__init__(name)
        self.pool_manager = None
        self.pool = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.pool_manager = LBaaSPoolManager(os_client=neutron_client)
        expected_protocol = "HTTP"
        expected_lb_algorithm = "ROUND_ROBIN"
        self.pool = \
            self.pool_manager.create(LBaaSPool(
                name=self.name,
                loadbalancer=context.loadbalancer,
                protocol=expected_protocol,
                lb_algorithm=expected_lb_algorithm))
        context.lbaas_pool = self.pool

    def cleanup(self, context):
        if self.pool_manager.get(self.pool):
            self.pool_manager.delete(self.pool)
            context.pool = None


class ListenerCreateStep(Step):
    def __init__(self, name):
        super(ListenerCreateStep, self).__init__(name)
        self.listener_manager = None
        self.listener = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.listener_manager = ListenerManager(os_client=neutron_client)
        expected_protocol = "HTTP"
        expected_protocol_port = "80"
        self.listener = \
            self.listener_manager.create(Listener(
                name=self.name,
                loadbalancer=context.loadbalancer,
                protocol=expected_protocol,
                protocol_port=expected_protocol_port))
        context.listener = self.listener

    def cleanup(self, context):
        if self.listener_manager.get(self.listener):
            self.listener_manager.delete(self.listener)
            context.listener = None


class LBaaSHealthMonitorCreateStep(Step):
    def __init__(self, name):
        super(LBaaSHealthMonitorCreateStep, self).__init__(name)
        self.healthmonitor_manager = None
        self.healthmonitor = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.healthmonitor_manager = LBaaSHealthMonitorManager(
            os_client=neutron_client)
        expected_delay = "10"
        expected_max_retries = "5"
        expected_timeout = "300"
        expected_type = "HTTP"
        self.healthmonitor = \
            self.healthmonitor_manager.create(LBaaSHealthMonitor(
                name=self.name,
                delay=expected_delay,
                max_retries=expected_max_retries,
                timeout=expected_timeout,
                type=expected_type,
                lbaas_pool=context.lbaas_pool))
        context.lbaas_healthmonitor = self.healthmonitor

    def cleanup(self, context):
        if self.healthmonitor_manager.get(self.healthmonitor):
            self.healthmonitor_manager.delete(self.healthmonitor)
            context.lbaas_healthmonitor = None


class LBaaSMemberCreateStep(Step):
    def __init__(self, name):
        super(LBaaSMemberCreateStep, self).__init__(name)
        self.member_manager = None
        self.member = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.member_manager = LBaaSMemberManager(os_client=neutron_client)
        expected_address = "10.0.61.2"
        expected_protocol_port = "80"
        self.member = \
            self.member_manager.create(LBaaSMember(
                name=self.name,
                subnet=context.subnets[1],
                address=expected_address,
                protocol_port=expected_protocol_port,
                lbaas_pool=context.lbaas_pool))
        context.lbaas_member = self.member

    def cleanup(self, context):
        if self.member_manager.get(self.member):
            self.member_manager.delete(self.member)
            context.lbaas_member = None


class MultipleNetworkCreateStep(Step):
    """The class to contain context variables across network test steps"""

    def __init__(self, name, index):
        super(MultipleNetworkCreateStep, self).__init__(name)
        self.network_manager = None
        self.network = None
        self.index = index

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.network_manager = NetworkManager(os_client=neutron_client)
        self.network = self.network_manager.create(Network(name=self.name))

        context.networks.append(self.network)

    def cleanup(self, context):
        if self.network_manager.get(self.network):
            self.network_manager.delete(self.network)
            context.network = None


class MultipleSubnetCreateStep(Step):
    """The class to contain context variables across subnet test steps"""

    def __init__(self, name, index, cidr):
        super(MultipleSubnetCreateStep, self).__init__(name)
        self.subnet_manager = None
        self.subnet = None
        self.index = index
        self.cidr = cidr

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.subnet_manager = SubnetManager(os_client=neutron_client)
        expected_cidr = self.cidr
        self.subnet = \
            self.subnet_manager.create(Subnet(
                name=self.name,
                cidr=expected_cidr,
                network=context.networks[self.index]))

        context.subnets.append(self.subnet)

    def cleanup(self, context):
        if self.subnet_manager.get(self.subnet):
            self.subnet_manager.delete(self.subnet)
            context.subnets = []


class FirewallRuleCreateStep(Step):
    def __init__(self, name):
        super(FirewallRuleCreateStep, self).__init__(name)
        self.firewall_rule_manager = None
        self.firewall_rule = None

    def execute(self, context):
        expected_action = "allow"
        expected_protocol = "TCP"
        neutron_client = NeutronClient(session=context.os_session)
        self.firewall_rule_manager = \
            FirewallRuleManager(os_client=neutron_client)
        self.firewall_rule = self.firewall_rule_manager.create(
            FirewallRule(name=self.name, action=expected_action,
                         protocol=expected_protocol))

        context.firewall_rule = self.firewall_rule

    def cleanup(self, context):
        if self.firewall_rule_manager.get(self.firewall_rule):
            self.firewall_rule_manager.delete(self.firewall_rule)
            context.firewall_rule = None


class AppendFirewallRuleStep(Step):
    def __init__(self, name):
        super(AppendFirewallRuleStep, self).__init__(name)
        self.firewall_rule = None

    def execute(self, context):
        self.firewall_rule = context.firewall_rule
        context.firewall_rules.append(context.firewall_rule)

    def cleanup(self, context):
        context.firewall_rules.remove(self.firewall_rule)


class FirewallPolicyCreateStep(Step):
    """
    The class to contain context variables across Firewall Policy test steps;
    without firewall rule
    """

    def __init__(self, name):
        super(FirewallPolicyCreateStep, self).__init__(name)
        self.firewall_policy_manager = None
        self.firewall_policy = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.firewall_policy_manager = \
            FirewallPolicyManager(os_client=neutron_client)
        self.firewall_policy = \
            self.firewall_policy_manager.create(FirewallPolicy(
                name=self.name, firewall_rules=context.firewall_rules))

        context.firewall_policy = self.firewall_policy

    def cleanup(self, context):
        if self.firewall_policy_manager.get(self.firewall_policy):
            self.firewall_policy_manager.delete(self.firewall_policy)
            context.firewall_policy = None


class FirewallSettingStep(Step):
    def __init__(self, name):
        super(FirewallSettingStep, self).__init__(name)
        self.router_id = None
        self.firewall_policy_id = None

    def execute(self, context):
        if hasattr(context, 'router') and hasattr(context.router, 'id'):
            self.router_id = context.router.id
            context.router_ids.append(self.router_id)
        self.firewall_policy_id = context.firewall_policy.id
        context.firewall_policy_id = self.firewall_policy_id

    def cleanup(self, context):
        if self.router_id is not None:
            context.router_ids.remove(self.router_id)
        context.firewall_policy_id = None


class FirewallCreateStep(Step):
    """
    The class to contain context variables across Firewall Policy test steps;
    without firewall rule
    """

    def __init__(self, name):
        super(FirewallCreateStep, self).__init__(name)
        self.firewall_manager = None
        self.firewall = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.firewall_manager = FirewallManager(os_client=neutron_client)
        self.firewall = \
            self.firewall_manager.create(
                Firewall(name=self.name, router_ids=context.router_ids,
                         firewall_policy_id=context.firewall_policy_id))

        context.firewall = self.firewall

    def cleanup(self, context):
        if self.firewall_manager.get(self.firewall):
            self.firewall_manager.delete(self.firewall)
            context.firewall = None


class PortforwardingCreateStep(Step):
    """
    The class to contain context variables across Portforwarding test steps;
    """

    def __init__(self, name):
        super(PortforwardingCreateStep, self).__init__(name)
        self.portforwarding_manager = None
        self.portforwarding = None

    def execute(self, context):
        neutron_client = context.neutron_client
        expected_destination_ip = "10.0.61.1"
        expected_destination_port = "10011"
        expected_source_port = "10011"
        expected_protocol = "TCP"
        self.portforwarding_manager = \
            PortforwardingManager(os_client=neutron_client)
        self.portforwarding = \
            self.portforwarding_manager.create(
                Portforwarding(name=self.name, router_id=context.router.id,
                               destination_ip=expected_destination_ip,
                               destination_port=expected_destination_port,
                               source_port=expected_source_port,
                               protocol=expected_protocol))

        context.portforwarding = self.portforwarding

    def cleanup(self, context):
        if self.portforwarding_manager.get(
                self.portforwarding, context.router.id):
            self.portforwarding_manager.delete(
                self.portforwarding, context.router.id)
            context.portforwarding = None


class ExternalNetworkSettingStep(Step):
    def __init__(self, name, ext_network_id=None):
        super(ExternalNetworkSettingStep, self).__init__(name)
        self.ext_network_id = ext_network_id

    def execute(self, context):
        context.external_net = Network(id=self.ext_network_id)

    def cleanup(self, context):
        context.external_net = None


class VpnIpsecpolicyCreateStep(Step):
    def __init__(self, name):
        super(VpnIpsecpolicyCreateStep, self).__init__(name)
        self.ipsecpolicy_manager = None
        self.ipsecpolicy = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.ipsecpolicy_manager = \
            VpnIpsecpolicyManager(os_client=neutron_client)
        self.ipsecpolicy = \
            self.ipsecpolicy_manager.create(VpnIpsecpolicy(name=self.name))
        context.ipsecpolicy = self.ipsecpolicy

    def cleanup(self, context):
        if self.ipsecpolicy_manager.get(self.ipsecpolicy):
            self.ipsecpolicy_manager.delete(self.ipsecpolicy)
            context.ipsecpolicy = None


class VpnIkepolicyCreateStep(Step):
    def __init__(self, name):
        super(VpnIkepolicyCreateStep, self).__init__(name)
        self.ikepolicy_manager = None
        self.ikepolicy = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.ikepolicy_manager = VpnIkepolicyManager(os_client=neutron_client)
        self.ikepolicy = \
            self.ikepolicy_manager.create(VpnIkepolicy(name=self.name))
        context.ikepolicy = self.ikepolicy

    def cleanup(self, context):
        if self.ikepolicy_manager.get(self.ikepolicy):
            self.ikepolicy_manager.delete(self.ikepolicy)
            context.ikepolicy = None


class VpnEndpointGroupCreateStep(Step):
    def __init__(self, name, type=None, endpoints=[]):
        super(VpnEndpointGroupCreateStep, self).__init__(name)
        self.endpoint_group_manager = None
        self.endpoint_group = None
        self.type = type
        self.endpoints = endpoints

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.endpoint_group_manager = VpnEndpointGroupManager(
            os_client=neutron_client)
        self.endpoint_group = \
            self.endpoint_group_manager.create(
                VpnEndpointGroup(name=self.name, type=self.type,
                                 endpoints=self.endpoints))
        context.endpoint_group = self.endpoint_group

    def cleanup(self, context):
        if self.endpoint_group_manager.get(self.endpoint_group):
            self.endpoint_group_manager.delete(self.endpoint_group)
            context.endpoint_group = None


class VpnServiceCreateStep(Step):
    def __init__(self, name, router_id=None):
        super(VpnServiceCreateStep, self).__init__(name)
        self.vpnservice_manager = None
        self.vpnservice = None
        self.router_id = router_id

    def execute(self, context):
        if self.router_id is None:
            self.router_id = context.router.id
        neutron_client = context.neutron_client
        self.vpnservice_manager = VpnServiceManager(
            os_client=neutron_client)
        self.vpnservice = \
            self.vpnservice_manager.create(
                VpnService(name=self.name, router_id=self.router_id))
        context.vpnservice = self.vpnservice

    def cleanup(self, context):
        if self.vpnservice_manager.get(self.vpnservice):
            self.vpnservice_manager.delete(self.vpnservice)
            context.vpnservice = None


class MultiRouterWithGatewayCreateAtOnceStep(Step):
    def __init__(self, name, names=[], number=2):
        super(MultiRouterWithGatewayCreateAtOnceStep, self).__init__(name)
        self.names = names
        self.router_manager = None
        self.routers = []
        self.number = number

    def execute(self, context):
        neutron_client = context.neutron_client
        self.router_manager = RouterManager(os_client=neutron_client)
        for i in range(self.number):
            self.routers.append(
                self.router_manager.create(Router(name=self.names[i])))
            self.router_manager.add_gateway_router(
                router=self.routers[-1], network=context.external_net)
        context.routers = self.routers

    def cleanup(self, context):
        for router in self.routers:
            if self.router_manager.get(router):
                self.router_manager.delete(router)


class MultiVpnServiceCreateAtOnceStep(Step):
    def __init__(self, name, names=[], number=2):
        super(MultiVpnServiceCreateAtOnceStep, self).__init__(name)
        self.vpnservice_manager = None
        self.vpnservices = []
        self.number = number
        self.names = names

    def execute(self, context):
        neutron_client = context.neutron_client
        self.vpnservice_manager = VpnServiceManager(os_client=neutron_client)
        for i in range(self.number):
            self.vpnservices.append(
                self.vpnservice_manager.create(
                    VpnService(name=self.name, router_id=context.routers[i].id)))
        context.vpnservices = self.vpnservices

    def cleanup(self, context):
        for service in self.vpnservices:
            if self.vpnservice_manager.get(service):
                self.vpnservice_manager.delete(service)


class MultiVpnEndpointsCreateAtOnceStep(Step):
    def __init__(self, name, names, number=2):
        super(MultiVpnEndpointsCreateAtOnceStep, self).__init__(name)
        self.endpoint_manager = None
        self.local_endpoints = []
        self.peer_endpoints = []
        self.number = number
        self.names = names

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.endpoint_manager = VpnEndpointGroupManager(
            os_client=neutron_client)
        for i in range(self.number):
            self.local_endpoints.append(
                self.endpoint_manager.create(
                    VpnEndpointGroup(
                        name=self.name, type="subnet",
                        endpoints=[context.subnets[i]])))
            self.peer_endpoints.append(
                self.endpoint_manager.create(
                    VpnEndpointGroup(
                        name=self.name, type="cidr",
                        endpoints=[context.subnets[i].cidr])))
        context.local_endpoints = self.local_endpoints
        context.peer_endpoints = self.peer_endpoints

    def cleanup(self, context):
        for endpoint in self.local_endpoints:
            if self.endpoint_manager.get(endpoint):
                self.endpoint_manager.delete(endpoint)
        for endpoint in self.peer_endpoints:
            if self.endpoint_manager.get(endpoint):
                self.endpoint_manager.delete(endpoint)
        context.peer_endpoints = None
        context.local_endpoints = None


class VpnIpsecSiteConnectionCreateStep(Step):
    def __init__(self, name):
        super(VpnIpsecSiteConnectionCreateStep, self).__init__(name)
        self.vpn_connection_manager = None
        self.vpn_connection = None
        self.vpnservice_manager = None

    def execute(self, context):
        self.vpnservice_manager = VpnServiceManager(
            os_client=context.neutron_client)
        peer_id = self.vpnservice_manager.get_external_v4_ip(
            context.vpnservices[1])
        psk = "secret"
        ikepolicy_id = context.ikepolicy.id
        ipsecpolicy_id = context.ipsecpolicy.id
        peer_ep_group_id = context.peer_endpoints[1].id
        peer_address = peer_id
        local_ep_group_id = context.local_endpoints[0].id
        vpnservice_id = context.vpnservices[0].id

        neutron_client = context.neutron_client
        self.vpn_connection_manager = VpnIpsecSiteConnectionManager(
            os_client=neutron_client)
        self.vpn_connection = \
            self.vpn_connection_manager.create(
                VpnIpsecSiteConnection(
                    name=self.name, psk=psk,
                    ipsecpolicy_id=ipsecpolicy_id,
                    peer_ep_group_id=peer_ep_group_id,
                    ikepolicy_id=ikepolicy_id,
                    vpnservice_id=vpnservice_id,
                    local_ep_group_id=local_ep_group_id,
                    peer_address=peer_address,
                    peer_id=peer_id))
        context.vpn_connection = self.vpn_connection

    def cleanup(self, context):
        if self.vpn_connection_manager.get(self.vpn_connection):
            self.vpn_connection_manager.delete(self.vpn_connection)
            context.vpn_connection = None


class PeerVpnConnectionsCreateStep(Step):
    def __init__(self, name):
        super(PeerVpnConnectionsCreateStep, self).__init__(name)
        self.vpn_connection_manager = None
        self.vpn_connection_local = None
        self.vpn_connection_peer = None
        self.vpnservice_manager = None

    def execute(self, context):
        self.vpnservice_manager = VpnServiceManager(
            os_client=context.neutron_client)
        peer_id_local = self.vpnservice_manager.get_external_v4_ip(
            context.vpnservices[1])
        peer_id_peer = self.vpnservice_manager.get_external_v4_ip(
            context.vpnservices[0])
        psk = "secret"
        ikepolicy_id = context.ikepolicy.id
        ipsecpolicy_id = context.ipsecpolicy.id
        peer_ep_group_id_local = context.peer_endpoints[1].id
        peer_ep_group_id_peer = context.peer_endpoints[0].id
        peer_address_local = peer_id_local
        peer_address_peer = peer_id_peer
        local_ep_group_id_local = context.local_endpoints[0].id
        local_ep_group_id_peer = context.local_endpoints[1].id
        vpnservice_id_local = context.vpnservices[0].id
        vpnservice_id_peer = context.vpnservices[1].id

        self.vpn_connection_manager = VpnIpsecSiteConnectionManager(
            os_client=context.neutron_client)
        self.vpn_connection_local = \
            self.vpn_connection_manager.create(
                VpnIpsecSiteConnection(
                    name=self.name, psk=psk,
                    ipsecpolicy_id=ipsecpolicy_id,
                    peer_ep_group_id=peer_ep_group_id_local,
                    ikepolicy_id=ikepolicy_id,
                    vpnservice_id=vpnservice_id_local,
                    local_ep_group_id=local_ep_group_id_local,
                    peer_address=peer_address_local,
                    peer_id=peer_id_local))
        self.vpn_connection_peer = \
            self.vpn_connection_manager.create(
                VpnIpsecSiteConnection(
                    name=self.name, psk=psk,
                    ipsecpolicy_id=ipsecpolicy_id,
                    peer_ep_group_id=peer_ep_group_id_peer,
                    ikepolicy_id=ikepolicy_id,
                    vpnservice_id=vpnservice_id_peer,
                    local_ep_group_id=local_ep_group_id_peer,
                    peer_address=peer_address_peer,
                    peer_id=peer_id_peer))
        context.vpn_connection_local = self.vpn_connection_local
        context.vpn_connection_peer = self.vpn_connection_peer

    def cleanup(self, context):
        if self.vpn_connection_manager.get(self.vpn_connection_local):
            self.vpn_connection_manager.delete(self.vpn_connection_local)
        if self.vpn_connection_manager.get(self.vpn_connection_peer):
            self.vpn_connection_manager.delete(self.vpn_connection_peer)
        context.vpn_connection_local = None
        context.vpn_connection_peer = None

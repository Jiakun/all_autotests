import random
from novaclient.v2.client import Client as NovaClient
from glanceclient.v2 import Client as GlanceClient
from cinderclient.v2.client import Client as CinderClient
from neutronclient.v2_0.client import Client as NeutronClient
from keystoneclient.v3.client import Client as KeystoneClient
from sedna.openstack.client import SednaClient
from keystoneauth1.session import Session
from keystoneauth1.identity.v3 import Password

from sedna.scenario import Step
from sedna.scenario import Context
from sedna.scenario import Scenario

from sedna.openstack.nova import ServerManager, FlavorManager, KeypairManager
from sedna.openstack.glance import ImageManager, IMAGE_PATH
from sedna.openstack.neutron import NetworkManager, SubnetManager,\
    PortManager, RouterManager, FloatingipManager, SecurityGroupManager,\
    LoadBalancerManager, ListenerManager, LBaaSPoolManager, FirewallRuleManager, \
    FirewallPolicyManager, FirewallManager, LBaaSHealthMonitorManager, \
    LBaaSMemberManager, PortforwardingManager
from sedna.openstack.cinder import VolumeManager
from sedna.openstack.cinder import SnapshotManager
from sedna.openstack.keystone import UserManager
from sedna.openstack.keystone import ProjectManager
from sedna.openstack.keystone import DomainManager

from sedna.openstack.common import Server, Flavor, Image, Subnet,\
    Network, Port, Router, Floatingip, Volume, Snapshot, User, Project,\
    Domain, SecurityGroup, Keypair, LoadBalancer, Listener, LBaaSPool,\
    LBaaSHealthMonitor, LBaaSMember, FirewallRule, FirewallPolicy, \
    Firewall, Portforwarding

from sedna.config import SednaConfigParser, SEDNA_CONF


"""
TODO: Require further integration to node server services
"""


config = SednaConfigParser(SEDNA_CONF)
auth_info = config.get_auth_info()
auth = Password(auth_url=auth_info["auth_url"] + auth_info["auth_version"],
                username=auth_info["admin_username"],
                password=auth_info["admin_password"],
                project_id=auth_info["admin_project_id"],
                user_domain_id=auth_info["admin_domain_id"]
                )
os_session = Session(auth=auth)

EXTERNAL_NETWORK_ID = config.get_external_network_id()


class UserContext(Context):
    def __init__(self, name, os_session, user=None):
        super(UserContext, self).__init__(name, os_session)
        self.user = user


class ProjectContext(Context):
    # before : domain  now:domain=None
    def __init__(self, name, os_session, domain=None, project=None):
        super(ProjectContext, self).__init__(name, os_session)
        self.domain = domain
        self.project = project


class DomainContext(Context):
    def __init__(self, name, os_session, domain=None):
        super(DomainContext, self).__init__(name, os_session)
        self.domain = domain


class VolumeContext(Context):
    def __init__(self, name, os_session, volume=None):
        super(VolumeContext, self).__init__(name, os_session)
        self.volume = volume


class SnapshotContext(Context):
    def __init__(self, name, os_session, volume=None, snapshot=None):
        super(SnapshotContext, self).__init__(name, os_session)
        self.volume = volume
        self.snapshot = snapshot


class NetworkContext(Context):
    def __init__(self, name, os_session, network=None):
        super(NetworkContext, self).__init__(name, os_session)
        self.network = network


class SubnetContext(Context):
    def __init__(self, name, os_session, network=None, subnet=None):
        super(SubnetContext, self).__init__(name, os_session)
        self.network = network
        self.subnet = subnet


class PortContext(Context):
    def __init__(self, name, os_session, subnet=None, port=None):
        super(PortContext, self).__init__(name, os_session)
        self.subnet = subnet
        self.port = port


class RouterContext(Context):
    def __init__(self, name, os_session):
        super(RouterContext, self).__init__(name, os_session)


class FloatingipContext(Context):
    def __init__(self, name, os_session, floatingip_network_id=None):
        super(FloatingipContext, self).__init__(name, os_session)
        self.floating_network_id = floatingip_network_id


class AssociateFloatingipContext(Context):
    def __init__(self, name, os_session, router=None, external_net=None,
                 floatingip=None, network=None, subnet=None, server=None):
        super(AssociateFloatingipContext, self).__init__(name, os_session)
        self.os_session = os_session
        self.neutron_client = NeutronClient(session=os_session)
        self.router = router
        self.external_net = external_net
        self.floatingip = floatingip
        self.network = network
        self.subnet = subnet
        self.server = server


class ImageContext(Context):
    def __init__(self, name, os_session, image=None):
        super(ImageContext, self).__init__(name, os_session)
        self.image = image


class FlavorContext(Context):
    def __init__(self, name, os_session, flavor=None):
        super(FlavorContext, self).__init__(name, os_session)
        self.flavor = flavor


class ServerContext(Context):
    def __init__(self, name, os_session, image=None, flavor=None,
                 network=None, subnet=None, server=None, volume=None):
        super(ServerContext, self).__init__(name, os_session)
        self.image = image
        self.flavor = flavor
        self.network = network
        self.nics = [{"net-id": network.id}] if network else None
        self.subnet = subnet
        self.server = server
        self.volume = volume


class ServerVolumeContext(Context):
    def __init__(self, name, os_session, image=None, flavor=None,
                 network=None, subnet=None, server=None, volume=None):
        super(ServerVolumeContext, self).__init__(name, os_session)
        self.image = image
        self.flavor = flavor
        self.network = network
        self.nics = [{"net-id": network.id}] if network else None
        self.subnet = subnet
        self.server = server
        self.volume = volume


class SecurityGroupContext(Context):
    def __init__(self, name, os_session, security_group=None):
        super(SecurityGroupContext, self).__init__(name, os_session)
        self.security_group = security_group


class KeypairContext(Context):
    def __init__(self, name, os_session):
        super(KeypairContext, self).__init__(name, os_session)


class LoadBalancerContext(Context):
    def __init__(self, name, os_session, loadbalancer=None, subnet=None):
        super(LoadBalancerContext, self).__init__(name, os_session)
        self.loadbalancer = loadbalancer
        self.subnet = subnet


class LBaaSPoolContext(Context):
    def __init__(self, name, os_session, lbaas_pool=None, loadbalancer=None):
        super(LBaaSPoolContext, self).__init__(name, os_session)
        self.pool = lbaas_pool
        self.loadbalancer = loadbalancer


class ListenerContext(Context):
    def __init__(self, name, os_session, listener=None, loadbalancer=None):
        super(ListenerContext, self).__init__(name, os_session)
        self.listener = listener
        self.loadbalancer = loadbalancer


class LBaaSHealthMonitorContext(Context):
    def __init__(self, name, os_session, lbaas_healthmonitor=None,
                 lbaas_pool=None):
        super(LBaaSHealthMonitorContext, self).__init__(name, os_session)
        self.lbaas_healthmonitor = lbaas_healthmonitor
        self.lbaas_pool = lbaas_pool


class LBaaSMemberContext(Context):
    def __init__(self, name, os_session, lbaas_member=None, lbaas_pool=None,
                 subnets=[], networks=[]):
        super(LBaaSMemberContext, self).__init__(name, os_session)
        self.lbaas_member = lbaas_member
        self.lbaas_pool = lbaas_pool
        self.subnets = subnets
        self.networks = networks


class FirewallRuleContext(Context):
    def __init__(self, name, os_session, firewall_rule=None):
        super(FirewallRuleContext, self).__init__(name, os_session)
        self.firewall_rule = firewall_rule


class FirewallPolicyContext(Context):
    def __init__(self, name, os_session, firewall_rules=[], firewall_policy=None):
        super(FirewallPolicyContext, self).__init__(name, os_session)
        self.firewall_policy = firewall_policy
        self.firewall_rules = firewall_rules


class FirewallContext(Context):
    def __init__(self, name, os_session, router_ids=[], firewall_policy_id=None):
        super(FirewallContext, self).__init__(name, os_session)
        self.firewall_policy_id = firewall_policy_id
        self.router_ids = router_ids
        self.firewall_rules = []


class PortforwardingContext(Context):
    def __init__(self, name, os_session, router_id=None, destination_ip=None,
                 protocol=None, source_port = None, destination_port = None):
        super(PortforwardingContext, self).__init__(name, os_session)
        self.router_id = router_id
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.protocol = protocol
        self.source_port = source_port
        self.neutron_client = NeutronClient(session=os_session)


"""

Step List

"""


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
        expected_cidr = "192.167.167.0/24"
        self.subnet =\
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
        self.router =\
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
    def __init__(self, name):
        super(RouterAddInterfaceStep, self).__init__(name)
        self.router_manager = None

    def execute(self, context):
        self.router_manager = RouterManager(os_client=context.neutron_client)
        self.router_manager.add_interface_router(
            router=context.router, subnet=context.subnet)

    def cleanup(self, context):
        if self.router_manager.get(context.router):
            self.router_manager.remove_interface_router(
                router=context.router, subnet=context.subnet)


class FloatingipCreateStep(Step):
    """The class to contain context variables across floatingip test steps"""
    def __init__(self, name):
        super(FloatingipCreateStep, self).__init__(name)
        self.floatingip_manager = None
        self.floatingip = None

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.floatingip_manager = FloatingipManager(os_client=neutron_client)
        self.floatingip =\
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
        self.loadbalancer =\
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
        self.pool =\
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
        self.listener =\
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
        self.healthmonitor =\
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
        self.member =\
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
    def __init__(self, name, index):
        super(MultipleSubnetCreateStep, self).__init__(name)
        self.subnet_manager = None
        self.subnet = None
        self.index = index

    def execute(self, context):
        neutron_client = NeutronClient(session=context.os_session)
        self.subnet_manager = SubnetManager(os_client=neutron_client)
        expected_cidr = "192.167.167." + str(self.index) + "/24"
        self.subnet =\
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
    """The class to contain context variables across firewall rule test steps"""
    def __init__(self, name):
        super(FirewallRuleCreateStep, self).__init__(name)
        self.firewall_rule_manager = None
        self.firewall_rule = None

    def execute(self, context):
        expected_action = "allow"
        expected_protocol = "TCP"
        neutron_client = NeutronClient(session=context.os_session)
        self.firewall_rule_manager = FirewallRuleManager(os_client=neutron_client)
        self.firewall_rule = self.firewall_rule_manager.create(
            FirewallRule(name=self.name, action=expected_action, protocol=expected_protocol))

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
        self.firewall_policy_manager = FirewallPolicyManager(os_client=neutron_client)
        self.firewall_policy =\
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
        self.firewall =\
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
        neutron_client = SednaClient(session=context.os_session)
        expected_destination_ip = "10.0.61.1"
        expected_destination_port = "10011"
        expected_source_port = "10011"
        expected_protocol = "TCP"
        self.portforwarding_manager = PortforwardingManager(os_client=neutron_client)
        self.portforwarding =\
            self.portforwarding_manager.create(
                Portforwarding(name=self.name, router_id=context.router.id,
                               destination_ip=expected_destination_ip,
                               destination_port=expected_destination_port,
                               source_port=expected_source_port, protocol=expected_protocol))

        context.portforwarding = self.portforwarding

    def cleanup(self, context):
        if self.portforwarding_manager.get(self.portforwarding, context.router.id):
            self.portforwarding_manager.delete(self.portforwarding, context.router.id)
            context.portforwarding = None


class ExternalNetworkSettingStep(Step):
    def execute(self, context):
        context.external_net = Network(id=EXTERNAL_NETWORK_ID)

    def cleanup(self, context):
        context.external_net = None


def rand_name(name='', prefix=None):
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

Scenario List

"""


class ResourceCreateScenario(object):
    def __init__(self):
        self.steps = None
        self.scenario = None
        self.context = None
        self.scenario_name = None

    def execute(self, observable, step_observable, is_clean_up=True):
        self.scenario = Scenario(name=self.scenario_name,
                                 steps=self.steps, context=self.context,
                                 observable=observable,
                                 step_observable=step_observable)

        self.scenario.run_steps()
        if is_clean_up:
            self.scenario.run_cleanup_steps()
        return self.scenario.get_status()


class ServerCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(ServerCreateScenario, self).__init__()
        self.scenario_name = "server create scenario"
        self.context = ServerContext(
            name=rand_name("ServerCreateScenarioTest_server", "sedna"),
            os_session=os_session)
        self.steps = [NetworkCreateStep(
            name=rand_name(
                "ServerCreateScenarioTest_network", "sedna")),
            SubnetCreateStep(
                name=rand_name(
                    "ServerCreateScenarioTest_subnet", "sedna")),
            ImageCreateStep(
                name=rand_name(
                    "ServerCreateScenarioTest_image", "sedna")),
            FlavorCreateStep(
                name=rand_name(
                    "ServerCreateScenarioTest_flavor", "sedna")),
            ServerCreateStep(
                name=self.context.name)]


class ServerAttachVolumeScenario(ResourceCreateScenario):
    def __init__(self):
        super(ServerAttachVolumeScenario, self).__init__()
        self.scenario_name = "server attach volume scenario"
        self.context = ServerVolumeContext(
            name=rand_name(
                "ServerAttachVolumeScenarioTest_volume_attach_server", "sedna"),
            os_session=os_session)
        self.steps = [NetworkCreateStep(
            name=rand_name("ServerAttachVolumeScenarioTest_network", "sedna")),
            SubnetCreateStep(
                name=rand_name("ServerAttachVolumeScenarioTest_subnet", "sedna")),
            ImageCreateStep(
                name=rand_name("ServerAttachVolumeScenarioTest_image", "sedna")),
            FlavorCreateStep(
                name=rand_name("ServerAttachVolumeScenarioTest_flavor", "sedna")),
            VolumeCreateStep(
                name=rand_name("ServerAttachVolumeScenarioTest_volume", "sedna")),
            ServerCreateStep(
                name=rand_name("ServerAttachVolumeScenarioTest_server", "sedna")),
            CreateServerVolumeStep(
                name=self.context.name)]


class ServerRebootScenario(ResourceCreateScenario):
    def __init__(self):
        super(ServerRebootScenario, self).__init__()
        self.scenario_name = "server reboot scenario"
        self.context = ServerVolumeContext(
            name=rand_name("ServerRebootScenarioTest_reboot", "sedna"),
            os_session=os_session)
        self.steps = [NetworkCreateStep(
            name=rand_name("ServerRebootScenarioTest_network", "sedna")),
            SubnetCreateStep(
                name=rand_name(
                    "ServerRebootScenarioTest_subnet", "sedna")),
            ImageCreateStep(
                name=rand_name(
                    "ServerRebootScenarioTest_image", "sedna")),
            FlavorCreateStep(
                name=rand_name(
                    "ServerRebootScenarioTest_flavor", "sedna")),
            ServerCreateStep(
                name=rand_name(
                    "ServerRebootScenarioTest_server", "sedna")),
            ServerRebootStep(
                name=self.context.name)]


class ServerStopAndStartScenario(ResourceCreateScenario):
    def __init__(self):
        super(ServerStopAndStartScenario, self).__init__()
        self.scenario_name = "server reboot scenario"
        self.context = ServerVolumeContext(
            name=rand_name("ServerStopAndStartScenarioTest_reboot", "sedna"),
            os_session=os_session)
        self.steps = [NetworkCreateStep(
            name=rand_name("ServerStopAndStartScenarioTest_network", "sedna")),
            SubnetCreateStep(
                name=rand_name(
                    "ServerStopAndStartScenarioTest_subnet", "sedna")),
            ImageCreateStep(
                name=rand_name(
                    "ServerStopAndStartScenarioTest_image", "sedna")),
            FlavorCreateStep(
                name=rand_name(
                    "ServerStopAndStartScenarioTestt_flavor", "sedna")),
            ServerCreateStep(
                name=rand_name(
                    "ServerStopAndStartScenarioTest_server", "sedna")),
            ServerStopStep(name="ServerStopAndStartScenarioTest_stop"),
            ServerStartStep(name="ServerStopAndStartScenarioTest_start")]


class PortCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(PortCreateScenario, self).__init__()
        self.scenario_name = "port create scenario"
        self.context = PortContext(
            name=rand_name("PortCreateScenarioTest_port", "sedna"),
            os_session=os_session)
        self.steps = [NetworkCreateStep(
            name=rand_name("PortCreateScenarioTest_network",
                           "sedna")), SubnetCreateStep(
                name=rand_name("PortCreateScenarioTest_subnet", "sedna")),
            PortCreateStep(
                name=self.context.name)]


class SnapshotCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(SnapshotCreateScenario, self).__init__()
        self.scenario_name = "snapshot create scenario"
        self.context = SnapshotContext(
            name=rand_name(
                "SnapshotCreateScenarioTest_snapshot", "sedna"),
            os_session=os_session)
        self.steps = [VolumeCreateStep(
            name=rand_name("SnapshotCreateScenarioTest_volume", "sedna")),
            SnapshotCreateStep(
                name=self.context.name)]


class VolumeCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(VolumeCreateScenario, self).__init__()
        self.scenario_name = "volume create scenario"
        self.context = VolumeContext(
            name=rand_name("VolumeCreateScenario_volume", "sedna"),
            os_session=os_session)
        self.steps = [VolumeCreateStep(
            name=self.context.name)]


class UserCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(UserCreateScenario, self).__init__()
        self.scenario_name = "user create scenario"
        self.context = UserContext(
            name=rand_name("UserCreateScenarioTest_user", "sedna"),
            os_session=os_session)
        self.steps = [UserCreateStep(name=self.context.name)]


class DomainCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(DomainCreateScenario, self).__init__()
        self.scenario_name = "domain create scenario"
        self.context = DomainContext(
            name=rand_name(
                "DomainCreateScenarioTest_domain", "sedna"),
            os_session=os_session)
        self.steps = [DomainCreateStep(
            name=self.context.name)]


class ProjectCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(ProjectCreateScenario, self).__init__()
        self.scenario_name = "project create scenario"
        self.context = ProjectContext(
            name=rand_name(
                "ProjectCreateScenarioTest_project", "sedna"),
            os_session=os_session)
        self.steps = [DomainCreateStep(
            name=rand_name("ProjectCreateScenarioTest_domain", "sedna")),
            ProjectCreateStep(
                name=self.context.name)]


class SecurityGroupCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(SecurityGroupCreateScenario, self).__init__()
        self.scenario_name = "security group create scenario"
        self.context = SecurityGroupContext(
            name=rand_name(
                "SecurityGroupScenorioTest_security_group", "sedna"),
            os_session=os_session)
        self.steps = [SecurityGroupCreateStep(
            name=self.context.name
        )]


class AssociateFloatingipScenario(ResourceCreateScenario):
    def __init__(self):
        super(AssociateFloatingipScenario, self).__init__()
        self.scenario_name = "associate floatingip scenario"

        external_net = Network(id=EXTERNAL_NETWORK_ID)

        self.context = \
            AssociateFloatingipContext(
                name=rand_name("AssociateFloatingipTest_associate_floatingip",
                               "sedna"),
                os_session=os_session,
                external_net=external_net)
        self.steps = [NetworkCreateStep(
            name=rand_name("AssociateFloatingipTest_network", "sedna")),
            SubnetCreateStep(
                name=rand_name("AssociateFloatingipTest_subnet", "sedna")),
            ImageCreateStep(
                name=rand_name("AssociateFloatingipTest_image", "sedna")),
            FlavorCreateStep(
                name=rand_name("AssociateFloatingipTest_flavor", "sedna")),
            ServerCreateStep(
                name=rand_name("AssociateFloatingipTest_server", "sedna")),
            RouterCreateStep(
                name=rand_name("AssociateFloatingipTest_router", "sedna")),
            RouterSetGatewayStep(
                name=rand_name(
                    "AssociateFloatingipTest_set_gateway", "sedna")),
            RouterAddInterfaceStep(
                name=rand_name(
                    "AssociateFloatingipTest_add_interface", "sedna")),
            FloatingipCreateStep(
                name=rand_name("AssociateFloatingipTest_floatingip", "sedna")),
            FloatingipAssociateStep(
                name=self.context.name)]


class KeypairCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(KeypairCreateScenario, self).__init__()
        self.scenario_name = "keypair create scenario"
        self.context = KeypairContext(
            name=rand_name("KeypairGroupScenario_keypair", "sedna"),
            os_session=os_session)
        self.steps = [KeypairStep(name=self.context.name)]


class LoadBalancerCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(LoadBalancerCreateScenario, self).__init__()
        self.scenario_name = "loadbalancer create scenario"
        self.context = LoadBalancerContext(
            name=rand_name(
                "LoadBalancerCreateScenarioTest_loadbalancer", "sedna"),
            os_session=os_session)
        self.steps = [
            NetworkCreateStep(
                name=rand_name(
                    "LoadBalancerCreateScenarioTest_network", "sedna")),
            SubnetCreateStep(
                name=rand_name(
                    "LoadBalancerCreateScenarioTest_subnet", "sedna")),
            LoadBalancerCreateStep(
                name=self.context.name
            )]


class LBaaSPoolCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(LBaaSPoolCreateScenario, self).__init__()
        self.scenario_name = "lbaas pool create scenario"
        self.context = LBaaSPoolContext(
            name=rand_name(
                "LBaaSPoolCreateScenarioTest_pool", "sedna"),
            os_session=os_session)
        self.steps = [
            NetworkCreateStep(
                name=rand_name(
                    "LBaaSPoolCreateScenarioTest_network", "sedna")),
            SubnetCreateStep(
                name=rand_name("LBaaSPoolCreateScenarioTest_subnet", "sedna")),
            LoadBalancerCreateStep(
                name=rand_name(
                    "LBaaSPoolCreateScenarioTest_loadbalancer", "sedna")),
            LBaaSPoolCreateStep(
                name=self.context.name
            )]


class ListenerCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(ListenerCreateScenario, self).__init__()
        self.scenario_name = "listener create scenario"
        self.context = ListenerContext(
            name=rand_name(
                "ListenerCreateScenarioTest_listener", "sedna"),
            os_session=os_session)
        self.steps = [
            NetworkCreateStep(
                name=rand_name("ListenerCreateScenarioTest_network", "sedna")),
            SubnetCreateStep(
                name=rand_name("ListenerCreateScenarioTest_subnet", "sedna")),
            LoadBalancerCreateStep(
                name=rand_name(
                    "ListenerCreateScenarioTest_loadbalancer", "sedna")),
            ListenerCreateStep(
                name=self.context.name
            )]


class LBaaSHealthMonitorCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(LBaaSHealthMonitorCreateScenario, self).__init__()
        self.scenario_name = "listener create scenario"
        self.context = LBaaSHealthMonitorContext(
            name=rand_name(
                "LBaaSHealthMonitorCreateScenarioTest_healthmonitor", "sedna"),
            os_session=os_session)
        self.steps = [
            NetworkCreateStep(
                name=rand_name(
                    "LBaaSHealthMonitorCreateScenarioTest_network", "sedna")),
            SubnetCreateStep(
                name=rand_name(
                    "LBaaSHealthMonitorCreateScenarioTest_subnet", "sedna")),
            LoadBalancerCreateStep(
                name=rand_name(
                    "LBaaSHealthMonitorCreateScenarioTest_loadbalancer",
                    "sedna")),
            LBaaSPoolCreateStep(
                name=rand_name(
                    "LBaaSHealthMonitorCreateScenarioTest_pool", "sedna")),
            LBaaSHealthMonitorCreateStep(
                name=self.context.name
            )]


class LBaaSMemberCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(LBaaSMemberCreateScenario, self).__init__()
        self.scenario_name = "listener create scenario"
        self.context = LBaaSMemberContext(
            name=rand_name(
                "LBaaSMemberCreateScenarioTest_member", "sedna"),
            os_session=os_session)
        self.steps = [
            MultipleNetworkCreateStep(
                name=rand_name(
                    "LBaaSMemberCreateScenarioTest_network", "sedna"),
                index=0),
            MultipleSubnetCreateStep(
                name=rand_name(
                    "LBaaSMemberCreateScenarioTest_subnet", "sedna"), index=0),
            LoadBalancerCreateStep(
                name=rand_name(
                    "LBaaSMemberCreateScenarioTest_loadbalancer", "sedna"),
                subnet_array_index=0),
            LBaaSPoolCreateStep(
                name=rand_name("LBaaSMemberCreateScenarioTest_pool", "sedna")),
            MultipleNetworkCreateStep(
                name=rand_name(
                    "LBaaSMemberCreateScenarioTest_network", "sedna"),
                index=1),
            MultipleSubnetCreateStep(
                name=rand_name(
                    "LBaaSMemberCreateScenarioTest_subnet", "sedna"), index=1),
            LBaaSMemberCreateStep(
                name=self.context.name
            )]


class RouterCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(RouterCreateScenario, self).__init__()
        self.scenario_name = "router create scenario"
        self.context = RouterContext(
            name=rand_name("RouterCreateScenarioTest_router", "sedna"),
            os_session=os_session)
        self.steps = [RouterCreateStep(name=self.context.name)]


class FirewallRuleCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(FirewallRuleCreateScenario, self).__init__()
        self.scenario_name = "firewall rule create scenario"
        self.context = FirewallRuleContext(
            name=rand_name("FirewallRuleCreateScenarioTest_firewallrule", "sedna"),
            os_session=os_session)
        self.steps = [FirewallRuleCreateStep(name=self.context.name)]


class FirewallPolicyCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(FirewallPolicyCreateScenario, self).__init__()
        self.scenario_name = "firewall policy create scenario"
        self.context = FirewallPolicyContext(
            name=rand_name("FirewallPolicyCreateScenarioTest_firewallpolicy", "sedna"),
            os_session=os_session)
        self.steps = [
            FirewallRuleCreateStep(
                name=rand_name("FirewallPolicyCreateScenarioTest_firewallrule", "sedna")),
            AppendFirewallRuleStep(
                name="FirewallPolicyCreateScenarioTest_addfirewallrule"),
            FirewallPolicyCreateStep(name=self.context.name)]


class FirewallCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(FirewallCreateScenario, self).__init__()
        self.scenario_name = "firewall create scenario"
        self.context = FirewallContext(
            name=rand_name("FirewallCreateScenario_firewall", "sedna"),
            os_session=os_session)
        self.steps = [
            FirewallRuleCreateStep(
                name=rand_name("FirewallCreateScenario_firewallrule", "sedna")),
            AppendFirewallRuleStep(
                name="FirewallCreateScenarioTest_addfirewallrule"),
            FirewallPolicyCreateStep(
                name=rand_name("FirewallCreateScenario_firewallpolicy", "sedna")),
            RouterCreateStep(
                name=rand_name("FirewallCreateScenarioTest_router", "sedna")),
            FirewallSettingStep(
                name=rand_name("FirewallCreateScenario_firewallsetting", "sedna")),
            FirewallRuleCreateStep(name=self.context.name)]


class FirewallNoRouterCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(FirewallNoRouterCreateScenario, self).__init__()
        self.scenario_name = "firewall no router create scenario"
        self.context = FirewallContext(
            name=rand_name("FirewallNoRouterCreateScenario_firewall", "sedna"),
            os_session=os_session)
        self.steps = [
            FirewallRuleCreateStep(
                name=rand_name("FirewallNoRouterScenario_firewallrule", "sedna")),
            AppendFirewallRuleStep(
                name="FirewallNoRouterCreateScenarioTest_addfirewallrule"),
            FirewallPolicyCreateStep(
                name=rand_name("FirewallNoRouterCreateScenario_firewallpolicy", "sedna")),
            FirewallSettingStep(
                name=rand_name("FirewallNoRouterCreateScenario_firewallsetting", "sedna")),
            FirewallRuleCreateStep(name=self.context.name)]


class PortforwardingCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(PortforwardingCreateScenario, self).__init__()
        self.scenario_name = "portforwarding create scenario"
        self.context = PortforwardingContext(
            name=rand_name("PortforwardingCreateScenarioTest_portforwarding", "sedna"),
            os_session=os_session)
        self.steps = [
            ExternalNetworkSettingStep(
                name=rand_name("PortforwardingCreateScenarioTest_set_external_network", "sedna")),
            RouterCreateStep(
                name=rand_name("PortforwardingCreateScenarioTest_router", "sedna")),
            RouterSetGatewayStep(
                name=rand_name(
                    "PortforwardingCreateScenarioTest__set_gateway", "sedna")),
            PortforwardingCreateStep(name=self.scenario_name)]

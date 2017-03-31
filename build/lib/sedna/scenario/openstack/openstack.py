import random
from novaclient.v2.client import Client as NovaClient
from glanceclient.v2 import Client as GlanceClient
from cinderclient.v2.client import Client as CinderClient
from neutronclient.v2_0.client import Client as NeutronClient
from keystoneclient.v3.client import Client as KeystoneClient
from keystoneauth1.session import Session
from keystoneauth1.identity.v3 import Password

from sedna.scenario import Step
from sedna.scenario import Context
from sedna.scenario import Scenario

from sedna.openstack.nova import ServerManager, FlavorManager, KeypairManager
from sedna.openstack.glance import ImageManager, IMAGE_PATH
from sedna.openstack.neutron import NetworkManager, SubnetManager,\
    PortManager, RouterManager, FloatingipManager, SecurityGroupManager,\
    LoadBalancerManager, ListenerManager, LBaaSPoolManager, \
    LBaaSHealthMonitorManager, LBaaSMemberManager
from sedna.openstack.cinder import VolumeManager
from sedna.openstack.cinder import SnapshotManager
from sedna.openstack.keystone import UserManager
from sedna.openstack.keystone import ProjectManager
from sedna.openstack.keystone import DomainManager

from sedna.openstack.common import Server, Flavor, Image, Subnet,\
    Network, Port, Router, Floatingip, Volume, Snapshot, User, Project,\
    Domain, SecurityGroup, Keypair, LoadBalancer, Listener, LBaaSPool,\
    LBaaSHealthMonitor, LBaaSMember


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

EXTERNAL_NETWORK_ID = "0290502e-591c-49fb-8f20-64d2b7e3cca8"


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
        pass


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
        if (self.subnet_array_index == -1):
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


class ServerCreateScenario(object):

    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        server_context = ServerContext(
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
                name=server_context.name)]
        self.scenario = Scenario(name="server create scenario",
                                 steps=self.steps, context=server_context,
                                 observable=observable)
        self.scenario.execute()


class ServerAttachVolumeScenario(object):

    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        server_context = ServerVolumeContext(
            name=rand_name(
                "ServerCreateScenarioTest_volume_attach_server", "sedna"),
            os_session=os_session)
        self.steps = [NetworkCreateStep(
            name=rand_name("ServerCreateScenarioTest_network", "sedna")),
            SubnetCreateStep(
                name=rand_name("ServerCreateScenarioTest_subnet", "sedna")),
            ImageCreateStep(
                name=rand_name("ServerCreateScenarioTest_image", "sedna")),
            FlavorCreateStep(
                name=rand_name("ServerCreateScenarioTest_flavor", "sedna")),
            VolumeCreateStep(
                name=rand_name("ServerCreateScenarioTest_volume", "sedna")),
            ServerCreateStep(
                name=rand_name("ServerCreateScenarioTest_server", "sedna")),
            CreateServerVolumeStep(
                name=server_context.name)]
        self.scenario = Scenario(name="server attach volume scenario",
                                 steps=self.steps, context=server_context,
                                 observable=observable)
        self.scenario.execute()


class ServerRebootScenario(object):

    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        server_context = ServerVolumeContext(
            name=rand_name("ServerCreateScenarioTest_reboot", "sedna"),
            os_session=os_session)
        self.steps = [NetworkCreateStep(
            name=rand_name("ServerCreateScenarioTest_network", "sedna")),
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
                name=rand_name(
                    "ServerCreateScenarioTest_server", "sedna")),
            ServerRebootStep(
                name=server_context.name)]
        self.scenario = Scenario(name="server reboot scenario",
                                 steps=self.steps, context=server_context,
                                 observable=observable)
        self.scenario.execute()


class PortCreateScenario(object):

    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        port_context = PortContext(
            name=rand_name("PortCreateScenarioTest_port", "sedna"),
            os_session=os_session)
        self.steps = [NetworkCreateStep(
            name=rand_name("PortCreateScenarioTest_network",
                           "sedna")), SubnetCreateStep(
                name=rand_name("PortCreateScenarioTest_subnet", "sedna")),
            PortCreateStep(
                name=port_context.name)]
        self.scenario = Scenario(name="port create scenario",
                                 steps=self.steps, context=port_context,
                                 observable=observable)
        self.scenario.execute()


class SnapshotCreateScenario(object):

    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        snapshot_context = SnapshotContext(
            name=rand_name(
                "SnapshotCreateScenarioTest_snapshot", "sedna"),
            os_session=os_session)

        self.steps = [VolumeCreateStep(
            name=rand_name("SnapshotCreateScenarioTest_volume", "sedna")),
            SnapshotCreateStep(
                name=snapshot_context.name)]

        self.scenario = Scenario(name="snapshot create scenario",
                                 steps=self.steps, context=snapshot_context,
                                 observable=observable)
        self.scenario.execute()


class VolumeCreateScenario(object):
    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        volume_context = VolumeContext(
            name=rand_name("VolumeCreateScenario_volume", "sedna"),
            os_session=os_session)
        self.steps = [VolumeCreateStep(
            name=volume_context.name)]

        self.scenario = Scenario(name="volume create scenario",
                                 steps=self.steps, context=volume_context,
                                 observable=observable)
        self.scenario.execute()


class UserCreateScenario(object):
    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        user_context = UserContext(
            name=rand_name("UserCreateScenarioTest_user", "sedna"),
            os_session=os_session)
        self.steps = [UserCreateStep(name=user_context.name)]
        self.scenario = Scenario(name="user create scenario",
                                 steps=self.steps, context=user_context,
                                 observable=observable)
        self.scenario.execute()


class DomainCreateScenario(object):
    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        domain_context = DomainContext(
            name=rand_name(
                "DomainCreateScenarioTest_domain", "sedna"),
            os_session=os_session)
        self.steps = [DomainCreateStep(
            name=domain_context.name)]

        self.scenario = Scenario(name="domain create scenario",
                                 steps=self.steps, context=domain_context,
                                 observable=observable)
        self.scenario.execute()


class ProjectCreateScenario(object):
    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        project_context = ProjectContext(
            name=rand_name(
                "ProjectCreateScenarioTest_project", "sedna"),
            os_session=os_session)
        self.steps = [DomainCreateStep(
            name=rand_name("DomainCreateScenarioTest_domain", "sedna")),
            ProjectCreateStep(
                name=project_context.name)]
        self.scenario = Scenario(name="project create scenario",
                                 steps=self.steps, context=project_context,
                                 observable=observable)
        self.scenario.execute()


class SecurityGroupCreateScenario(object):
    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        security_context = SecurityGroupContext(
            name=rand_name(
                "SecurityGroupScenorioTest_security_group", "sedna"),
            os_session=os_session)
        self.steps = [SecurityGroupCreateStep(
            name=security_context.name
        )]
        self.scenario = Scenario(name="security group create scenario",
                                 steps=self.steps, context=security_context,
                                 observable=observable)
        self.scenario.execute()


class AssociateFloatingipScenario(object):
    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        external_net = Network(id=EXTERNAL_NETWORK_ID)
        associate_floatingip_context = \
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
                name=associate_floatingip_context.name)]
        self.scenario = \
            Scenario(name="associate floatingip scenario", steps=self.steps,
                     context=associate_floatingip_context,
                     observable=observable)

        self.scenario.execute()


class KeypairCreateScenario(object):
    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        keypair_context = KeypairContext(
            name=rand_name("KeypairGroupScenario_keypair", "sedna"),
            os_session=os_session)
        self.steps = [KeypairStep(name=keypair_context.name)]
        self.scenario = Scenario(name="keypair create scenario",
                                 steps=self.steps, context=keypair_context,
                                 observable=observable)
        self.scenario.execute()


class LoadBalancerCreateScenario(object):
    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        loadbalancer_context = LoadBalancerContext(
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
                name=loadbalancer_context.name
            )]
        self.scenario = Scenario(name="loadbalancer create scenario",
                                 steps=self.steps,
                                 context=loadbalancer_context,
                                 observable=observable)
        self.scenario.execute()


class LBaaSPoolCreateScenario(object):
    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        lbaas_pool_context = LBaaSPoolContext(
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
                name=lbaas_pool_context.name
            )]
        self.scenario = Scenario(name="lbaas pool create scenario",
                                 steps=self.steps, context=lbaas_pool_context,
                                 observable=observable)
        self.scenario.execute()


class ListenerCreateScenario(object):
    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        listener_context = ListenerContext(
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
                name=listener_context.name
            )]
        self.scenario = Scenario(name="listener create scenario",
                                 steps=self.steps, context=listener_context,
                                 observable=observable)
        self.scenario.execute()


class LBaaSHealthMonitorCreateScenario(object):
    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        healthmonitor_context = LBaaSHealthMonitorContext(
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
                name=healthmonitor_context.name
            )]
        self.scenario = Scenario(name="lbaas health monitor create scenario",
                                 steps=self.steps,
                                 context=healthmonitor_context,
                                 observable=observable)
        self.scenario.execute()


class LBaaSMemberCreateScenario(object):
    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        member_context = LBaaSMemberContext(
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
                name=member_context.name
            )]
        self.scenario = Scenario(name="lbaas member create scenario",
                                 steps=self.steps, context=member_context,
                                 observable=observable)
        self.scenario.execute()


class RouterCreateScenario(object):
    def __init__(self):
        self.steps = None
        self.scenario = None

    def execute(self, observable):
        router_context = RouterContext(
            name=rand_name("RouterCreateScenarioTest_router", "sedna"),
            os_session=os_session)
        self.steps = [RouterCreateStep(name=router_context.name)]
        self.scenario = Scenario(name="simple scenario",
                                 steps=self.steps, context=router_context,
                                 observable=observable)
        self.scenario.execute()

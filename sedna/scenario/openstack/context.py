from neutronclient.v2_0.client import Client as NeutronClient
from sedna.openstack.client import SednaClient
from sedna.scenario import Context


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
    def __init__(self, name, os_session, router=None,
                 floatingip=None, network=None, subnet=None, server=None):
        super(AssociateFloatingipContext, self).__init__(name, os_session)
        self.os_session = os_session
        self.neutron_client = NeutronClient(session=os_session)
        self.router = router
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
    def __init__(self, name, os_session, firewall_rules=[],
                 firewall_policy=None):
        super(FirewallPolicyContext, self).__init__(name, os_session)
        self.firewall_policy = firewall_policy
        self.firewall_rules = firewall_rules


class FirewallContext(Context):
    def __init__(self, name, os_session, router_ids=[],
                 firewall_policy_id=None):
        super(FirewallContext, self).__init__(name, os_session)
        self.firewall_policy_id = firewall_policy_id
        self.router_ids = router_ids
        self.firewall_rules = []


class PortforwardingContext(Context):
    def __init__(self, name, os_session, router_id=None, destination_ip=None,
                 protocol=None, source_port=None, destination_port=None):
        super(PortforwardingContext, self).__init__(name, os_session)
        self.router_id = router_id
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.protocol = protocol
        self.source_port = source_port
        self.neutron_client = SednaClient(session=os_session)


class VpnIpsecpolicyContext(Context):
    def __init__(self, name, os_session):
        super(VpnIpsecpolicyContext, self).__init__(name, os_session)


class VpnIkepolicyContext(Context):
    def __init__(self, name, os_session):
        super(VpnIkepolicyContext, self).__init__(name, os_session)


class VpnEndpointGroupContext(Context):
    def __init__(self, name, os_session, type=None, endpoints=[]):
        super(VpnEndpointGroupContext, self).__init__(name, os_session)
        self.type = type
        self.endpoints = endpoints


class VpnServiceContext(Context):
    def __init__(self, name, os_session, router=None, router_id=None):
        super(VpnServiceContext, self).__init__(name, os_session)
        self.neutron_client = NeutronClient(session=os_session)
        self.router = None
        self.router_id = router_id


class VpnIpsecSiteConnectionContext(Context):
    def __init__(self, name, os_session, ikepolicy=None,
                 ipsecpolicy=None, peer_endpoints=[],
                 vpnservices=[], local_endpoints=[],
                 routers=[], subnets=[], networks=[]):
        super(VpnIpsecSiteConnectionContext, self).__init__(name, os_session)
        self.neutron_client = NeutronClient(session=os_session)
        self.ikepolicy = ikepolicy
        self.ipsecpolicy = ipsecpolicy
        self.peer_endpoints = peer_endpoints
        self.vpnservices = vpnservices
        self.local_endpoints = local_endpoints
        self.routers = routers
        self.subnets = subnets
        self.networks = networks

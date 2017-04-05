import random

from keystoneauth1.session import Session
from keystoneauth1.identity.v3 import Password

from sedna.config import SednaConfigParser, SEDNA_CONF

from sedna.scenario import Scenario
from sedna.scenario.openstack.context import ServerContext, \
    FlavorContext, ImageContext, SubnetContext, NetworkContext, \
    PortContext, RouterContext, FloatingipContext, VolumeContext, \
    SnapshotContext, UserContext, ProjectContext, DomainContext, \
    SecurityGroupContext, KeypairContext, LoadBalancerContext, \
    ListenerContext, LBaaSPoolContext, LBaaSHealthMonitorContext, \
    LBaaSMemberContext, FirewallRuleContext, FirewallPolicyContext, \
    FirewallContext, VpnIpsecpolicyContext, VpnIkepolicyContext, \
    VpnEndpointGroupContext, VpnServiceContext, PortforwardingContext, \
    ServerVolumeContext, AssociateFloatingipContext, \
    VpnIpsecSiteConnectionContext
from sedna.scenario.openstack.step import ServerCreateStep, \
    FlavorCreateStep, ImageCreateStep, SubnetCreateStep, \
    NetworkCreateStep, PortCreateStep, RouterCreateStep, \
    FloatingipCreateStep, SnapshotCreateStep, UserCreateStep, \
    VolumeCreateStep, ProjectCreateStep, DomainCreateStep, \
    SecurityGroupCreateStep, KeypairStep, LoadBalancerCreateStep, \
    ListenerCreateStep, LBaaSPoolCreateStep, LBaaSHealthMonitorCreateStep, \
    LBaaSMemberCreateStep, FirewallRuleCreateStep, FirewallPolicyCreateStep, \
    FirewallSettingStep, VpnIpsecpolicyCreateStep, VpnIkepolicyCreateStep, \
    ServerRebootStep, VpnEndpointGroupCreateStep, VpnServiceCreateStep, \
    MultipleNetworkCreateStep, MultipleSubnetCreateStep, \
    FloatingipAssociateStep, RouterSetGatewayStep, RouterAddInterfaceStep, \
    CreateServerVolumeStep, ExternalNetworkSettingStep, \
    PortforwardingCreateStep, ServerStopStep, ServerStartStep, \
    AppendFirewallRuleStep, VpnIpsecSiteConnectionCreateStep, \
    MultiRouterWithGatewayCreateAtOnceStep, MultiVpnServiceCreateAtOnceStep, \
    MultiVpnEndpointsCreateAtOnceStep, FirewallCreateStep


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
                "ServerAttachVolumeScenarioTest_attach_volume", "sedna"),
            os_session=os_session)
        self.steps = [NetworkCreateStep(
            name=rand_name(
                "ServerAttachVolumeScenarioTest_network", "sedna")),
            SubnetCreateStep(
                name=rand_name(
                    "ServerAttachVolumeScenarioTest_subnet", "sedna")),
            ImageCreateStep(
                name=rand_name(
                    "ServerAttachVolumeScenarioTest_image", "sedna")),
            FlavorCreateStep(
                name=rand_name(
                    "ServerAttachVolumeScenarioTest_flavor", "sedna")),
            VolumeCreateStep(
                name=rand_name(
                    "ServerAttachVolumeScenarioTest_volume", "sedna")),
            ServerCreateStep(
                name=rand_name(
                    "ServerAttachVolumeScenarioTest_server", "sedna")),
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
        self.context = \
            AssociateFloatingipContext(
                name=rand_name("AssociateFloatingipTest_associate_floatingip",
                               "sedna"),
                os_session=os_session)
        self.steps = [ExternalNetworkSettingStep(
            name=rand_name("AssociateFloatingipTest_ext_net", "sedna"),
            ext_network_id=EXTERNAL_NETWORK_ID),
            NetworkCreateStep(
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
            name=rand_name(
                "FirewallRuleCreateScenarioTest_firewallrule", "sedna"),
            os_session=os_session)
        self.steps = [FirewallRuleCreateStep(name=self.context.name)]


class FirewallPolicyCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(FirewallPolicyCreateScenario, self).__init__()
        self.scenario_name = "firewall policy create scenario"
        self.context = FirewallPolicyContext(
            name=rand_name(
                "FirewallPolicyCreateScenarioTest_firewallpolicy", "sedna"),
            os_session=os_session)
        self.steps = [
            FirewallRuleCreateStep(
                name=rand_name(
                    "FirewallPolicyCreateScenarioTest_firewallrule", "sedna")),
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
                name=rand_name(
                    "FirewallCreateScenario_firewallrule", "sedna")),
            AppendFirewallRuleStep(
                name="FirewallCreateScenarioTest_addfirewallrule"),
            FirewallPolicyCreateStep(
                name=rand_name(
                    "FirewallCreateScenario_firewallpolicy", "sedna")),
            RouterCreateStep(
                name=rand_name("FirewallCreateScenarioTest_router", "sedna")),
            FirewallSettingStep(
                name=rand_name(
                    "FirewallCreateScenario_firewallsetting", "sedna")),
            FirewallCreateStep(name=self.context.name)]


class FirewallNoRouterCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(FirewallNoRouterCreateScenario, self).__init__()
        self.scenario_name = "firewall no router create scenario"
        self.context = FirewallContext(
            name=rand_name("FirewallNoRouterCreateScenario_firewall", "sedna"),
            os_session=os_session)
        self.steps = [
            FirewallRuleCreateStep(
                name=rand_name(
                    "FirewallNoRouterScenario_firewallrule", "sedna")),
            AppendFirewallRuleStep(
                name="FirewallNoRouterCreateScenarioTest_addfirewallrule"),
            FirewallPolicyCreateStep(
                name=rand_name(
                    "FirewallNoRouterCreateScenario_firewallpolicy", "sedna")),
            FirewallSettingStep(
                name=rand_name(
                    "FirewallNoRouterScenario_firewallsetting", "sedna")),
            FirewallCreateStep(name=self.context.name)]


class PortforwardingCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(PortforwardingCreateScenario, self).__init__()
        self.scenario_name = "portforwarding create scenario"
        self.context = PortforwardingContext(
            name=rand_name(
                "PortforwardingCreateScenarioTest_portforwarding", "sedna"),
            os_session=os_session)
        self.steps = [
            ExternalNetworkSettingStep(
                name=rand_name(
                    "PortforwardingCreateTest_set_external_network", "sedna"),
                ext_network_id=EXTERNAL_NETWORK_ID),
            RouterCreateStep(
                name=rand_name(
                    "PortforwardingCreateScenarioTest_router", "sedna")),
            RouterSetGatewayStep(
                name=rand_name(
                    "PortforwardingCreateScenarioTest_set_gateway", "sedna")),
            PortforwardingCreateStep(name=self.scenario_name)]


class VpnIkepolicyCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(VpnIkepolicyCreateScenario, self).__init__()
        self.scenario_name = "vpn ikepolicy create scenario"
        self.context = VpnIkepolicyContext(
            name=rand_name("IkepolicyCreateScenarioTest_ikepolicy", "sedna"),
            os_session=os_session)
        self.steps = [VpnIkepolicyCreateStep(name=self.scenario_name)]


class VpnIpsecpolicyCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(VpnIpsecpolicyCreateScenario, self).__init__()
        self.scenario_name = "vpn ipsecpolicy create scenario"
        self.context = VpnIkepolicyContext(
            name=rand_name(
                "IpsecpolicyCreateScenarioTest_ipsecpolicy", "sedna"),
            os_session=os_session)
        self.steps = [VpnIpsecpolicyCreateStep(name=self.scenario_name)]


class VpnEndpointGroupCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(VpnEndpointGroupCreateScenario, self).__init__()
        self.scenario_name = "vpn endpoint group create scenario"
        self.context = VpnEndpointGroupContext(
            name=rand_name(
                "EndpointGroupCreateScenarioTest_endpoint", "sedna"),
            os_session=os_session)
        self.steps = [
            VpnEndpointGroupCreateStep(name=self.scenario_name,
                                       type="cidr",
                                       endpoints=["192.168.0.1/24"])]


class VpnServiceCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(VpnServiceCreateScenario, self).__init__()
        self.scenario_name = "vpn service create scenario"
        self.context = VpnServiceContext(
            name=rand_name(
                "VpnServiceCreateScenarioTest_vpnservice", "sedna"),
            os_session=os_session)
        self.steps = [
            ExternalNetworkSettingStep(
                name=rand_name(
                    "VpnServiceCreateTest_set_external_network", "sedna"),
                ext_network_id=EXTERNAL_NETWORK_ID),
            RouterCreateStep(
                name=rand_name(
                    "VpnServiceCreateScenarioTest_router", "sedna")),
            RouterSetGatewayStep(
                name=rand_name(
                    "VpnServiceCreateScenarioTest_set_gateway", "sedna")),
            VpnServiceCreateStep(
                name=self.scenario_name)]


class VpnIpsecSiteConnectionCreateScenario(ResourceCreateScenario):
    def __init__(self):
        super(VpnIpsecSiteConnectionCreateScenario, self).__init__()
        self.scenario_name = "vpn connection create scenario"
        self.context = VpnIpsecSiteConnectionContext(
            name=rand_name(
                "VpnConnectionCreateScenarioTest_connection", "sedna"),
            os_session=os_session)

        self.router_names = self.create_rand_name("router", 2)
        self.endpoint_names = self.create_rand_name("ep", 2)
        self.vpnservice_names = self.create_rand_name("vpnservice", 2)

        self.steps = [
            ExternalNetworkSettingStep(
                name=rand_name(
                    "VpnConnectionCreateTest_set_external_network", "sedna"),
                ext_network_id=EXTERNAL_NETWORK_ID),
            MultipleNetworkCreateStep(
                name=rand_name(
                    "VpnConnectionCreateTest_network_0_", "sedna"),
                index=0),
            MultipleSubnetCreateStep(
                name=rand_name(
                    "VpnConnectionCreateTest_subnet_0_", "sedna"), index=0,
                cidr="192.167.166.11/24"),
            MultipleNetworkCreateStep(
                name=rand_name(
                    "VpnConnectionCreateTest_network_1_", "sedna"),
                index=1),
            MultipleSubnetCreateStep(
                name=rand_name(
                    "VpnConnectionCreateTest_subnet_1_", "sedna"), index=1,
                cidr="192.167.166.12/24"),
            MultiRouterWithGatewayCreateAtOnceStep(
                name="VpnConnectionCreateTest_multi_routers",
                names=self.router_names, number=2),
            RouterAddInterfaceStep(
                name="VpnConnectionCreateTest_Router_0_Subnet_0",
                router_index=0, subnet_index=0),
            RouterAddInterfaceStep(
                name="VpnConnectionCreateTest_Router_1_Subnet_1",
                router_index=1, subnet_index=1),
            MultiVpnEndpointsCreateAtOnceStep(
                name="VpnConnectionCreateTest_multi_endpoints",
                names=self.endpoint_names, number=2),
            MultiVpnServiceCreateAtOnceStep(
                name="VpnConnectionCreateTest_multi_services",
                names=self.vpnservice_names, number=2),
            VpnIpsecpolicyCreateStep(
                name=rand_name(
                    "VpnConnectionCreateTest_ipsecpolicy", "sedna")),
            VpnIkepolicyCreateStep(
                name=rand_name(
                    "VpnConnectionCreateTest_ipsecpolicy", "sedna")),
            VpnIpsecSiteConnectionCreateStep(
                name=self.context.name)]

    @staticmethod
    def create_rand_name(resource_type="", number=2):
        rand_names = []
        for i in range(number):
            rand_names.append(
                rand_name(
                    "VpnConnectionCreateTest_" + resource_type + "_" + str(i) + "_", "sedna"))
        return rand_names

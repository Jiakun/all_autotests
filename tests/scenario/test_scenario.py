from unittest2 import TestCase
import logging
import random
from time import sleep

from keystoneauth1.identity.v3 import Password
from keystoneauth1.session import Session

from sedna.scenario import Scenario, Step, Context, Status, Stage
from sedna.scenario.openstack.step import NetworkCreateStep, \
    SubnetCreateStep, ImageCreateStep, FlavorCreateStep, ServerCreateStep, \
    PortCreateStep,  VolumeCreateStep, SnapshotCreateStep, UserCreateStep, \
    ProjectCreateStep, DomainCreateStep, CreateServerVolumeStep, \
    ServerRebootStep, SecurityGroupCreateStep, RouterCreateStep, \
    RouterSetGatewayStep, RouterAddInterfaceStep, FloatingipCreateStep, \
    FloatingipAssociateStep, KeypairStep, LoadBalancerCreateStep, \
    ListenerCreateStep, LBaaSPoolCreateStep, LBaaSHealthMonitorCreateStep, \
    LBaaSMemberCreateStep, MultipleNetworkCreateStep, \
    FirewallRuleCreateStep, FirewallPolicyCreateStep, FirewallCreateStep, \
    AppendFirewallRuleStep, FirewallSettingStep, PortforwardingCreateStep, \
    ServerStartStep, ServerStopStep, ExternalNetworkSettingStep, \
    VpnIkepolicyCreateStep, VpnIpsecpolicyCreateStep, VpnServiceCreateStep, \
    VpnEndpointGroupCreateStep, MultipleSubnetCreateStep, \
    MultiVpnServiceCreateAtOnceStep, MultiVpnEndpointsCreateAtOnceStep, \
    MultiRouterWithGatewayCreateAtOnceStep, VpnIpsecSiteConnectionCreateStep, \
    PeerVpnConnectionsCreateStep

from sedna.scenario.openstack.context import ServerContext, FlavorContext, \
    ImageContext, SubnetContext,  NetworkContext, PortContext, \
    SnapshotContext, VolumeContext, UserContext, DomainContext, \
    ProjectContext, AssociateFloatingipContext, SecurityGroupContext, \
    ServerVolumeContext, KeypairContext, LoadBalancerContext, ListenerContext,\
    LBaaSPoolContext, LBaaSHealthMonitorContext, LBaaSMemberContext, \
    RouterContext, FirewallRuleContext, FirewallPolicyContext, \
    FirewallContext, PortforwardingContext, VpnIkepolicyContext, \
    VpnEndpointGroupContext, VpnIpsecpolicyContext, VpnServiceContext, \
    VpnIpsecSiteConnectionContext, FloatingipContext

from sedna.scenario.openstack.openstack import ServerCreateScenario, \
    ServerAttachVolumeScenario, ServerRebootScenario, \
    PortCreateScenario, SnapshotCreateScenario, VolumeCreateScenario, \
    UserCreateScenario, DomainCreateScenario, ProjectCreateScenario, \
    SecurityGroupCreateScenario, AssociateFloatingipScenario, \
    KeypairCreateScenario, LoadBalancerCreateScenario,\
    ListenerCreateScenario, LBaaSPoolCreateScenario, \
    LBaaSHealthMonitorCreateScenario, LBaaSMemberCreateScenario, \
    RouterCreateScenario, FirewallRuleCreateScenario, \
    FirewallCreateScenario, FirewallNoRouterCreateScenario, \
    PortforwardingCreateScenario, ServerStopAndStartScenario, \
    VpnIkepolicyCreateScenario, VpnIpsecpolicyCreateScenario, \
    VpnEndpointGroupCreateScenario, VpnServiceCreateScenario, \
    FirewallPolicyCreateScenario, VpnIpsecSiteConnectionCreateScenario

from sedna.openstack.common import Network

from sedna.observer import Observable, LoggerObserver, ObserverInfoType

from random import randint

logging.basicConfig()
LOG = logging.getLogger("sedna.scenario")

# 12.12
auth_url = "http://lb.12.ha.polex.io:35357/"
admin_username = "admin"
admin_password = "87fcde29a1f42e4e2d3179b3"
admin_project_id = "7d5dff05fcd9425b95a9751cef1a39db"
admin_domain_id = "default"

"""
auth_url = "http://lb.63.qa.polex.in:35357/"
admin_username = "admin"
admin_password = "cb158f63cb2a0a81c798d214"
admin_project_id = "e910148a98ff473b98ff563c510b3f22"
admin_domain_id = "default"
"""
# region = "RegionOne"

# EXTERNAL_NETWORK_ID = "0290502e-591c-49fb-8f20-64d2b7e3cca8"
# 12.12
EXTERNAL_NETWORK_ID = "5e3f8d37-5b44-4ca9-8499-322f74f6d5b4"

auth = Password(auth_url=auth_url + "v3",
                username=admin_username,
                password=admin_password,
                project_id=admin_project_id,
                user_domain_id=admin_domain_id
                )

os_session = Session(auth=auth)


class StepsTest(TestCase):
    """step test process test"""
    def setUp(self):
        mocked_observer = _MockedObserver()
        self.observable = Observable()
        self.observable.register_observer(mocked_observer)

        self.step_observable = Observable()
        self.observable.register_observer(mocked_observer)

    def test_simple_scenario(self):
        """all steps succeed"""

        context = DummyContext(name="&&test_cleanup&&",
                               os_session=os_session)
        steps = [DummyStep(), DummyStep()]
        scenario = Scenario(name="simple scenario",
                            steps=steps, context=context,
                            observable=self.observable,
                            step_observable=self.step_observable)

        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_partial_execution_failure(self):
        """a step in the middle of the process fails to execute"""

        context = DummyContext(name="&&test_partail_failure&&",
                               os_session=os_session)
        steps = [DummyStep(), DummyFailureStep(), DummyStep()]
        scenario = Scenario(name="partial failure scenario",
                            steps=steps, context=context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        scenario.execute()

        self.assertStageStatus(steps[0], Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(steps[1], Stage.FINISHED, Status.FAILED)
        self.assertStageStatus(steps[2], Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.FAILED)

        self.assertIsNotNone(steps[1].execution_error_info.error)
        self.assertIsNotNone(steps[1].execution_error_info.traceback)

    def test_cleanup_failure(self):
        """a step in the middle of the process fails to cleanup"""

        context = DummyContext(name="&&test_cleanup_failure&&",
                               os_session=os_session)
        steps = [DummyStep(), DummyCleanupFailureStep(), DummyStep()]
        scenario = Scenario(name="cleanup failure scenario",
                            steps=steps, context=context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        scenario.execute()

        self.assertStageStatus(steps[0], Stage.EXECUTED, Status.SUCCEEDED)
        self.assertStageStatus(steps[1], Stage.CLEANING_UP, Status.FAILED)
        self.assertStageStatus(steps[2], Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.FAILED)

        self.assertIsNotNone(steps[1].cleanup_error_info.error)
        self.assertIsNotNone(steps[1].cleanup_error_info.traceback)

    def assertSteps(self, steps, expected_stage, expected_status):
        for step in steps:
            self.assertIs(expected_status, step.status)
            self.assertIs(expected_stage, step.stage)

    def assertStageStatus(self, target, expected_stage, expected_status):
        self.assertIs(expected_status, target.status)
        self.assertIs(expected_stage, target.stage)

    def runSteps(self, steps, scenario):
        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_server_create_positive(self):
        server_context = ServerContext(
            name=rand_name("ServerCreateScenarioTest_server", "sedna"),
            os_session=os_session)
        steps = [NetworkCreateStep(
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
        scenario = Scenario(name="server create scenario",
                            steps=steps, context=server_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_server_create_negative(self):
        pass

    def test_server_suspend_volume(self):
        server_context = ServerVolumeContext(
            name=rand_name(
                "ServerCreateScenarioTest_volume_attach_server", "sedna"),
            os_session=os_session)
        steps = [NetworkCreateStep(
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
            VolumeCreateStep(
                name=rand_name(
                    "ServerCreateScenarioTest_volume", "sedna")),
            ServerCreateStep(
                name=rand_name(
                    "ServerCreateScenarioTest_server", "sedna")),
            CreateServerVolumeStep(
                name=server_context.name)]
        scenario = Scenario(name="server create scenario",
                            steps=steps, context=server_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_server_reboot(self):
        server_context = ServerVolumeContext(
            name=rand_name("ServerRebootScenarioTest_reboot", "sedna"),
            os_session=os_session)
        steps = [NetworkCreateStep(
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
                     name=server_context.name)]
        scenario = Scenario(name="server reboot scenario",
                            steps=steps, context=server_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_server_stop_and_start(self):
        server_context = ServerVolumeContext(
            name=rand_name("ServerRebootScenarioTest_reboot", "sedna"),
            os_session=os_session)
        steps = [NetworkCreateStep(
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
        scenario = Scenario(name="server reboot scenario",
                            steps=steps, context=server_context,
                            observable=self.observable,
                            step_observable=self.step_observable)

        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        sleep(5)

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_port_create(self):
        port_context = PortContext(
            name=rand_name("PortCreateScenarioTest_port", "sedna"),
            os_session=os_session)
        steps = [NetworkCreateStep(
                     name=rand_name("PortCreateScenarioTest_network",
                                    "sedna")),
                 SubnetCreateStep(
                     name=rand_name("PortCreateScenarioTest_subnet", "sedna")),
                 PortCreateStep(
                     name=port_context.name)]
        scenario = Scenario(name="port create scenario",
                            steps=steps, context=port_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_snapshot_create_positive(self):
        snapshot_context = SnapshotContext(
            name=rand_name(
                "SnapshotCreateScenarioTest_snapshot", "sedna"),
            os_session=os_session)

        steps = [VolumeCreateStep(
            name=rand_name("SnapshotCreateScenarioTest_volume", "sedna")),
                 SnapshotCreateStep(
                     name=snapshot_context.name)]

        scenario = Scenario(name="simple scenario",
                            steps=steps, context=snapshot_context,
                            observable=self.observable,
                            step_observable=self.step_observable)

        self.runSteps(steps=steps, scenario=scenario)

    def test_volume_create_positive(self):
        volume_context = VolumeContext(
            name=rand_name("VolumeCreateScenario_volume", "sedna"),
            os_session=os_session)
        steps = [VolumeCreateStep(
            name=volume_context.name)]

        scenario = Scenario(name="simple scenario",
                            steps=steps, context=volume_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_user_create_positive(self):
        user_context = UserContext(
            name=rand_name("UserCreateScenarioTest_user", "sedna"),
            os_session=os_session)
        steps = [UserCreateStep(name=user_context.name)]
        scenario = Scenario(name="simple scenario",
                            steps=steps, context=user_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_router_create_positive(self):
        router_context = RouterContext(
            name=rand_name("RouterCreateScenarioTest_router", "sedna"),
            os_session=os_session)
        steps = [RouterCreateStep(name=router_context.name)]
        scenario = Scenario(name="simple scenario",
                            steps=steps, context=router_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_domain_create_positive(self):
        domain_context = DomainContext(
            name=rand_name(
                "DomainCreateScenarioTest_domain", "sedna"),
            os_session=os_session)
        steps = [DomainCreateStep(
            name=domain_context.name)]

        scenario = Scenario(name="simple scenario",
                            steps=steps, context=domain_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_project_create_positive(self):
        project_context = ProjectContext(
            name=rand_name(
                "ProjectCreateScenarioTest_project", "sedna"),
            os_session=os_session)
        steps = [DomainCreateStep(
            name=rand_name("DomainCreateScenarioTest_domain", "sedna")),
                 ProjectCreateStep(
                     name=project_context.name)]
        scenario = Scenario(name="simple scenario",
                            steps=steps, context=project_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_security_group_create(self):
        security_context = SecurityGroupContext(
            name=rand_name(
                "SecurityGroupScenorioTest_security_group", "sedna"),
            os_session=os_session)
        steps = [SecurityGroupCreateStep(
            name=security_context.name
        )]
        scenario = Scenario(name="simple scenario",
                            steps=steps, context=security_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_keypair_create(self):
        keypair_context = KeypairContext(
            name=rand_name("KeypairGroupScenario_keypair", "sedna"),
            os_session=os_session)
        steps = [KeypairStep(name=keypair_context.name)]
        scenario = Scenario(name="simple scenario",
                            steps=steps, context=keypair_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_associate_floatingip_positive(self):
        associate_floatingip_context = \
            AssociateFloatingipContext(
                name=rand_name("AssociateFloatingipTest_associate_floatingip",
                               "sedna"),
                os_session=os_session)
        steps = [
            ExternalNetworkSettingStep(
                name="AssociateFloatingipTest_ext_net",
                ext_network_id=EXTERNAL_NETWORK_ID),
            NetworkCreateStep(
                name=rand_name(
                    "AssociateFloatingipTest_network", "sedna")),
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
        scenario = \
            Scenario(name="simple scenario", steps=steps,
                     context=associate_floatingip_context,
                     observable=self.observable,
                     step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_loadbalancer_create(self):
        loadbalancer_context = LoadBalancerContext(
            name=rand_name(
                "LoadBalancerCreateScenarioTest_loadbalancer", "sedna"),
            os_session=os_session)
        steps = [NetworkCreateStep(
                     name=rand_name(
                         "LoadBalancerCreateScenarioTest_network", "sedna")),
                 SubnetCreateStep(
                     name=rand_name(
                         "LoadBalancerCreateScenarioTest_subnet", "sedna")),
                 LoadBalancerCreateStep(
                     name=loadbalancer_context.name)]
        scenario = Scenario("loadbalancer create scenario", steps,
                            context=loadbalancer_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_lbaas_pool_create(self):
        lbaas_pool_context = LBaaSPoolContext(
            name=rand_name("LBaaSPoolCreateScenarioTest_pool", "sedna"),
            os_session=os_session)
        steps = [NetworkCreateStep(
                     name=rand_name(
                         "LBaaSPoolCreateScenarioTest_network", "sedna")),
                 SubnetCreateStep(
                     name=rand_name(
                         "LBaaSPoolCreateScenarioTest_subnet", "sedna")),
                 LoadBalancerCreateStep(
                     name=rand_name(
                         "LBaaSPoolCreateScenarioTest_loadbalancer", "sedna")),
                 LBaaSPoolCreateStep(
                     name=lbaas_pool_context.name)]
        scenario = Scenario("lbaas pool create scenario", steps,
                            lbaas_pool_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_listener_create(self):
        listener_context = ListenerContext(
            name=rand_name("ListenerCreateScenarioTest_listener", "sedna"),
            os_session=os_session)
        steps = [NetworkCreateStep(
                     name=rand_name(
                         "ListenerCreateScenarioTest_network", "sedna")),
                 SubnetCreateStep(
                     name=rand_name(
                         "ListenerCreateScenarioTest_subnet", "sedna")),
                 LoadBalancerCreateStep(
                     name=rand_name(
                         "ListenerCreateScenarioTest_loadbalancer", "sedna")),
                 ListenerCreateStep(
                     name=listener_context.name)]
        scenario = Scenario("listener create scenario", steps,
                            listener_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_lbaas_healthmonitor_create(self):
        lbaas_healthmonitor_context = LBaaSHealthMonitorContext(
            name=rand_name(
                "LBaaSHealthMonitorCreateScenarioTest_listener", "sedna"),
            os_session=os_session)
        steps = [NetworkCreateStep(
                     name=rand_name(
                         "LBaaSHealthMonitorCreateScenarioTest_network",
                         "sedna")),
                 SubnetCreateStep(
                     name=rand_name(
                         "LBaaSHealthMonitorCreateScenarioTest_subnet",
                         "sedna")),
                 LoadBalancerCreateStep(
                     name=rand_name(
                         "LBaaSHealthMonitorCreateScenarioTest_loadbalancer",
                         "sedna")),
                 LBaaSPoolCreateStep(
                     name=rand_name(
                         "LBaaSHealthMonitorCreateScenarioTest_pool",
                         "sedna")),
                 LBaaSHealthMonitorCreateStep(
                     name=lbaas_healthmonitor_context.name)]
        scenario = Scenario("lbaas health monitor create scenario", steps,
                            lbaas_healthmonitor_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_lbaas_member_create(self):
        lbaas_member_context = LBaaSMemberContext(
            name=rand_name("LBaaSMemberCreateScenarioTest_member", "sedna"),
            os_session=os_session)
        steps = [MultipleNetworkCreateStep(
                     name=rand_name(
                         "LBaaSMemberCreateScenarioTest_network", "sedna"),
                     index=0),
                 MultipleSubnetCreateStep(
                     name=rand_name(
                         "LBaaSMemberCreateScenarioTest_subnet", "sedna"),
                     index=0, cidr="192.167.167.3/24"),
                 LoadBalancerCreateStep(
                     name=rand_name(
                         "LBaaSMemberCreateScenarioTest_loadbalancer",
                         "sedna"), subnet_array_index=0),
                 LBaaSPoolCreateStep(
                     name=rand_name(
                         "LBaaSMemberCreateScenarioTest_pool", "sedna")),
                 MultipleNetworkCreateStep(
                     name=rand_name(
                         "LBaaSMemberCreateScenarioTest_network", "sedna"),
                     index=1),
                 MultipleSubnetCreateStep(
                     name=rand_name(
                         "LBaaSMemberCreateScenarioTest_subnet", "sedna"),
                     index=1, cidr="192.167.167.4/24"),
                 LBaaSMemberCreateStep(
                     name=lbaas_member_context.name)]
        scenario = Scenario("lbaas member create scenario", steps,
                            lbaas_member_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        sleep(5)

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_firewall_rule_create(self):
        firewall_rule_context = FirewallRuleContext(
            name=rand_name(
                "FirewallRuleCreateScenarioTest_firewallrule", "sedna"),
            os_session=os_session)
        steps = [FirewallRuleCreateStep(
                     name=firewall_rule_context.name)]
        scenario = Scenario("firewall rule create scenario", steps,
                            firewall_rule_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_firewall_policy_create(self):
        firewall_policy_context = FirewallPolicyContext(
            name=rand_name(
                "FirewallPolicyCreateScenarioTest_firewallpolicy", "sedna"),
            os_session=os_session)
        steps = [
            FirewallRuleCreateStep(
                name=rand_name(
                    "FirewallPolicyCreateScenarioTest_firewallrule", "sedna")),
            AppendFirewallRuleStep(
                name="FirewallPolicyCreateScenarioTest_addfirewallrule"),
            FirewallPolicyCreateStep(
                name=firewall_policy_context.name)]
        scenario = Scenario("firewall policy create scenario", steps,
                            firewall_policy_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_firewall_create(self):
        firewall_context = FirewallContext(
            name=rand_name("FirewallCreateScenarioTest_firewall", "sedna"),
            os_session=os_session)
        steps = [
            FirewallRuleCreateStep(
                name=rand_name(
                    "FirewallCreateScenarioTest_firewallrule", "sedna")),
            AppendFirewallRuleStep(
                name="FirewallCreateScenarioTest_addfirewallrule"),
            FirewallPolicyCreateStep(
                name=rand_name(
                    "FirewallCreateScenarioTest_firewallpolicy", "sedna")),
            RouterCreateStep(
                name=rand_name(
                    "FirewallCreateScenarioTest_router", "sedna")),
            FirewallSettingStep(
                name=rand_name(
                    "FirewallCreateScenarioTest_firewallsetting", "sedna")),
            FirewallCreateStep(
                name=firewall_context.name)]
        scenario = Scenario("firewall create scenario", steps,
                            firewall_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_firewall_no_router_create(self):
        firewall_context = FirewallContext(
            name=rand_name("FirewallNoRouterCreateTest_firewall", "sedna"),
            os_session=os_session)
        steps = [
            FirewallRuleCreateStep(
                name=rand_name(
                    "FirewallNoRouterCreateTest_firewallrule", "sedna")),
            AppendFirewallRuleStep(
                name="FirewallNoRouterCreateTest_addfirewallrule"),
            FirewallPolicyCreateStep(
                name=rand_name(
                    "FirewallNoRouterCreateTest_firewallpolicy", "sedna")),
            FirewallSettingStep(
                name=rand_name(
                    "FirewallNoRouterCreateTest_firewallsetting", "sedna")),
            FirewallCreateStep(
                name=firewall_context.name)]
        scenario = Scenario("firewall no router create scenario", steps,
                            firewall_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_portforwarding_router_create(self):
        portforwarding_context = PortforwardingContext(
            name=rand_name(
                "PortforwardingCreateTest_portforwarding", "sedna"),
            os_session=os_session)
        steps = [
            ExternalNetworkSettingStep(
                name=rand_name(
                    "PortforwardingCreateTest_set_external_network", "sedna")),
            RouterCreateStep(
                name=rand_name(
                    "PortforwardingCreateTest_router", "sedna")),
            RouterSetGatewayStep(
                name=rand_name(
                    "PortforwardingCreateTest_set_gateway", "sedna")),
            PortforwardingCreateStep(
                name=portforwarding_context.name)]
        scenario = Scenario("portforwarding create scenario", steps,
                            portforwarding_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_vpn_ikepolicy_create(self):
        context = VpnIkepolicyContext(
            name=rand_name(
                "VpnIkepolicyCreateScenarioTest_ikepolicy", "sedna"),
            os_session=os_session)
        steps = [VpnIkepolicyCreateStep(name=context.name)]
        scenario = Scenario("ikepolicy create scenario", steps,
                            context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_vpn_ipsecpolicy_create(self):
        context = VpnIpsecpolicyContext(
            name=rand_name(
                "IpsecpolicyCreateScenarioTest_ipsecpolicy", "sedna"),
            os_session=os_session)
        steps = [VpnIpsecpolicyCreateStep(name=context.name)]
        scenario = Scenario("ipsecpolicy create scenario", steps,
                            context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_vpn_endpoint_group_create(self):
        context = VpnEndpointGroupContext(
            name=rand_name(
                "EndpointCreateScenarioTest_endpoint", "sedna"),
            os_session=os_session)
        steps = [VpnEndpointGroupCreateStep(
            name=context.name, type="cidr", endpoints=["192.168.0.1/24"])]
        scenario = Scenario("endpoint group create scenario", steps,
                            context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_vpn_service_create(self):
        context = VpnServiceContext(
            name=rand_name(
                "VpnServiceCreateScenarioTest_vpnservice", "sedna"),
            os_session=os_session)
        steps = [
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
                name=context.name)]
        scenario = Scenario("vpn service create scenario", steps,
                            context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_vpn_connection_create_scenario(self):
        def create_rand_name(resource_type="", number=2):
            rand_names = []
            for i in range(number):
                rand_names.append(
                    rand_name(
                        "VpnConnectionCreateTest_" +
                        resource_type + "_" + str(i) + "_", "sedna"))
            return rand_names

        context = VpnIpsecSiteConnectionContext(
            name=rand_name(
                "VpnConnectionCreateScenarioTest_connection", "sedna"),
            os_session=os_session)
        router_names = create_rand_name("router", 2)
        endpoint_names = create_rand_name("ep", 2)
        vpnservice_names = create_rand_name("vpnservice", 2)

        steps = [
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
                cidr="192.167.167.10/24"),
            MultipleNetworkCreateStep(
                name=rand_name(
                    "VpnConnectionCreateTest_network_1_", "sedna"),
                index=1),
            MultipleSubnetCreateStep(
                name=rand_name(
                    "VpnConnectionCreateTest_subnet_1_", "sedna"), index=1,
                cidr="192.167.166.10/24"),
            MultiRouterWithGatewayCreateAtOnceStep(
                name="VpnConnectionCreateTest_multi_routers",
                names=router_names, number=2),
            RouterAddInterfaceStep(
                name="VpnConnectionCreateTest_Router_0_Subnet_0",
                router_index=0, subnet_index=0),
            RouterAddInterfaceStep(
                name="VpnConnectionCreateTest_Router_1_Subnet_1",
                router_index=1, subnet_index=1),
            MultiVpnEndpointsCreateAtOnceStep(
                name="VpnConnectionCreateTest_multi_endpoints",
                names=endpoint_names, number=2),
            MultiVpnServiceCreateAtOnceStep(
                name="VpnConnectionCreateTest_multi_services",
                names=vpnservice_names, number=2),
            VpnIpsecpolicyCreateStep(
                name=rand_name(
                    "VpnConnectionCreateTest_ipsecpolicy", "sedna")),
            VpnIkepolicyCreateStep(
                name=rand_name(
                    "VpnConnectionCreateTest_ipsecpolicy", "sedna")),
            VpnIpsecSiteConnectionCreateStep(
                name=context.name)]

        scenario = Scenario("vpn connection create scenario", steps,
                            context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)

    def test_peer_vpn_connections_create_scenario(self):
        def create_rand_name(resource_type="", number=2):
            rand_names = []
            for i in range(number):
                rand_names.append(
                    rand_name(
                        "VpnConnectionCreateTest_" +
                        resource_type + "_" + str(i) + "_", "sedna"))
            return rand_names

        context = VpnIpsecSiteConnectionContext(
            name=rand_name(
                "PeerVpnConnectionCreateScenarioTest_connection", "sedna"),
            os_session=os_session)
        router_names = create_rand_name("router", 2)
        endpoint_names = create_rand_name("ep", 2)
        vpnservice_names = create_rand_name("vpnservice", 2)

        steps = [
            ExternalNetworkSettingStep(
                name=rand_name(
                    "PeerVpnConnectionCreateTest_set_external_network", "sedna"),
                ext_network_id=EXTERNAL_NETWORK_ID),
            MultipleNetworkCreateStep(
                name=rand_name(
                    "PeerVpnConnectionCreateTest_network_0_", "sedna"),
                index=0),
            MultipleSubnetCreateStep(
                name=rand_name(
                    "PeerVpnConnectionCreateTest_subnet_0_", "sedna"), index=0,
                cidr="192.167.167.10/24"),
            MultipleNetworkCreateStep(
                name=rand_name(
                    "PeerVpnConnectionCreateTest_network_1_", "sedna"),
                index=1),
            MultipleSubnetCreateStep(
                name=rand_name(
                    "PeerVpnConnectionCreateTest_subnet_1_", "sedna"), index=1,
                cidr="192.167.166.10/24"),
            MultiRouterWithGatewayCreateAtOnceStep(
                name="PeerVpnConnectionCreateTest_multi_routers",
                names=router_names, number=2),
            RouterAddInterfaceStep(
                name="PeerVpnConnectionCreateTest_Router_0_Subnet_0",
                router_index=0, subnet_index=0),
            RouterAddInterfaceStep(
                name="PeerVpnConnectionCreateTest_Router_1_Subnet_1",
                router_index=1, subnet_index=1),
            MultiVpnEndpointsCreateAtOnceStep(
                name="PeerVpnConnectionCreateTest_multi_endpoints",
                names=endpoint_names, number=2),
            MultiVpnServiceCreateAtOnceStep(
                name="PeerVpnConnectionCreateTest_multi_services",
                names=vpnservice_names, number=2),
            VpnIpsecpolicyCreateStep(
                name=rand_name(
                    "PeerVpnConnectionCreateTest_ipsecpolicy", "sedna")),
            VpnIkepolicyCreateStep(
                name=rand_name(
                    "PeerVpnConnectionCreateTest_ipsecpolicy", "sedna")),
            PeerVpnConnectionsCreateStep(
                name=context.name)]

        scenario = Scenario("peer vpn connections create scenario", steps,
                            context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.runSteps(steps=steps, scenario=scenario)


class _MockedObserver(object):
    def update(self, result):
        return True

    def end(self):
        return True


class ScenariosTest(TestCase):
    """scenario test process test"""

    def setUp(self):
        observer = _MockedObserver()
        self.observable = Observable()
        self.observable.register_observer(observer)
        self.step_observable = Observable()
        self.step_observable.register_observer(observer)
        self.log_observer = LoggerObserver(
            logger=LOG, info_type=ObserverInfoType.SCENARIO_STEP)
        self.step_observable.register_observer(observer)

    def assertSteps(self, steps, expected_stage, expected_status):
        for step in steps:
            self.assertIs(expected_status, step.status)
            self.assertIs(expected_stage, step.stage)

    def assertStageStatus(self, target, expected_stage, expected_status):
        self.assertIs(expected_status, target.status)
        self.assertIs(expected_stage, target.stage)

    def testScenario(self, scenario_class, time=0):
        this_scenario = scenario_class()
        this_scenario.execute(self.observable, self.step_observable)

        sleep(time)

        self.assertSteps(
            this_scenario.steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            this_scenario.scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_create_server_scenario(self):
        self.testScenario(ServerCreateScenario)

    def test_server_attach_volume_scenario(self):
        self.testScenario(ServerAttachVolumeScenario)

    def test_reboot_server_scenario(self):
        self.testScenario(ServerRebootScenario, 5)

    def test_stop_and_start_server_scenario(self):
        self.testScenario(ServerStopAndStartScenario, 5)

    def test_port_create_scenario(self):
        self.testScenario(PortCreateScenario)

    def test_snapshot_create_scenario(self):
        self.testScenario(SnapshotCreateScenario)

    def test_volume_create_scenario(self):
        self.testScenario(VolumeCreateScenario)

    def test_user_create_scenario(self):
        self.testScenario(UserCreateScenario)

    def test_router_create_scenario(self):
        self.testScenario(RouterCreateScenario)

    def test_domain_create_scenario(self):
        self.testScenario(DomainCreateScenario)

    def test_project_create_scenario(self):
        self.testScenario(ProjectCreateScenario)

    def test_security_group_scenario(self):
        self.testScenario(SecurityGroupCreateScenario)

    def test_associate_floatingip_scenario(self):
        self.testScenario(AssociateFloatingipScenario)

    def test_keypair_scenario(self):
        self.testScenario(KeypairCreateScenario)

    def test_loadbalancer_create_scenario(self):
        self.testScenario(LoadBalancerCreateScenario)

    def test_lbaas_pool_create_scenario(self):
        self.testScenario(LBaaSPoolCreateScenario)

    def test_listener_create_scenario(self):
        self.testScenario(ListenerCreateScenario)

    def test_lbaas_healthmonitor_create_scenario(self):
        self.testScenario(LBaaSHealthMonitorCreateScenario)

    def test_lbaas_member_create_scenario(self):
        self.testScenario(LBaaSMemberCreateScenario)

    def test_firewall_rule_create_scenario(self):
        self.testScenario(FirewallRuleCreateScenario)

    def test_firewall_policy_create_scenario(self):
        self.testScenario(FirewallPolicyCreateScenario)

    def test_firewall_create_scenario(self):
        self.testScenario(FirewallCreateScenario)

    def test_firewall_no_router_create_scenario(self):
        self.testScenario(FirewallNoRouterCreateScenario)

    def test_portforwarding_create_scenario(self):
        self.testScenario(PortforwardingCreateScenario)

    def test_vpn_ikepolicy_create_scenario(self):
        self.testScenario(VpnIkepolicyCreateScenario)

    def test_vpn_ipsecpolicy_create_scenario(self):
        self.testScenario(VpnIpsecpolicyCreateScenario)

    def test_vpn_endpoint_group_create_scenario(self):
        self.testScenario(VpnEndpointGroupCreateScenario)

    def test_vpn_service_create_scenario(self):
        self.testScenario(VpnServiceCreateScenario)


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


class DummyStep(Step):

    def __init__(self):
        super(DummyStep, self).__init__("dummy step")

    def execute(self, context):
        pass

    def cleanup(self, context):
        pass


class DummyContext(Context):
    pass


class DummyFailureStep(DummyStep):

    def __init__(self):
        super(DummyStep, self).__init__("Dummy Failure Step")

    def execute(self, context):
        raise Exception("test exception")


class DummyCleanupFailureStep(DummyStep):

    def __init__(self):
        super(DummyStep, self).__init__("Dummy Cleanup Failure Step")

    def cleanup(self, context):
        raise Exception("test cleanup exception")

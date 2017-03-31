from unittest2 import TestCase
import logging
import random
from time import sleep

from keystoneauth1.identity.v3 import Password
from keystoneauth1.session import Session

from sedna.scenario import Scenario, Step, Context, Status, Stage
from sedna.scenario.openstack.openstack import NetworkCreateStep, \
    SubnetCreateStep, ImageCreateStep, FlavorCreateStep, ServerCreateStep, \
    PortCreateStep,  VolumeCreateStep, SnapshotCreateStep, UserCreateStep, \
    ProjectCreateStep, DomainCreateStep, CreateServerVolumeStep, \
    ServerRebootStep, SecurityGroupCreateStep, RouterCreateStep, \
    RouterSetGatewayStep, RouterAddInterfaceStep, FloatingipCreateStep, \
    FloatingipAssociateStep, KeypairStep, LoadBalancerCreateStep, \
    ListenerCreateStep, LBaaSPoolCreateStep, LBaaSHealthMonitorCreateStep, \
    LBaaSMemberCreateStep, MultipleNetworkCreateStep, MultipleSubnetCreateStep, \
    FirewallRuleCreateStep, FirewallPolicyCreateStep, FirewallCreateStep, \
    AppendFirewallRuleStep, FirewallSettingStep, PortforwardingCreateStep, \
    ServerStartStep, ServerStopStep, ExternalNetworkSettingStep

from sedna.scenario.openstack.openstack import ServerContext, FlavorContext, \
    ImageContext, SubnetContext,  NetworkContext, PortContext, \
    SnapshotContext, VolumeContext, UserContext, DomainContext, \
    ProjectContext, AssociateFloatingipContext, SecurityGroupContext, \
    ServerVolumeContext, KeypairContext, LoadBalancerContext, ListenerContext,\
    LBaaSPoolContext, LBaaSHealthMonitorContext, LBaaSMemberContext, \
    RouterContext, FirewallRuleContext, FirewallPolicyContext, \
    FirewallContext, PortforwardingContext

from sedna.scenario.openstack.openstack import ServerCreateScenario, \
    ServerAttachVolumeScenario, ServerRebootScenario, \
    PortCreateScenario, SnapshotCreateScenario, VolumeCreateScenario, \
    UserCreateScenario, DomainCreateScenario, ProjectCreateScenario, \
    SecurityGroupCreateScenario, AssociateFloatingipScenario, \
    KeypairCreateScenario, LoadBalancerCreateScenario,\
    ListenerCreateScenario, LBaaSPoolCreateScenario, \
    LBaaSHealthMonitorCreateScenario, LBaaSMemberCreateScenario, \
    RouterCreateScenario, FirewallRuleCreateScenario, FirewallPolicyCreateScenario, \
    FirewallCreateScenario, FirewallNoRouterCreateScenario, \
    PortforwardingCreateScenario, ServerStopAndStartScenario

from sedna.openstack.common import Network

from sedna.observer import Observable, LoggerObserver, ObserverInfoType

logging.basicConfig()
LOG = logging.getLogger("sedna.scenario")


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

        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_server_create_negative(self):
        pass

    def test_server_suspend_volume(self):
        server_context = ServerVolumeContext(
            name=rand_name(
                "ServerCreateScenarioTest_volume_attach_server", "sedna"),
            os_session=os_session)
        steps = [NetworkCreateStep(
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
        scenario = Scenario(name="server create scenario",
                            steps=steps, context=server_context,
                            observable=self.observable,
                            step_observable=self.step_observable)

        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

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

        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

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
        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

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

        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

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

        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_user_create_positive(self):
        user_context = UserContext(
            name=rand_name("UserCreateScenarioTest_user", "sedna"),
            os_session=os_session)
        steps = [UserCreateStep(name=user_context.name)]
        scenario = Scenario(name="simple scenario",
                            steps=steps, context=user_context,
                            observable=self.observable,
                            step_observable=self.step_observable)

        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_router_create_positive(self):
        router_context = RouterContext(
            name=rand_name("RouterCreateScenarioTest_router", "sedna"),
            os_session=os_session)
        steps = [RouterCreateStep(name=router_context.name)]
        scenario = Scenario(name="simple scenario",
                            steps=steps, context=router_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

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
        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()
        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

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

        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

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

        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_keypair_create(self):
        keypair_context = KeypairContext(
            name=rand_name("KeypairGroupScenario_keypair", "sedna"),
            os_session=os_session)
        steps = [KeypairStep(name=keypair_context.name)]
        scenario = Scenario(name="simple scenario",
                            steps=steps, context=keypair_context,
                            observable=self.observable,
                            step_observable=self.step_observable)

        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_associate_floatingip_positive(self):
        external_net = Network(id=EXTERNAL_NETWORK_ID)
        associate_floatingip_context = \
            AssociateFloatingipContext(
                name=rand_name("AssociateFloatingipTest_associate_floatingip",
                               "sedna"),
                os_session=os_session,
                external_net=external_net)
        steps = [NetworkCreateStep(
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
        scenario = \
            Scenario(name="simple scenario", steps=steps,
                     context=associate_floatingip_context,
                     observable=self.observable,
                     step_observable=self.step_observable)

        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

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
        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

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
        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

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
        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

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
        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

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
                     index=0),
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
                     index=1),
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
            name=rand_name("FirewallRuleCreateScenarioTest_firewallrule", "sedna"),
            os_session=os_session)
        steps = [FirewallRuleCreateStep(
                     name=firewall_rule_context.name)]
        scenario = Scenario("firewall rule create scenario", steps,
                            firewall_rule_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_firewall_policy_create(self):
        firewall_policy_context = FirewallPolicyContext(
            name=rand_name("FirewallPolicyCreateScenarioTest_firewallpolicy", "sedna"),
            os_session=os_session)
        steps = [
            FirewallRuleCreateStep(
                name=rand_name("FirewallPolicyCreateScenarioTest_firewallrule", "sedna")),
            AppendFirewallRuleStep(
                name="FirewallPolicyCreateScenarioTest_addfirewallrule"),
            FirewallPolicyCreateStep(
                name=firewall_policy_context.name)]
        scenario = Scenario("firewall policy create scenario", steps,
                            firewall_policy_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_firewall_create(self):
        firewall_context = FirewallContext(
            name=rand_name("FirewallCreateScenarioTest_firewall", "sedna"),
            os_session=os_session)
        steps = [
            FirewallRuleCreateStep(
                name=rand_name("FirewallCreateScenarioTest_firewallrule", "sedna")),
            AppendFirewallRuleStep(
                name="FirewallCreateScenarioTest_addfirewallrule"),
            FirewallPolicyCreateStep(
                name=rand_name("FirewallCreateScenarioTest_firewallpolicy", "sedna")),
            RouterCreateStep(
                name=rand_name("FirewallCreateScenarioTest_router", "sedna")),
            FirewallSettingStep(
                name=rand_name("FirewallCreateScenarioTest_firewallsetting", "sedna")),
            FirewallCreateStep(
                name=firewall_context.name)]
        scenario = Scenario("firewall create scenario", steps,
                            firewall_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_firewall_no_router_create(self):
        firewall_context = FirewallContext(
            name=rand_name("FirewallNoRouterCreateScenarioTest_firewall", "sedna"),
            os_session=os_session)
        steps = [
            FirewallRuleCreateStep(
                name=rand_name("FirewallNoRouterCreateScenarioTest_firewallrule", "sedna")),
            AppendFirewallRuleStep(
                name="FirewallNoRouterCreateScenarioTest_addfirewallrule"),
            FirewallPolicyCreateStep(
                name=rand_name("FirewallNoRouterCreateScenarioTest_firewallpolicy", "sedna")),
            FirewallSettingStep(
                name=rand_name("FirewallNoRouterCreateScenarioTest_firewallsetting", "sedna")),
            FirewallCreateStep(
                name=firewall_context.name)]
        scenario = Scenario("firewall no router create scenario", steps,
                            firewall_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.execute()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_portforwarding_router_create(self):
        portforwarding_context = PortforwardingContext(
            name=rand_name("PortforwardingCreateScenarioTest_portforwarding", "sedna"),
            os_session=os_session)
        steps = [
            ExternalNetworkSettingStep(
                name=rand_name("PortforwardingCreateScenarioTest_set_external_network", "sedna")),
            RouterCreateStep(
                name=rand_name("PortforwardingCreateScenarioTest_router", "sedna")),
            RouterSetGatewayStep(
                name=rand_name("PortforwardingCreateScenarioTest_set_gateway", "sedna")),
            PortforwardingCreateStep(
                name=portforwarding_context.name)]
        scenario = Scenario("portforwarding create scenario", steps,
                            portforwarding_context,
                            observable=self.observable,
                            step_observable=self.step_observable)
        self.assertSteps(steps, Stage.QUEUED, Status.PENDING)
        self.assertStageStatus(scenario, Stage.QUEUED, Status.PENDING)

        scenario.run_steps()

        self.assertSteps(steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(scenario, Stage.FINISHED, Status.SUCCEEDED)


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

    def test_create_server_scenario(self):
        create_server_scenario = ServerCreateScenario()
        create_server_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            create_server_scenario.steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            create_server_scenario.scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_server_attach_volume_scenario(self):
        server_attach_volume_scenario = ServerAttachVolumeScenario()
        server_attach_volume_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            server_attach_volume_scenario.steps,
            Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            server_attach_volume_scenario.scenario,
            Stage.FINISHED, Status.SUCCEEDED)

    def test_reboot_server_scenario(self):
        reboot_server_scenario = ServerRebootScenario()
        reboot_server_scenario.execute(self.observable, self.step_observable)

        sleep(5)

        self.assertSteps(
            reboot_server_scenario.steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            reboot_server_scenario.scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_stop_and_start_server_scenario(self):
        reboot_server_scenario = ServerStopAndStartScenario()
        reboot_server_scenario.execute(self.observable, self.step_observable)

        sleep(5)

        self.assertSteps(
            reboot_server_scenario.steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            reboot_server_scenario.scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_port_create_scenario(self):
        port_create_scenario = PortCreateScenario()
        port_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            port_create_scenario.steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            port_create_scenario.scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_snapshot_create_scenario(self):
        snapshot_create_scenario = SnapshotCreateScenario()
        snapshot_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            snapshot_create_scenario.steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            snapshot_create_scenario.scenario,
            Stage.FINISHED, Status.SUCCEEDED)

    def test_volume_create_scenario(self):
        volume_create_scenario = VolumeCreateScenario()
        volume_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            volume_create_scenario.steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            volume_create_scenario.scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_user_create_scenario(self):
        test_user_create_scenario = UserCreateScenario()
        test_user_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            test_user_create_scenario.steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            test_user_create_scenario.scenario,
            Stage.FINISHED, Status.SUCCEEDED)

    def test_router_create_scenario(self):
        test_router_create_scenario = RouterCreateScenario()
        test_router_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            test_router_create_scenario.steps,
            Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            test_router_create_scenario.scenario,
            Stage.FINISHED, Status.SUCCEEDED)

    def test_domain_create_scenario(self):
        domain_create_scenario = DomainCreateScenario()
        domain_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            domain_create_scenario.steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            domain_create_scenario.scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_project_create_scenario(self):
        project_create_scenario = ProjectCreateScenario()
        project_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            project_create_scenario.steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            project_create_scenario.scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_security_group_scenario(self):
        security_group_scenario = SecurityGroupCreateScenario()
        security_group_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            security_group_scenario.steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            security_group_scenario.scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_associate_floatingip_scenario(self):
        associate_floatingip_scenario = AssociateFloatingipScenario()
        associate_floatingip_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            associate_floatingip_scenario.steps,
            Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            associate_floatingip_scenario.scenario,
            Stage.FINISHED, Status.SUCCEEDED)

    def test_keypair_scenario(self):
        keypair_scenario = KeypairCreateScenario()
        keypair_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            keypair_scenario.steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            keypair_scenario.scenario, Stage.FINISHED, Status.SUCCEEDED)

    def test_loadbalancer_create_scenario(self):
        loadbalancer_create_scenario = LoadBalancerCreateScenario()
        loadbalancer_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            loadbalancer_create_scenario.steps, Stage.FINISHED,
            Status.SUCCEEDED)
        self.assertStageStatus(
            loadbalancer_create_scenario.scenario, Stage.FINISHED,
            Status.SUCCEEDED)

    def test_lbaas_pool_create_scenario(self):
        lbaas_pool_create_scenario = LBaaSPoolCreateScenario()
        lbaas_pool_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            lbaas_pool_create_scenario.steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            lbaas_pool_create_scenario.scenario, Stage.FINISHED,
            Status.SUCCEEDED)

    def test_listener_create_scenario(self):
        listener_create_scenario = ListenerCreateScenario()
        listener_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            listener_create_scenario.steps, Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            listener_create_scenario.scenario, Stage.FINISHED,
            Status.SUCCEEDED)

    def test_lbaas_healthmonitor_create_scenario(self):
        lbaas_healthmonitor_create_scenario = \
            LBaaSHealthMonitorCreateScenario()
        lbaas_healthmonitor_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            lbaas_healthmonitor_create_scenario.steps,
            Stage.FINISHED, Status.SUCCEEDED)
        self.assertStageStatus(
            lbaas_healthmonitor_create_scenario.scenario,
            Stage.FINISHED, Status.SUCCEEDED)

    def test_lbaas_member_create_scenario(self):
        lbaas_member_create_scenario = LBaaSMemberCreateScenario()
        lbaas_member_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            lbaas_member_create_scenario.steps, Stage.FINISHED,
            Status.SUCCEEDED)
        self.assertStageStatus(
            lbaas_member_create_scenario.scenario, Stage.FINISHED,
            Status.SUCCEEDED)

    def test_firewall_rule_create_scenario(self):
        firewall_rule_create_scenario = FirewallRuleCreateScenario()
        firewall_rule_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            firewall_rule_create_scenario.steps, Stage.FINISHED,
            Status.SUCCEEDED)
        self.assertStageStatus(
            firewall_rule_create_scenario.scenario, Stage.FINISHED,
            Status.SUCCEEDED)

    def test_firewall_policy_create_scenario(self):
        firewall_policy_create_scenario = FirewallPolicyCreateScenario()
        firewall_policy_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            firewall_policy_create_scenario.steps, Stage.FINISHED,
            Status.SUCCEEDED)
        self.assertStageStatus(
            firewall_policy_create_scenario.scenario, Stage.FINISHED,
            Status.SUCCEEDED)

    def test_firewall_create_scenario(self):
        firewall_create_scenario = FirewallCreateScenario()
        firewall_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            firewall_create_scenario.steps, Stage.FINISHED,
            Status.SUCCEEDED)
        self.assertStageStatus(
            firewall_create_scenario.scenario, Stage.FINISHED,
            Status.SUCCEEDED)

    def test_firewall_no_router_create_scenario(self):
        firewall_create_scenario = FirewallNoRouterCreateScenario()
        firewall_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            firewall_create_scenario.steps, Stage.FINISHED,
            Status.SUCCEEDED)
        self.assertStageStatus(
            firewall_create_scenario.scenario, Stage.FINISHED,
            Status.SUCCEEDED)

    def test_portforwarding_create_scenario(self):
        portforwarding_create_scenario = PortforwardingCreateScenario()
        portforwarding_create_scenario.execute(self.observable, self.step_observable)
        self.assertSteps(
            portforwarding_create_scenario.steps, Stage.FINISHED,
            Status.SUCCEEDED)
        self.assertStageStatus(
            portforwarding_create_scenario.scenario, Stage.FINISHED,
            Status.SUCCEEDED)


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

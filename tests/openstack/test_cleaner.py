import logging

from keystoneauth1.identity.v3 import Password
from keystoneauth1.session import Session

from novaclient.v2.client import Client as NovaClient
from glanceclient.v2 import Client as GlanceClient
from cinderclient.v2.client import Client as CinderClient
from neutronclient.v2_0.client import Client as NeutronClient
from keystoneclient.v3.client import Client as KeystoneClient

from sedna.error import NoneReferenceError

from sedna.openstack.nova import ServerManager, FlavorManager, \
    KeypairManager
from tests.openstack.base import ResourceManagerTest
from sedna.openstack.glance import ImageManager, IMAGE_PATH
from sedna.openstack.neutron import NetworkManager, SubnetManager, \
    PortManager, RouterManager, FloatingipManager, LoadBalancerManager, \
    LBaaSPoolManager, ListenerManager, LBaaSHealthMonitorManager, \
    LBaaSMemberManager, SecurityGroupManager, FirewallRuleManager, \
    FirewallPolicyManager, FirewallManager, VpnEndpointGroupManager, \
    VpnIpsecSiteConnectionManager, VpnIkepolicyManager, VpnServiceManager, \
    VpnIpsecpolicyManager
from sedna.openstack.cinder import VolumeManager
from sedna.openstack.cinder import SnapshotManager
from sedna.openstack.keystone import UserManager
from sedna.openstack.keystone import ProjectManager
from sedna.openstack.keystone import DomainManager

from sedna.openstack.common import Server, Flavor, Image, Subnet,\
    Network, Port, Router, Floatingip, Volume, Snapshot, User, \
    Project, Domain


from unittest2 import TestCase
from sedna.openstack.cleaner import TargetResourcesCleaner, ListenerCleaner, \
    LBaaSHealthMonitorCleaner, LBaaSMemberCleaner, PortCleaner, \
    ServerCleaner, ImageCleaner, LBaaSPoolCleaner, SubnetCleaner, \
    LoadBalancerCleaner, RouterCleaner, FloatingipCleaner,\
    NetworkCleaner, KeypairCleaner, FlavorCleaner, SnapshotCleaner, \
    VolumeCleaner, SecurityGroupCleaner, FirewallRuleCleaner, \
    FirewallPolicyCleaner, FirewallCleaner, PortforwardingCleaner, \
    VpnEndpointGroupCleaner, VpnIkepolicyCleaner, VpnServiceCleaner, \
    VpnIpsecpolicyCleaner, VpnIpsecSiteConnectionCleaner

prefix_name = ["sedna"]


logging.basicConfig()


class TargetResourcesCleanerTest(object):
    def __init__(self):
        self.manager = None
        self.cleaner = None
        self.neutron_client = None
        self.nova_client = None
        self.glance_client = None
        self.cinder_client = None

    def set_up(self, manager=None, cleaner=None):
        self.manager = manager
        self.cleaner = cleaner

    def test_cleanup(self):
        # self.cleaner.get_resource_list_with_prefix_name()
        self.cleaner.delete_resources_with_prefix_name()
        result_list = self.cleaner.get_resource_list_with_prefix_name()
        if result_list is not None and len(result_list) > 1:
            logging.info("%s", str(result_list))
        else:
            pass
            # raise Exception(str(result_list))

    def tear_down(self):
        pass

    def _init_openstack_client(self, openstack_client_class):
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
        # region = "RegionOne"
        """
        auth = Password(auth_url=auth_url + "v3",
                        username=admin_username,
                        password=admin_password,
                        project_id=admin_project_id,
                        user_domain_id=admin_domain_id
                        )

        os_session = Session(auth=auth)
        return openstack_client_class(session=os_session)

"""
glance
"""


class ImageCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(ImageCleanerTest, self).__init__(method_name)
        self.glance_client = self._init_openstack_client(GlanceClient)
        self.nova_client = self._init_openstack_client(NovaClient)

    def setUp(self):
        self.set_up(manager=ImageManager(
            glance_client=self.glance_client),
            cleaner=ImageCleaner(prefix_name,
                                 glance_client=self.glance_client,
                                 nova_client=self.nova_client))

"""
Cinder
"""


class VolumeCleanUpTest(TestCase, TargetResourcesCleanerTest):
    # deleting requires long time, not waiting for the final result
    # wrong resource type?
    def __init__(self, method_name="runTest"):
        super(VolumeCleanUpTest, self).__init__(method_name)
        self.cinder_client = self._init_openstack_client(CinderClient)

    def setUp(self):
        self.set_up(manager=VolumeManager(
            cinder_client=self.cinder_client),
            cleaner=VolumeCleaner(prefix_name, self.cinder_client))


class SnapshotCleanerTest(TestCase, TargetResourcesCleanerTest):
    # wrong resource type?
    def __init__(self, method_name="runTest"):
        super(SnapshotCleanerTest, self).__init__(method_name)
        self.cinder_client = self._init_openstack_client(CinderClient)

    def setUp(self):
        self.set_up(manager=SnapshotManager(
            cinder_client=self.cinder_client),
            cleaner=SnapshotCleaner(prefix_name, self.cinder_client))

"""
Nova
"""


class ServerCleanerTest(TestCase, TargetResourcesCleanerTest):
    # wrong resource type
    def __init__(self, method_name="runTest"):
        super(ServerCleanerTest, self).__init__(method_name)
        self.nova_client = self._init_openstack_client(NovaClient)
        self.glance_client = self._init_openstack_client(GlanceClient)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=ServerManager(
            nova_client=self.nova_client,
            glance_client=self.glance_client,
            neutron_client=self.neutron_client),
            cleaner=ServerCleaner(prefix_name,
                                  nova_client=self.nova_client,
                                  glance_client=self.glance_client,
                                  neutron_client=self.neutron_client))


class FlavorCleanerTest(TestCase, TargetResourcesCleanerTest):
    # wrong resource type
    def __init__(self, method_name="runTest"):
        super(FlavorCleanerTest, self).__init__(method_name)
        self.nova_client = self._init_openstack_client(NovaClient)

    def setUp(self):
        self.set_up(manager=FlavorManager(
            os_client=self.nova_client),
            cleaner=FlavorCleaner(prefix_name, self.nova_client))


class KeypairCleanerTest(TestCase, TargetResourcesCleanerTest):
    # wrong resource type
    def __init__(self, method_name="runTest"):
        super(KeypairCleanerTest, self).__init__(method_name)
        self.nova_client = self._init_openstack_client(NovaClient)

    def setUp(self):
        self.set_up(manager=KeypairManager(
            nova_client=self.nova_client),
            cleaner=KeypairCleaner(prefix_name, self.nova_client))

"""
neutron
"""


class NetworkCleanerTest(TestCase, TargetResourcesCleanerTest):
    # subnet is tested in their cases
    def __init__(self, method_name="runTest"):
        super(NetworkCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=NetworkManager(
            os_client=self.neutron_client),
            cleaner=NetworkCleaner(prefix_name, self.neutron_client))


class SubnetCleanerTest(TestCase, TargetResourcesCleanerTest):
    # floatingip, loadbalancer are port are tested in their cases
    def __init__(self, method_name="runTest"):
        super(SubnetCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=SubnetManager(
            os_client=self.neutron_client),
            cleaner=SubnetCleaner(prefix_name, self.neutron_client))


class SecurityGroupCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(SecurityGroupCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=SecurityGroupManager(
            os_client=self.neutron_client),
            cleaner=SecurityGroupCleaner(prefix_name, self.neutron_client))


class PortCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(PortCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=PortManager(
            os_client=self.neutron_client),
            cleaner=PortCleaner(prefix_name, self.neutron_client))

    def test_delete_with_router_ids(self):
        router_manager = RouterManager(self.neutron_client)
        router_list = \
            RouterCleaner(
                prefix_name, self.neutron_client).get_resource_list_with_prefix_name()
        router_ids = []
        for router in router_list:
            router_ids.append(router.id)
        self.cleaner.delete_with_router_ids(router_ids, router_manager)


class FloatingipCleanerTest(TestCase, TargetResourcesCleanerTest):
    # NO 'name' attribute. Delete by status
    def __init__(self, method_name="runTest"):
        super(FloatingipCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=FloatingipManager(
            os_client=self.neutron_client),
            cleaner=FloatingipCleaner(prefix_name, self.neutron_client))


class RouterCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(RouterCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=RouterManager(
            os_client=self.neutron_client),
            cleaner=RouterCleaner(prefix_name, self.neutron_client))

    def test_remove_gateway(self):
        self.cleaner.remove_gateway()

    def test_remove_interface(self):
        self.cleaner.remove_interface()


class ListenerCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(ListenerCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=ListenerManager(
            os_client=self.neutron_client),
            cleaner=ListenerCleaner(prefix_name, self.neutron_client))


class LBaaSHealthMonitorCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(LBaaSHealthMonitorCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=LBaaSHealthMonitorManager(
            os_client=self.neutron_client),
            cleaner=LBaaSHealthMonitorCleaner(
                prefix_name, self.neutron_client))


class LBaaSMemberCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(LBaaSMemberCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=LBaaSMemberManager(
            os_client=self.neutron_client),
            cleaner=LBaaSMemberCleaner(prefix_name, self.neutron_client))

    def test_cleanup(self):
        # this case is included in pool clean up
        pass


class LBaaSPoolCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(LBaaSPoolCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=LBaaSPoolManager(
            os_client=self.neutron_client),
            cleaner=LBaaSPoolCleaner(prefix_name, self.neutron_client))

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

        if len(result_list) > 1:
            print result_list
            logging.info("%s", str(result_list))


class LoadBalancerCleanerTest(TestCase, TargetResourcesCleanerTest):
    # listener and pool is tested in their cases
    def __init__(self, method_name="runTest"):
        super(LoadBalancerCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=LoadBalancerManager(
            os_client=self.neutron_client),
            cleaner=LoadBalancerCleaner(prefix_name, self.neutron_client))


class FirewallRuleCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(FirewallRuleCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=FirewallRuleManager(
            os_client=self.neutron_client),
            cleaner=FirewallRuleCleaner(prefix_name, self.neutron_client))


class FirewallPolicyCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(FirewallPolicyCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=FirewallPolicyManager(
            os_client=self.neutron_client),
            cleaner=FirewallPolicyCleaner(prefix_name, self.neutron_client))


class FirewallCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(FirewallCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=FirewallManager(
            os_client=self.neutron_client),
            cleaner=FirewallCleaner(prefix_name, self.neutron_client))

"""
class PortforwardingCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(PortforwardingCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=PortforwardingManager(
            os_client=self.neutron_client),
            cleaner=PortforwardingCleaner(prefix_name, self.neutron_client))
"""


class VpnIpsecSiteConnectionCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(VpnIpsecSiteConnectionCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=VpnIpsecSiteConnectionManager(
            os_client=self.neutron_client),
            cleaner=VpnIpsecSiteConnectionCleaner(prefix_name, self.neutron_client))


class VpnEndpointGroupCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(VpnEndpointGroupCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=VpnEndpointGroupManager(
            os_client=self.neutron_client),
            cleaner=VpnEndpointGroupCleaner(prefix_name, self.neutron_client))


class VpnIpsecpolicyCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(VpnIpsecpolicyCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=VpnIpsecpolicyManager(
            os_client=self.neutron_client),
            cleaner=VpnIpsecpolicyCleaner(prefix_name, self.neutron_client))


class VpnIkepolicyCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(VpnIkepolicyCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=VpnIkepolicyManager(
            os_client=self.neutron_client),
            cleaner=VpnIkepolicyCleaner(prefix_name, self.neutron_client))


class VpnServiceCleanerTest(TestCase, TargetResourcesCleanerTest):
    def __init__(self, method_name="runTest"):
        super(VpnServiceCleanerTest, self).__init__(method_name)
        self.neutron_client = self._init_openstack_client(NeutronClient)

    def setUp(self):
        self.set_up(manager=VpnServiceManager(
            os_client=self.neutron_client),
            cleaner=VpnServiceCleaner(prefix_name, self.neutron_client))

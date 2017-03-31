from keystoneauth1.identity.v3 import Password
from keystoneauth1.session import Session

from neutronclient.v2_0.client import Client as NeutronClient
from novaclient.v2.client import Client as NovaClient
from glanceclient.v2 import Client as GlanceClient

from sedna.openstack.common import Network, Port, Subnet, Floatingip, \
    Router, Flavor, Image, Server, LoadBalancer, LBaaSPool, Listener, \
    LBaaSHealthMonitor, LBaaSMember
from sedna.openstack.neutron import NetworkManager, PortManager,\
    SubnetManager, FloatingipManager, RouterManager, LoadBalancerManager, \
    LBaaSPoolManager, ListenerManager, LBaaSHealthMonitorManager, \
    LBaaSMemberManager
from sedna.openstack.nova import ServerManager, FlavorManager
from sedna.openstack.glance import ImageManager, IMAGE_PATH
from sedna.config import SednaConfigParser, SEDNA_CONF

PREFIX_NAME = ["sedna-HA-"]


class HAResourceCleaner(object):
    def __init__(self, prefix_name, resource_class, cleaner_class, **kwargs):
        """
        :param resource_class:the resource class name to cleanup
        :param cleaner_class:the cleaner class name
        :param kwargs:
        {'manager_class': ManagerClass_1,
        'openstack_client_class': OpenstackClientClass},
        {'manager_class': ManagerClass_2,
        'openstack_client_class': OpenstackClientClass_2}...
        """
        self.prefix_name = prefix_name
        self.resource_class = resource_class
        self.cleaner_class = cleaner_class
        self.kwargs = kwargs

    def clean(self):
        resource_manager = self.kwargs['manager_class'](
            self._init_openstack_client(self.kwargs['openstack_client_class']))
        resource_cleaner = self.cleaner_class(
            prefix_name=self.prefix_name, resource_manager=resource_manager)
        resource_cleaner.delete_resources_with_prefix_name()

    def _init_openstack_client(self, openstack_client_class):
        config = SednaConfigParser(SEDNA_CONF)
        auth_info = config.get_auth_info()
        auth = Password(auth_url=auth_info["auth_url"] + auth_info["auth_version"],
                        username=auth_info["admin_username"],
                        password=auth_info["admin_password"],
                        project_id=auth_info["admin_project_id"],
                        user_domain_id=auth_info["admin_domain_id"]
                        )
        os_session = Session(auth=auth)

        return openstack_client_class(session=os_session)


# class RouterCleaner(ResourceCleaner):
#     def __init__(self, method_name="runTest"):
#         super(RouterCleaner, self).__init__()
#         self.neutron_client = self._init_openstack_client(NeutronClient)
#
#     def setUp(self):
#         self.set_up(manager=RouterManager(
#             os_client=self.neutron_client),
#             cleaner=RouterCleaner(prefix_name, self.neutron_client))

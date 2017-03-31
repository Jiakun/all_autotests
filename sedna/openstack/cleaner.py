import logging
from sedna.error import NoneReferenceError
from sedna.openstack.glance import Image
from sedna.openstack.neutron import Subnet, Router
from sedna.openstack.nova import ServerManager, FlavorManager, \
    KeypairManager
from sedna.openstack.keystone import ProjectManager, UserManager, \
    DomainManager
from sedna.openstack.cinder import VolumeManager, SnapshotManager
from tests.openstack.base import ResourceManagerTest
from sedna.openstack.glance import ImageManager, IMAGE_PATH
from sedna.openstack.neutron import NetworkManager, SubnetManager, \
    PortManager, RouterManager, FloatingipManager, LoadBalancerManager, \
    LBaaSPoolManager, ListenerManager, LBaaSHealthMonitorManager,\
    LBaaSMemberManager, SecurityGroupManager, FirewallRuleManager, \
    FirewallPolicyManager, FirewallManager, PortforwardingManager, \
    VpnEndpointGroupManager, VpnIpsecSiteConnectionManager, \
    VpnIkepolicyManager, VpnIpsecpolicyManager, VpnServiceManager


class TargetResourcesCleaner(object):
    def __init__(self, resource_manager, prefix_name):
        self.manager = resource_manager
        self.resources_to_delete = []
        self.prefix_name = prefix_name

    def get_resource_list_with_prefix_name(self):
        resource_list_with_prefix_name = []
        resources = self.manager.list()
        for name in self.prefix_name:
            for resource in resources:
                if resource.name is not None and name in resource.name:
                    resource_list_with_prefix_name.append(resource)
                elif name in resource.id:
                    resource_list_with_prefix_name.append(resource)

        return resource_list_with_prefix_name

    def delete_resources_with_prefix_name(self):
        self.resources_to_delete = self.get_resource_list_with_prefix_name()
        for resource in self.resources_to_delete:
            try:
                self.manager.delete(resource)

            except:
                pass
            #     raise Exception("bug")


"""
keystone

TODO: NOT IMPLEMENTED
"""


class UserCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, keystone_client):
        super(UserCleaner, self).__init__(
            UserManager(keystone_client=keystone_client),
            prefix_name)


class ProjectCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, keystone_client):
        super(ProjectCleaner, self).__init__(
            ProjectManager(keystone_client=keystone_client),
            prefix_name)


class DomainCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, keystone_client):
        super(DomainCleaner, self).__init__(
            DomainManager(keystone_client=keystone_client),
            prefix_name)


"""
Glance
"""


class ImageCleaner(TargetResourcesCleaner):
    # delete by Nova Client
    # TODO: delete by Glance Client
    def __init__(self, prefix_name, glance_client, nova_client):
        super(ImageCleaner, self).__init__(
            ImageManager(glance_client=glance_client),
            prefix_name)
        self.nova_client = nova_client

    def get_resource_list_with_prefix_name(self):
        resource_list_with_prefix_name = []
        resources = self.manager.list_by_nova(self.nova_client)
        for name in self.prefix_name:
            for resource in resources:
                if resource.name is not None and name in resource.name:
                    resource_list_with_prefix_name.append(
                        Image(name=resource.name, id=resource.id))
        return resource_list_with_prefix_name


"""
Cinder
"""


class SnapshotCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, cinder_client):
        super(SnapshotCleaner, self).__init__(
            SnapshotManager(cinder_client=cinder_client),
            prefix_name)


class VolumeCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, cinder_client):
        super(VolumeCleaner, self).__init__(
            VolumeManager(cinder_client=cinder_client),
            prefix_name)


"""
Nova
"""


class ServerCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, nova_client, glance_client,
                 neutron_client):
        super(ServerCleaner, self).__init__(
            ServerManager(nova_client=nova_client,
                          glance_client=glance_client,
                          neutron_client=neutron_client),
            prefix_name)


class FlavorCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, nova_client):
        super(FlavorCleaner, self).__init__(
            FlavorManager(os_client=nova_client),
            prefix_name)
        self.server_cleaner = None

    def set(self, server_cleaner):
        self.server_cleaner = server_cleaner

    def delete_resources_with_prefix_name(self):
        if self.server_cleaner is not None:
            self.server_cleaner.delete_resources_with_prefix_name()

        super(FlavorCleaner, self).delete_resources_with_prefix_name()


class KeypairCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, nova_client):
        super(KeypairCleaner, self).__init__(
            KeypairManager(nova_client=nova_client),
            prefix_name)


"""
Neutron
"""


class NetworkCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(NetworkCleaner, self).__init__(
            NetworkManager(os_client=neutron_client),
            prefix_name)
        self.subnet_cleaner = None

    def set(self, subnet_cleaner=None):
        self.subnet_cleaner = subnet_cleaner

    def delete_resources_with_prefix_name(self):
        if self.subnet_cleaner is not None:
            self.subnet_cleaner.delete_resources_with_prefix_name()

        super(NetworkCleaner, self).delete_resources_with_prefix_name()


class SubnetCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(SubnetCleaner, self).__init__(
            SubnetManager(os_client=neutron_client),
            prefix_name)
        self.loadbalancer_cleaner = None
        self.port_cleaner = None
        self.floatingip_cleaner = None

    def set(self, loadbalancer_cleaner=None, port_cleaner=None,
            floatingip_cleaner=None):
        self.loadbalancer_cleaner = loadbalancer_cleaner
        self.port_cleaner = port_cleaner
        self.floatingip_cleaner = floatingip_cleaner

    def delete_resources_with_prefix_name(self):
        if self.loadbalancer_cleaner is not None:
            self.loadbalancer_cleaner.delete_resources_with_prefix_name()

        if self.port_cleaner is not None:
            self.port_cleaner.delete_resources_with_prefix_namee()

        if self.floatingip_cleaner is not None:
            self.floatingip_cleaner.delete_resources_with_prefix_name()

        super(SubnetCleaner, self).delete_resources_with_prefix_name()


class SecurityGroupCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(SecurityGroupCleaner, self).__init__(
            SecurityGroupManager(os_client=neutron_client),
            prefix_name)


class PortCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(PortCleaner, self).__init__(
            PortManager(os_client=neutron_client),
            prefix_name)

    def delete_resources_with_prefix_name(self):
        pass

    def delete_with_router_ids(self, router_ids, router_manager):
        port_list = self.manager.list()
        for port in port_list:
            try:
                if port.device_id in router_ids:
                    router_manager.remove_interface_router(
                        Router(port.device_id), Subnet(port.subnet_id))
            except:
                pass


class FloatingipCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(FloatingipCleaner, self).__init__(
            FloatingipManager(os_client=neutron_client),
            prefix_name)

    def get_resource_list_with_prefix_name(self):
        # list all floatingip with status = 'DOWN'
        resource_list_with_prefix_name = []
        resources = self.manager.list()
        for resource in resources:
            if resource.status == 'DOWN':
                resource_list_with_prefix_name.append(resource)
        return resource_list_with_prefix_name


class RouterCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(RouterCleaner, self).__init__(
            RouterManager(os_client=neutron_client),
            prefix_name)

    def remove_gateway(self):
        router_list = self.get_resource_list_with_prefix_name()
        for router in router_list:
            try:
                self.manager.remove_gateway_router(router)
            except:
                pass

    def remove_interface(self):
        router_list = self.get_resource_list_with_prefix_name()
        for router in router_list:
            try:
                subnet_id = \
                    router.external_gateway_info["external_fixed_ips"][0]["subnet_id"]
                self.manager.remove_interface_router(
                    router, Subnet(id=subnet_id))
            except:
                pass


class ListenerCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(ListenerCleaner, self).__init__(
            ListenerManager(os_client=neutron_client),
            prefix_name)


class LBaaSHealthMonitorCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(LBaaSHealthMonitorCleaner, self).__init__(
            LBaaSHealthMonitorManager(os_client=neutron_client),
            prefix_name)


class LBaaSMemberCleaner(TargetResourcesCleaner):
    # lbaas member requires its pool to be list and deleted
    def __init__(self, prefix_name, neutron_client):
        super(LBaaSMemberCleaner, self).__init__(
            LBaaSMemberManager(os_client=neutron_client),
            prefix_name)
        self.lbaas_pool = None

    def set(self, lbaas_pool=None):
        self.lbaas_pool = lbaas_pool

    def get_resource_list_with_prefix_name(self):
        resource_list_with_prefix_name = []
        resources = self.manager.list(self.lbaas_pool)
        for name in self.prefix_name:
            for resource in resources:
                if name in resource.name:
                    resource_list_with_prefix_name.append(resource)
        return resource_list_with_prefix_name


class LBaaSPoolCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(LBaaSPoolCleaner, self).__init__(
            LBaaSPoolManager(os_client=neutron_client),
            prefix_name)
        self.lbaas_healthmonitor_cleaner = None
        self.lbaas_member_cleaner = None

    def set(self, lbaas_healthmonitor_cleaner=None,
            lbaas_member_cleaner=None):
        self.lbaas_healthmonitor_cleaner = lbaas_healthmonitor_cleaner
        self.lbaas_member_cleaner = lbaas_member_cleaner

    def delete_resources_with_prefix_name(self):
        # delete HealthMonitor and Member first
        # health monitor
        self.resources_to_delete = self.get_resource_list_with_prefix_name()
        if self.lbaas_healthmonitor_cleaner is not None:
            self.lbaas_healthmonitor_cleaner.\
                delete_resources_with_prefix_name()

        for pool in self.resources_to_delete:
            # member
            if self.lbaas_member_cleaner is not None:
                self.lbaas_member_cleaner.set(pool.id)
                self.lbaas_member_cleaner.delete_resources_with_prefix_name()

            try:
                self.manager.delete(pool)
            except:
                pass


class LoadBalancerCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(LoadBalancerCleaner, self).__init__(
            LoadBalancerManager(os_client=neutron_client),
            prefix_name)
        self.lbaas_listener_cleaner = None
        self.lbaas_pool_cleaner = None

    def set(self, lbaas_listener_cleaner=None, lbaas_pool_cleaner=None):
        self.lbaas_listener_cleaner = lbaas_listener_cleaner
        self.lbaas_pool_cleaner = lbaas_pool_cleaner

    def delete_resources_with_prefix_name(self):
        # delete Listener and Pool first
        # listener
        if self.lbaas_listener_cleaner is not None:
            self.lbaas_listener_cleaner.delete_resources_with_prefix_name()
        # pool
        if self.lbaas_pool_cleaner is not None:
            self.lbaas_pool_cleaner.delete_resources_with_prefix_name()

        super(LoadBalancerCleaner, self).delete_resources_with_prefix_name()


class FirewallRuleCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(FirewallRuleCleaner, self).__init__(
            FirewallRuleManager(os_client=neutron_client),
            prefix_name)


class FirewallPolicyCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(FirewallPolicyCleaner, self).__init__(
            FirewallPolicyManager(os_client=neutron_client),
            prefix_name)
        self.firewall_rule_cleaner = None

    def set(self, firewall_rule_cleaner=None):
        self.firewall_rule_cleaner = firewall_rule_cleaner

    def delete_resources_with_prefix_name(self):
        # firewall rule
        if self.firewall_rule_cleaner is not None:
            self.firewall_rule_cleaner.delete_resources_with_prefix_name()
        # firewall policy
        super(FirewallPolicyCleaner, self).delete_resources_with_prefix_name()


class FirewallCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(FirewallCleaner, self).__init__(
            FirewallManager(os_client=neutron_client),
            prefix_name)
        self.firewall_policy_cleaner = None
        self.router_cleaner = None

    def set(self, firewall_policy_cleaner=None, router_cleaner=None):
        self.firewall_policy_cleaner = firewall_policy_cleaner
        self.router_cleaner = router_cleaner

    def delete_resources_with_prefix_name(self):
        # firewall policy
        if self.firewall_policy_cleaner is not None:
            self.firewall_policy_cleaner.delete_resources_with_prefix_name()
        # router
        if self.router_cleaner is not None:
            self.router_cleaner.delete_resources_with_prefix_name()
        # firewall
        super(FirewallCleaner, self).delete_resources_with_prefix_name()


class PortforwardingCleaner(TargetResourcesCleaner):
    # portforwarding requires its router
    def __init__(self, prefix_name, sedna_neutron_client):
        super(PortforwardingCleaner, self).__init__(
            PortforwardingManager(os_client=sedna_neutron_client),
            prefix_name)
        self.router_id = None

    def set(self, router_id=None):
        self.router_id = router_id

    def get_resource_list_with_prefix_name(self):
        resource_list_with_prefix_name = []
        resources = self.manager.list(self.router_id)
        for name in self.prefix_name:
            for resource in resources:
                if name in resource.name:
                    resource_list_with_prefix_name.append(resource)
        return resource_list_with_prefix_name


class VpnIpsecSiteConnectionCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(VpnIpsecSiteConnectionCleaner, self).__init__(
            VpnIpsecSiteConnectionManager(os_client=neutron_client),
            prefix_name)


class VpnEndpointGroupCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(VpnEndpointGroupCleaner, self).__init__(
            VpnEndpointGroupManager(os_client=neutron_client),
            prefix_name)


class VpnIpsecpolicyCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(VpnIpsecpolicyCleaner, self).__init__(
            VpnIpsecpolicyManager(os_client=neutron_client),
            prefix_name)


class VpnIkepolicyCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(VpnIkepolicyCleaner, self).__init__(
            VpnIkepolicyManager(os_client=neutron_client),
            prefix_name)


class VpnServiceCleaner(TargetResourcesCleaner):
    def __init__(self, prefix_name, neutron_client):
        super(VpnServiceCleaner, self).__init__(
            VpnServiceManager(os_client=neutron_client),
            prefix_name)

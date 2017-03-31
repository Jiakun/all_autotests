from neutronclient.common.exceptions import NotFound
from sedna.openstack.common import Network, Port, Subnet, \
    Floatingip, Router, Server, SecurityGroup, LoadBalancer, \
    LBaaSPool, Listener, LBaaSHealthMonitor, LBaaSMember, \
    FirewallRule, FirewallPolicy, Firewall, Portforwarding, \
    VpnIkepolicy, VpnIpsecpolicy, VpnService, VpnEndpointGroup, \
    VpnIpsecSiteConnection
from sedna.error import NoneReferenceError, IllegalStateError

from time import sleep, clock


class NeutronResourceJsonFactory(object):
    def get_created_json(self, resource_name, resource_instance, os_client):
        if resource_name == "network":
            network_json = {resource_name: vars(resource_instance)}
            return os_client.create_network(network_json)

        elif resource_name == "subnet":
            subnet_json = {"subnet": {
                "name": resource_instance.name,
                "network_id": resource_instance.network.id,
                "cidr": resource_instance.cidr,
                "ip_version": resource_instance.ip_version,
            }}
            return os_client.create_subnet(subnet_json)

        elif resource_name == "security_group":
            body_name = {resource_name: {"name": resource_instance.name}}
            return os_client.create_security_group(body_name)

        elif resource_name == "port":
            port_json = {"port": {
                "name": resource_instance.name,
                "network_id": resource_instance.subnet.network.id,
                "fixed_ips": [
                    {"subnet_id": resource_instance.subnet.id},
                ]
            }}
            return os_client.create_port(port_json)

        elif resource_name == "floatingip":
            floatingip_json = {"floatingip": {
                "floating_network_id": resource_instance.external_net.id
            }}

            return os_client.create_floatingip(floatingip_json)

        elif resource_name == "router":
            router_json = {"router": {
                "name": resource_instance.name,
                "admin_state_up": resource_instance.admin_state_up
            }}
            return os_client.create_router(router_json)

        elif resource_name == "loadbalancer":
            loadbalancer_json = {"loadbalancer": {
                "name": resource_instance.name,
                "vip_subnet_id": resource_instance.subnet.id,
                # "provisioning_status": loadbalancer.provisioning_status
            }}
            return os_client.create_loadbalancer(loadbalancer_json)

        elif resource_name == "pool":
            lbaas_pool_json = {"pool": {
                "name": resource_instance.name,
                "lb_algorithm": resource_instance.lb_algorithm,
                "protocol": resource_instance.protocol,
                "loadbalancer_id": resource_instance.loadbalancer.id
            }}
            return os_client.create_lbaas_pool(lbaas_pool_json)
        elif resource_name == "listener":
            listener_json = {"listener": {
                "name": resource_instance.name,
                "protocol_port": resource_instance.protocol_port,
                "protocol": resource_instance.protocol,
                "loadbalancer_id": resource_instance.loadbalancer.id,
            }}
            return os_client.create_listener(listener_json)

        elif resource_name == "healthmonitor":
            lbaas_healthmonitor_json = {"healthmonitor": {
                "name": resource_instance.name,
                "delay": resource_instance.delay,
                "max_retries": resource_instance.max_retries,
                "timeout": resource_instance.timeout,
                "type": resource_instance.type,
                "pool_id": resource_instance.pool.id,
            }}
            return os_client.create_lbaas_healthmonitor(
                lbaas_healthmonitor_json)

        elif resource_name == "firewall_rule":
            firewall_rule_json = {"firewall_rule": {
                "name": resource_instance.name,
                "protocol": resource_instance.protocol,
                "action": resource_instance.action,
            }}
            return os_client.create_firewall_rule(firewall_rule_json)
        elif resource_name == "firewall_policy":
            firewall_rules_ids = []
            if resource_instance.firewall_rules is not None:
                if isinstance(resource_instance.firewall_rules[0], basestring):
                    firewall_rules_ids = resource_instance.endpoints
                else:
                    for firewall_rule in resource_instance.firewall_rules:
                        firewall_rules_ids.append(firewall_rule.id)
            firewall_policy_json = {"firewall_policy": {
                "name": resource_instance.name,
                "firewall_rules": firewall_rules_ids
            }}
            return os_client.create_firewall_policy(firewall_policy_json)
        elif resource_name == "firewall":
            firewall_json = {"firewall": {
                "name": resource_instance.name,
                "router_ids": resource_instance.router_ids,
                "firewall_policy_id": resource_instance.firewall_policy_id
            }}
            return os_client.create_firewall(firewall_json)
        elif resource_name == "ikepolicy":
            ikepolicy_json = {resource_name: vars(resource_instance)}
            return os_client.create_ikepolicy(ikepolicy_json)
        elif resource_name == "ipsecpolicy":
            ipsecpolicy_json = {resource_name: vars(resource_instance)}
            return os_client.create_ipsecpolicy(ipsecpolicy_json)
        elif resource_name == "vpnservice":
            vpnservice_json = {"vpnservice":{
                "name": resource_instance.name,
                "router_id": resource_instance.router_id,
            }}
            return os_client.create_vpnservice(vpnservice_json)
        elif resource_name == "endpoint_group":
            endpoints_ids = []
            if resource_instance.endpoints is not None:
                if isinstance(resource_instance.endpoints[0], basestring):
                    endpoints_ids = resource_instance.endpoints
                else:
                    for endpoint in resource_instance.endpoints:
                        endpoints_ids.append(endpoint.id)
            endpoint_group_json = {"endpoint_group": {
                "name": resource_instance.name,
                "type": resource_instance.type,
                "endpoints": endpoints_ids
            }}
            return os_client.create_endpoint_group(endpoint_group_json)
        elif resource_name == "ipsec_site_connection":
            ipsec_site_connection_json = {"ipsec_site_connection": {
                "name": resource_instance.name,
                "psk": resource_instance.psk,
                "ipsecpolicy_id": resource_instance.ipsecpolicy_id,
                "peer_ep_group_id": resource_instance.peer_ep_group_id,
                "ikepolicy_id": resource_instance.ikepolicy_id,
                "vpnservice_id": resource_instance.vpnservice_id,
                "local_ep_group_id": resource_instance.local_ep_group_id,
                "peer_address": resource_instance.peer_address,
                "peer_id": resource_instance.peer_id
            }}
            return os_client.create_ipsec_site_connection(ipsec_site_connection_json)

    def get_show_json(self, resource_name, os_client, resource_id):
        if resource_name == "network":
            return os_client.show_network(resource_id)
        elif resource_name == "subnet":
            return os_client.show_subnet(resource_id)
        elif resource_name == "security_group":
            return os_client.show_security_group(resource_id)
        elif resource_name == "port":
            return os_client.show_port(resource_id)
        elif resource_name == "floatingip":
            return os_client.show_floatingip(resource_id)
        elif resource_name == "router":
            return os_client.show_router(resource_id)
        elif resource_name == "loadbalancer":
            return os_client.show_loadbalancer(resource_id)
        elif resource_name == "pool":
            return os_client.show_lbaas_pool(resource_id)
        elif resource_name == "listener":
            return os_client.show_listener(resource_id)
        elif resource_name == "healthmonitor":
            return os_client.show_lbaas_healthmonitor(resource_id)
        elif resource_name == "firewall_rule":
            return os_client.show_firewall_rule(resource_id)
        elif resource_name == "firewall_policy":
            return os_client.show_firewall_policy(resource_id)
        elif resource_name == "firewall":
            return os_client.show_firewall(resource_id)
        elif resource_name == "ikepolicy":
            return os_client.show_ikepolicy(resource_id)
        elif resource_name == "ipsecpolicy":
            return os_client.show_ipsecpolicy(resource_id)
        elif resource_name == "vpnservice":
            return os_client.show_vpnservice(resource_id)
        elif resource_name == "endpoint_group":
            return os_client.show_endpoint_group(resource_id)
        elif resource_name == "ipsec_site_connection":
            return os_client.show_ipsec_site_connection(resource_id)

    def get_list_json(self, resource_name, os_client):
        _params = {}
        if resource_name == "network":
            return os_client.list_networks()
        elif resource_name == "subnet":
            return os_client.list_subnets()
        elif resource_name == "security_group":
            return os_client.list_security_groups()
        elif resource_name == "port":
            return os_client.list_ports()
        elif resource_name == "floatingip":
            return os_client.list_floatingips(retrieve_all=True, **_params)
        elif resource_name == "router":
            return os_client.list_routers(retrieve_all=True, **_params)
        elif resource_name == "loadbalancer":
            return os_client.list_loadbalancers(retrieve_all=True, **_params)
        elif resource_name == "pool":
            return os_client.list_lbaas_pools(retrieve_all=True, **_params)
        elif resource_name == "listener":
            return os_client.list_listeners(retrieve_all=True, **_params)
        elif resource_name == "healthmonitor":
            return os_client.list_lbaas_healthmonitors(retrieve_all=True, **_params)
        elif resource_name == "firewall_rule":
            return os_client.list_firewall_rules(retrieve_all=True, **_params)
        elif resource_name == "firewall_policy":
            return os_client.list_firewall_policies(retrieve_all=True, **_params)
        elif resource_name == "firewall":
            return os_client.list_firewalls(retrieve_all=True, **_params)
        elif resource_name == "ikepolicy":
            return os_client.list_ikepolicies(retrieve_all=True, **_params)
        elif resource_name == "ipsecpolicy":
            return os_client.list_ipsecpolicies(retrieve_all=True, **_params)
        elif resource_name == "vpnservice":
            return os_client.list_vpnservices(retrieve_all=True, **_params)
        elif resource_name == "endpoint_group":
            return os_client.list_endpoint_groups(retrieve_all=True, **_params)
        elif resource_name == "ipsec_site_connection":
            return os_client.list_ipsec_site_connections(retrieve_all=True, **_params)

    def get_delete_json(self, resource_name, os_client, resource_id):
        if resource_name == "network":
            return os_client.delete_network(resource_id)
        elif resource_name == "subnet":
            return os_client.delete_subnet(resource_id)
        elif resource_name == "security_group":
            return os_client.delete_security_group(resource_id)
        elif resource_name == "port":
            return os_client.delete_port(resource_id)
        elif resource_name == "floatingip":
            return os_client.delete_floatingip(resource_id)
        elif resource_name == "router":
            return os_client.delete_router(resource_id)
        elif resource_name == "loadbalancer":
            return os_client.delete_loadbalancer(resource_id)
        elif resource_name == "pool":
            return os_client.delete_lbaas_pool(resource_id)
        elif resource_name == "listener":
            return os_client.delete_listener(resource_id)
        elif resource_name == "healthmonitor":
            return os_client.delete_lbaas_healthmonitor(resource_id)
        elif resource_name == "firewall_rule":
            return os_client.delete_firewall_rule(resource_id)
        elif resource_name == "firewall_policy":
            return os_client.delete_firewall_policy(resource_id)
        elif resource_name == "firewall":
            return os_client.delete_firewall(resource_id)
        elif resource_name == "ikepolicy":
            return os_client.delete_ikepolicy(resource_id)
        elif resource_name == "ipsecpolicy":
            return os_client.delete_ipsecpolicy(resource_id)
        elif resource_name == "vpnservice":
            return os_client.delete_vpnservice(resource_id)
        elif resource_name == "endpoint_group":
            return os_client.delete_endpoint_group(resource_id)
        elif resource_name == "ipsec_site_connection":
            return os_client.delete_ipsec_site_connection(resource_id)


class NeutronResourceManager(object):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        if os_client is None:
            raise NoneReferenceError("os_client can't be None")
        self.os_client = os_client

        self.resource_class = None
        self.resource_name = None

        self.expected_status = None
        self.timeout = 60
        self.interval = 5
        self.start_time = None
        self.end_time = None

    def create(self, neutron_resource):
        if neutron_resource is None:
            raise NoneReferenceError("neutron resource to create can't be None")

        if not isinstance(neutron_resource, self.resource_class):
            raise TypeError(
                "neutron resource %s is not %s instance"
                % (neutron_resource, self.resource_class.__name__))
        created_resource_json = NeutronResourceJsonFactory().get_created_json(
            resource_name=self.resource_name,
            resource_instance=neutron_resource,
            os_client=self.os_client)

        self.start_time = clock()
        while not self.check_status(created_resource_json[self.resource_name]["id"]):
            if clock() - self.start_time > self.timeout:
                raise RuntimeError(
                    "Failed to wait for resource %s to reach status %s "
                    "in %s sec"
                    % (self.resource_name, self.expected_status, self.timeout))
            self.wait()
        self.end_time = clock()

        return self._cascaded_build(created_resource_json)

    def get(self, neutron_resource):
        if not neutron_resource:
            raise NoneReferenceError("neutron resource to delete is None!")

        if not isinstance(neutron_resource, self.resource_class):
            raise TypeError("neutron resource %s is not %s instance"
                            % (neutron_resource, self.resource_class.__name__))

        if not hasattr(neutron_resource, "id") or not neutron_resource.id:
            raise ValueError(
                "No id is given in the neutron resource %s" % neutron_resource)
        try:
            resource_body_json = NeutronResourceJsonFactory().get_show_json(
                resource_name=self.resource_name, resource_id=neutron_resource.id,
                os_client=self.os_client)
        except NotFound:
            return None
        return self.resource_class(os_resource=resource_body_json[self.resource_name])

    def list(self):
        resource_json_list = NeutronResourceJsonFactory().get_list_json(
            os_client=self.os_client, resource_name=self.resource_name)
        resources = []
        resources_name = self.resource_name[:-1] + "ies" \
            if self.resource_name[-1] == 'y' else self.resource_name + "s"
        for resource_json in resource_json_list[resources_name]:
            resource = self.resource_class(os_resource=resource_json)
            resources.append(resource)
        return resources

    def delete(self, resource_instance):
        """
        Delete the given resource instance from OpenStack
        :param resource_instance: the resource to delete
        :raise NoneReferenceError: if the input parameter is None, or if there
        is no id in the input parameter
        :raise TypeError: if the input parameter is not the Resource
        """
        if resource_instance is None:
            raise NoneReferenceError("resource instance to delete can't be None")

        if not isinstance(resource_instance, self.resource_class):
            raise TypeError(
                "resource instance %s is not %s instance"
                % (resource_instance, self.resource_class.__name__))

        if not hasattr(resource_instance, "id") or not resource_instance.id:
            raise NoneReferenceError(
                "the id of the resource instance to delete is None. %s"
                % resource_instance)

        self.start_time = clock()
        while not self.check_status(resource_instance.id):
            if clock() - self.start_time > self.timeout:
                raise Exception("Update %s timeout." % self.resource_name)
            self.wait()

        result = NeutronResourceJsonFactory().get_delete_json(
            resource_name=self.resource_name, os_client=self.os_client,
            resource_id=resource_instance.id)

        return result

    def _cascaded_build(self, os_resource_json):
        resource = self.resource_class(
            os_resource=os_resource_json[self.resource_name])
        return resource

    def check_status(self, resource_id):
        return True

    def wait(self):
        sleep(self.interval)


class NetworkManager(NeutronResourceManager):
    """Manager class used to manipulate Network resource"""
    def __init__(self, os_client):
        super(NetworkManager, self).__init__(os_client=os_client)
        self.resource_class = Network
        self.resource_name = "network"


class SecurityGroupManager(NeutronResourceManager):
    """Manager class used to manipulate SecurityGroup resource"""
    def __init__(self, os_client):
        super(SecurityGroupManager, self).__init__(os_client=os_client)
        self.resource_class = SecurityGroup
        self.resource_name = "security_group"


class SubnetManager(NeutronResourceManager):
    """Manager class used to manipulate subnet resource"""
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        super(SubnetManager, self).__init__(os_client=os_client)
        self.resource_class = Subnet
        self.resource_name = "subnet"
        self.network_manager = NetworkManager(self.os_client)

        # TODO: check_status should be replaced later
        self.is_wait = False

    def wait(self):
        sleep(5)
        self.is_wait = True

    def check_status(self, resource_id):
        return self.is_wait

    def _cascaded_build(self, os_subnet_json):
        subnet_json = os_subnet_json["subnet"]
        subnet = Subnet(os_resource=subnet_json)
        subnet.network = Network(subnet_json["network_id"])
        return subnet


class PortManager(NeutronResourceManager):
    """Manager class used to manipulate port resource"""

    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        super(PortManager, self).__init__(os_client=os_client)
        self.resource_class = Port
        self.resource_name = "port"
        self.subnet_manager = SubnetManager(self.os_client)

    def list(self, device=None, network=None):
        """Fetches a list of all ports for a project."""
        # TODO(sy): this function need to be tested
        # Pass filters in "params" argument to do_request
        _params = {}
        if device is not None:
            if not isinstance(device, Server) or isinstance(device, Router):
                raise TypeError(
                    "device %s is not sedna Server or Router instance"
                    % device)
            _params["device_id"] = device.id

        if network is not None:
            if not isinstance(network, Network):
                raise TypeError(
                    "network %s is not sedna Network instance" % network)
            _params["network_id"] = network.id

        ports_json = self.os_client.list_ports(retrieve_all=True, **_params)
        ports = []
        for port_json in ports_json["ports"]:
            port = Port(os_resource=port_json)
            port.subnet = port_json["fixed_ips"][0]["subnet_id"]
            ports.append(port)

        return ports

    def _cascaded_build(self, os_port_json):
        # port_json = os_port_json["port"]
        port = Port(os_resource=os_port_json["port"])
        port.subnet = self.subnet_manager.get(
                Subnet(os_port_json["port"]["fixed_ips"][0]["subnet_id"]))
        return port


class FloatingipManager(NeutronResourceManager):
    """Manager class to manipulate floatingip resource"""
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        super(FloatingipManager, self).__init__(os_client=os_client)
        self.resource_class = Floatingip
        self.resource_name = "floatingip"
        self.subnet_manager = SubnetManager(self.os_client)
        self.port_manager = PortManager(os_client=self.os_client)

    def associate_floatingip(self, floatingip, network, server):
        if not isinstance(floatingip, Floatingip):
            raise TypeError(
                "floatingip %s is not %s instance"
                % (floatingip, Floatingip.__name__))

        if not hasattr(floatingip, "id") or not floatingip.id:
            raise NoneReferenceError(
                "the id of the floatingip to delete is None. %s" % floatingip)

        port_list = self.port_manager.list(
            device=server, network=network)

        if len(port_list) is None:
            raise NoneReferenceError(
                "port in %s and %s to associate can't be None" %
                (server, network))

        if len(port_list) > 1:
            raise NoneReferenceError(
                "port in %s and %s to associate can't be over One" %
                (server, network))

        port = port_list[0]

        if not isinstance(port, Port):
            raise TypeError(
                "port %s is not %s instance"
                % (port, Port.__name__))

        if not hasattr(port, "id") or not port.id:
            raise NoneReferenceError(
                "the id of the port to delete is None. %s" % port)
        body = {"floatingip": {"port_id": port.id}}
        return self.os_client.update_floatingip(
            floatingip=floatingip.id, body=body)

    def disassociate_floatingip(self, floatingip):
        if not isinstance(floatingip, Floatingip):
            raise TypeError(
                "floatingip %s is not %s instance"
                % (floatingip, Floatingip.__name__))

        if not hasattr(floatingip, "id") or not floatingip.id:
            raise NoneReferenceError(
                "the id of the floatingip to delete is None. %s" % floatingip)

        body = {"floatingip": {"port_id": None}}
        return self.os_client.update_floatingip(
            floatingip=floatingip.id, body=body)


class RouterManager(NeutronResourceManager):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Router client
        """
        super(RouterManager, self).__init__(os_client=os_client)
        self.resource_class = Router
        self.resource_name = "router"
        self.subnet_manager = SubnetManager(self.os_client)

    def add_gateway_router(self, router, network):
        """
        First step is get router by id, then add add a gateway in the router
        :param router: the existed router belongs to sedna Router class
        :param network:the subnet instance of the sedna Network class
        :return:
        """
        if not router:
            raise NoneReferenceError("router to add gateway is None!")

        if not isinstance(router, Router):
            raise TypeError("router %s is not %s instance"
                            % (router, Router.__name__))

        if not hasattr(router, "id") or not router.id:
            raise ValueError(
                "No id is given in the router %s" % router)

        if not isinstance(network, Network):
            raise TypeError("network %s is not %s instance"
                            % (network, Network.__name__))

        if not hasattr(network, "id") or not network.id:
            raise ValueError(
                "No id is given in the network %s" % network)

        try:
            router_body_json = \
                self.os_client.show_router(router.id)
        except NotFound:
            return None

        body = {'network_id': network.id}
        return self.os_client.add_gateway_router(
            router=router_body_json["router"]["id"], body=body)

    def add_interface_router(self, router, subnet):
        """
        Adds an internal network interface to the specified router.
        :param router:
        :param subnet:
        :return:
        """
        if not router:
            raise NoneReferenceError("router to add interface is None!")

        if not isinstance(router, Router):
            raise TypeError("router %s is not %s instance"
                            % (router, Router.__name__))

        if not hasattr(router, "id") or not router.id:
            raise ValueError(
                "No id is given in the router %s" % router)

        if not isinstance(subnet, Subnet):
            raise TypeError("subnet %s is not %s instance"
                            % (subnet, Subnet.__name__))

        if not hasattr(subnet, "id") or not subnet.id:
            raise ValueError(
                "No id is given in the subnet %s" % subnet)

        try:
            router_body_json = \
                self.os_client.show_router(router.id)
        except NotFound:
            return None
        body = {'subnet_id': subnet.id}
        return self.os_client.add_interface_router(
            router=router_body_json["router"]["id"], body=body)

    def remove_gateway_router(self, router):
        """
        Removes an external network gateway from the specified router.
        """
        if not router:
            raise NoneReferenceError("router to add interface is None!")

        if not isinstance(router, Router):
            raise TypeError("router %s is not %s instance"
                            % (router, Router.__name__))

        if not hasattr(router, "id") or not router.id:
            raise ValueError(
                "No id is given in the router %s" % router)

        try:
            router_body_json = \
                self.os_client.show_router(router.id)
        except NotFound:
            return None
        return self.os_client.remove_gateway_router(
            router=router_body_json["router"]["id"])

    def remove_interface_router(self, router, subnet):
        """Removes an internal network interface from the specified router."""
        if not router:
            raise NoneReferenceError("router to add interface is None!")

        if not isinstance(router, Router):
            raise TypeError("router %s is not %s instance"
                            % (router, Router.__name__))

        if not hasattr(router, "id") or not router.id:
            raise ValueError(
                "No id is given in the router %s" % router)

        if not isinstance(subnet, Subnet):
            raise TypeError("subnet %s is not %s instance"
                            % (subnet, Subnet.__name__))

        if not hasattr(subnet, "id") or not subnet.id:
            raise ValueError(
                "No id is given in the subnet %s" % subnet)

        try:
            router_body_json = \
                self.os_client.show_router(router.id)
        except NotFound:
            return None
        body = {'subnet_id': subnet.id}
        return self.os_client.remove_interface_router(
            router=router_body_json["router"]["id"], body=body)

    def get_port_list(self, router):
        if router is None:
            raise NoneReferenceError("resource instance to delete can't be None")

        if not isinstance(router, self.resource_class):
            raise TypeError(
                "resource instance %s is not %s instance"
                % (router, self.resource_class.__name__))

        if not hasattr(router, "id") or not router.id:
            raise NoneReferenceError(
                "the id of the resource instance to delete is None. %s"
                % router)

        try:
            router_body_json = \
                self.os_client.show_router(router.id)
        except NotFound:
            return None


class LoadBalancerManager(NeutronResourceManager):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        super(LoadBalancerManager, self).__init__(os_client=os_client)
        self.resource_class = LoadBalancer
        self.resource_name = "loadbalancer"
        self.subnet_manager = SubnetManager(self.os_client)
        self.expected_provisioning_status = "ACTIVE"
        self.expected_operating_status = "ONLINE"

    def list(self):
        """Fetches a list of all loadbalancers for a project."""
        _params = {}

        loadbalancers_json =\
            self.os_client.list_loadbalancers(retrieve_all=True, **_params)
        loadbalancers = []
        for loadbalancer_json in loadbalancers_json["loadbalancers"]:
            loadbalancer = LoadBalancer(os_resource=loadbalancer_json)
            loadbalancer.subnet = loadbalancer_json["vip_subnet_id"][0]
            loadbalancers.append(loadbalancer)
        return loadbalancers

    def show_loadbalancer_stats(self, loadbalancer=None):
        """
        This function does not test yet. Require further programming.
        Especially for the return of the object
        :param loadbalancer:
        :return: json
        """
        if loadbalancer is None:
            raise NoneReferenceError(
                "loadbalancer to show stats can't be None")

        if not isinstance(loadbalancer, LoadBalancer):
            raise TypeError(
                "%s is not %s instance"
                % (loadbalancer, LoadBalancer.__name__))

        if not hasattr(loadbalancer, "id") or not loadbalancer.id:
            raise NoneReferenceError(
                "the id of the loadbalancer to show stats is None. %s"
                % loadbalancer)
        try:
            loadbalancer_stats_json = \
                self.os_client.retrieve_loadbalancer_stats(loadbalancer.id)
        except NotFound:
            return None
        return loadbalancer_stats_json

    def check_status(self, resource_id):
        lb_info = NeutronResourceJsonFactory().get_show_json(
            resource_name=self.resource_name, resource_id=resource_id,
            os_client=self.os_client)
        if lb_info is None:
            return False
        loadbalancer_provisioning_status = lb_info["loadbalancer"]["provisioning_status"]
        loadbalancer_operating_status = lb_info["loadbalancer"]["operating_status"]
        if loadbalancer_provisioning_status == self.expected_provisioning_status\
                and loadbalancer_operating_status == self.expected_operating_status:
            return True
        else:
            return False


class LBaaSPoolManager(NeutronResourceManager):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        super(LBaaSPoolManager, self).__init__(os_client=os_client)
        self.resource_class = LBaaSPool
        self.resource_name = "pool"
        self.loadbalancer_manager = LoadBalancerManager(self.os_client)

    def delete(self, resource_instance):
        if resource_instance is None:
            raise NoneReferenceError("resource instance to delete can't be None")

        if not isinstance(resource_instance, self.resource_class):
            raise TypeError(
                "resource instance %s is not %s instance"
                % (resource_instance, self.resource_class.__name__))

        if not hasattr(resource_instance, "id") or not resource_instance.id:
            raise NoneReferenceError(
                "the id of the resource instance to delete is None. %s"
                % resource_instance)

        self.wait_loadbalancer(resource_instance)

        result = NeutronResourceJsonFactory().get_delete_json(
            resource_name=self.resource_name, os_client=self.os_client,
            resource_id=resource_instance.id)

        return result

    def wait_loadbalancer(self, resource):
        if not isinstance(resource, self.resource_class):
            raise TypeError("neutron resource %s is not %s instance"
                            % (resource, self.resource_class.__name__))
        if resource.loadbalancer is None:
            return True
        elif isinstance(resource.loadbalancer, LoadBalancer):
            if isinstance(resource.loadbalancer.id, list):
                lb_id = resource.loadbalancer.id[0]["id"]
            else:
                lb_id = resource.loadbalancer.id
        elif isinstance(resource.loadbalancer, basestring):
            lb_id = resource.loadbalancer
        else:
            raise TypeError("cannot find the loadbalancer id")

        self.start_time = clock()
        while not self.loadbalancer_manager.check_status(lb_id):
            if clock() - self.start_time > self.timeout:
                raise Exception("Update loadbalancer timeout.")
            self.wait()
        return True

    def list(self):
        """Fetches a list of all pools for a project."""
        # TODO(sy): this function need to be tested
        # Pass filters in "params" argument to do_request
        _params = {}

        lbaas_pools_json = self.os_client.list_lbaas_pools(
            retrieve_all=True, **_params)
        lbaas_pools = []
        for lbaas_pool_json in lbaas_pools_json["pools"]:
            lbaas_pool = LBaaSPool(os_resource=lbaas_pool_json)
            lbaas_pool.loadbalancer = lbaas_pool_json["loadbalancers"][0]["id"]
            lbaas_pools.append(lbaas_pool)

        return lbaas_pools

    def _cascaded_build(self, os_pool_json):
        pool = LBaaSPool(os_resource=os_pool_json["pool"])
        pool.loadbalancer = self.loadbalancer_manager.get(
                LoadBalancer(os_pool_json["pool"]["loadbalancers"][0]["id"]))
        return pool


class ListenerManager(NeutronResourceManager):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        super(ListenerManager, self).__init__(os_client=os_client)
        self.resource_class = Listener
        self.resource_name = "listener"
        self.loadbalancer_manager = LoadBalancerManager(self.os_client)

    def list(self):
        """Fetches a list of all listeners for a project."""
        # TODO(sy): this function need to be tested
        # Pass filters in "params" argument to do_request
        _params = {}

        listeners_json = self.os_client.list_listeners(
            retrieve_all=True, **_params)
        listeners = []
        for listener_json in listeners_json["listeners"]:
            listener = Listener(os_resource=listener_json)
            listener.loadbalancer.id = listener_json["loadbalancers"][0]["id"]
            listeners.append(listener)

        return listeners

    def _cascaded_build(self, os_listener_json):
        listener = Listener(os_resource=os_listener_json["listener"])
        listener.loadbalancer = self.loadbalancer_manager.get(
                LoadBalancer(
                    os_listener_json["listener"]["loadbalancers"][0]["id"]))
        return listener

    def delete(self, resource_instance):
        if resource_instance is None:
            raise NoneReferenceError("resource instance to delete can't be None")

        if not isinstance(resource_instance, self.resource_class):
            raise TypeError(
                "resource instance %s is not %s instance"
                % (resource_instance, self.resource_class.__name__))

        if not hasattr(resource_instance, "id") or not resource_instance.id:
            raise NoneReferenceError(
                "the id of the resource instance to delete is None. %s"
                % resource_instance)

        self.wait_loadbalancer(resource_instance)

        result = NeutronResourceJsonFactory().get_delete_json(
            resource_name=self.resource_name, os_client=self.os_client,
            resource_id=resource_instance.id)

        return result

    def wait_loadbalancer(self, resource):
        if not isinstance(resource, self.resource_class):
            raise TypeError("neutron resource %s is not %s instance"
                            % (resource, self.resource_class.__name__))
        if resource.loadbalancer is None:
            return True
        elif isinstance(resource.loadbalancer, LoadBalancer):
            if isinstance(resource.loadbalancer.id, list):
                lb_id = resource.loadbalancer.id[0]["id"]
            else:
                lb_id = resource.loadbalancer.id
        elif isinstance(resource.loadbalancer, basestring):
            lb_id = resource.loadbalancer
        else:
            raise TypeError("cannot find the loadbalancer id")

        self.start_time = clock()
        while not self.loadbalancer_manager.check_status(lb_id):
            if clock() - self.start_time > self.timeout:
                raise Exception("Update loadbalancer timeout.")
            self.wait()
        return True


class LBaaSHealthMonitorManager(NeutronResourceManager):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        super(LBaaSHealthMonitorManager, self).__init__(os_client=os_client)
        self.resource_class = LBaaSHealthMonitor
        self.resource_name = "healthmonitor"
        self.pool_manager = LBaaSPoolManager(self.os_client)

    def delete(self, resource_instance):
        if resource_instance is None:
            raise NoneReferenceError("resource instance to delete can't be None")

        if not isinstance(resource_instance, self.resource_class):
            raise TypeError(
                "resource instance %s is not %s instance"
                % (resource_instance, self.resource_class.__name__))

        if not hasattr(resource_instance, "id") or not resource_instance.id:
            raise NoneReferenceError(
                "the id of the resource instance to delete is None. %s"
                % resource_instance)

        self.wait_loadbalancer(resource_instance)

        result = NeutronResourceJsonFactory().get_delete_json(
            resource_name=self.resource_name, os_client=self.os_client,
            resource_id=resource_instance.id)

        return result

    def wait_loadbalancer(self, resource):
        if not isinstance(resource, self.resource_class):
            raise TypeError("neutron resource %s is not %s instance"
                            % (resource, self.resource_class.__name__))
        if resource.pool is None:
            return True
        elif isinstance(resource.pool, LBaaSPool):
            pool = resource.pool
        elif isinstance(resource.pool, basestring):
            pool = self.pool_manager.get(LBaaSPool(id=resource.pool))
        else:
            raise TypeError("cannot find the pool of the healthmonitor")
        self.start_time = clock()
        while not self.pool_manager.wait_loadbalancer(pool):
            if clock() - self.start_time > self.timeout:
                raise Exception("Update loadbalancer timeout.")
            self.wait()
        return True

    def _cascaded_build(self, os_healthmonitor_json):
        lbaas_healthmonitor = LBaaSHealthMonitor(
            os_resource=os_healthmonitor_json["healthmonitor"])
        lbaas_healthmonitor.pool = self.pool_manager.get(
            LBaaSPool(
                os_healthmonitor_json["healthmonitor"]["pools"][0]["id"]))
        return lbaas_healthmonitor


class LBaaSMemberManager(object):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        if os_client is None:
            raise NoneReferenceError("os_client can't be None")
        self.os_client = os_client
        self.pool_manager = LBaaSPoolManager(self.os_client)
        self.subnet_manager = SubnetManager(self.os_client)

    def create(self, lbaas_member):
        """
        Create a new member based lon the given parameter.
        --address, --protocol_port, --subnet and --pool are required
        :param lbaas_member: the member to create
        :return: the newly created member
        """
        if lbaas_member is None:
            raise NoneReferenceError("member to create can't be None")

        if not isinstance(lbaas_member, LBaaSMember):
            raise TypeError(
                "%s is not %s instance"
                % (lbaas_member, LBaaSMember.__name__))

        lbaas_member_json = {"member": {
            "name": lbaas_member.name,
            "address": lbaas_member.address,
            "protocol_port": lbaas_member.protocol_port,
            "subnet_id": lbaas_member.subnet.id,
        }}
        response_json = self.os_client.create_lbaas_member(
            lbaas_member.pool.id, lbaas_member_json)
        return self._cascaded_build(response_json, lbaas_member.pool.id)

    def get(self, lbaas_member):
        """
        Getting the member by the given id in the input criteria.
        :param lbaas_member: the member object as retrieving criteria
        :return: the member retrieved
        :raise NoneReferenceError: if the input criteria is None
        :raise TypeError: if the input parameter is not the type managed by the
        current manager
        :raise ValueError: if no id is given in the criteria
        """
        if not lbaas_member:
            raise NoneReferenceError("member to delete is None!")

        if not isinstance(lbaas_member, LBaaSMember):
            raise TypeError("%s is not %s instance"
                            % (lbaas_member, LBaaSMember.__name__))

        if not hasattr(lbaas_member, "id") or not lbaas_member.id:
            raise ValueError(
                "No id is given in the member %s" % lbaas_member)

        try:
            lbaas_member_body_json = self.os_client.show_lbaas_member(
                lbaas_member.id, lbaas_member.pool.id)
        except NotFound:
            return None
        return self._cascaded_build(
            lbaas_member_body_json, lbaas_member.pool.id)

    def delete(self, lbaas_member):
        """
        Delete the given member from OpenStack
        :param lbaas_member: the member to delete
        :raise NoneReferenceError: if the input parameter is None, or if there
        is no id in the input parameter
        :raise TypeError: if the input parameter is not the Pool
        """
        if lbaas_member is None:
            raise NoneReferenceError("member to delete can't be None")

        if not isinstance(lbaas_member, LBaaSMember):
            raise TypeError(
                "member %s is not %s instance"
                % (lbaas_member, LBaaSMember.__name__))

        if not hasattr(lbaas_member, "id") or not lbaas_member.id:
            raise NoneReferenceError(
                "the id of the member to delete is None. %s" % lbaas_member)
        return self.os_client.delete_lbaas_member(
            lbaas_member.id, lbaas_member.pool.id)

    def list_by_member(self, lbaas_member):
        """Fetches a list of all members for a project."""
        # TODO(sy): this function need to be tested
        # Pass filters in "params" argument to do_request
        _params = {}

        lbaas_members_json = self.os_client.list_lbaas_members(
            lbaas_member.pool.id, retrieve_all=True, **_params)
        lbaas_members = []
        for lbaas_member_json in lbaas_members_json["members"]:
            lbaas_member_json["pool_id"] = lbaas_member.pool.id
            lbaas_member = LBaaSMember(os_resource=lbaas_member_json)
            lbaas_members.append(lbaas_member)

        return lbaas_members

    def list(self, lbaas_pool_id):
        """Fetches a list of all members for a project."""
        # TODO(sy): this function need to be tested
        # Pass filters in "params" argument to do_request
        _params = {}

        lbaas_members_json = self.os_client.list_lbaas_members(
            lbaas_pool_id, retrieve_all=True, **_params)
        lbaas_members = []
        for lbaas_member_json in lbaas_members_json["members"]:
            lbaas_member_json["pool_id"] = lbaas_pool_id
            lbaas_member = LBaaSMember(os_resource=lbaas_member_json)
            lbaas_members.append(lbaas_member)

        return lbaas_members

    def _cascaded_build(self, os_lbaas_member_json, pool_id):
        os_lbaas_member_json["member"]["pool_id"] = pool_id
        lbaas_member = LBaaSMember(os_resource=os_lbaas_member_json["member"])
        lbaas_member.subnet = self.subnet_manager.get(
                Subnet(os_lbaas_member_json["member"]["subnet_id"]))
        # json does not include pool_id
        lbaas_member.pool = self.pool_manager.get(
            LBaaSPool(os_lbaas_member_json["member"]["pool_id"]))
        return lbaas_member


class FirewallRuleManager(NeutronResourceManager):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        super(FirewallRuleManager, self).__init__(os_client=os_client)
        self.resource_class = FirewallRule
        self.resource_name = "firewall_rule"


class FirewallPolicyManager(NeutronResourceManager):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        super(FirewallPolicyManager, self).__init__(os_client=os_client)
        self.resource_class = FirewallPolicy
        self.resource_name = "firewall_policy"
        self.firewall_rule_manager = FirewallRuleManager(self.os_client)


class FirewallManager(NeutronResourceManager):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        super(FirewallManager, self).__init__(os_client=os_client)
        self.resource_class = Firewall
        self.resource_name = "firewall"
        self.firewall_policy_manager = FirewallPolicyManager(self.os_client)
        self.router_manager = RouterManager(self.os_client)


class PortforwardingManager(object):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        if os_client is None:
            raise NoneReferenceError("os_client can't be None")
        self.os_client = os_client
        self.resource_class = Portforwarding
        self.resource_name = "portforwarding"
        self.router_manager = RouterManager(self.os_client)

    def create(self, portforwarding):
        """
        Create a new member based lon the given parameter.
        destination_ip, protocol, source_port, destination_port,
        router_id are required
        :param portforwarding: the portforwarding to create
        :return: the newly created portforwarding
        """
        if portforwarding is None:
            raise NoneReferenceError("portforwarding to create can't be None")

        if not isinstance(portforwarding, Portforwarding):
            raise TypeError(
                "%s is not %s instance"
                % (portforwarding, Portforwarding.__name__))
        portforwarding_json = {"portforwarding": {
            "name": portforwarding.name,
            "destination_ip": portforwarding.destination_ip,
            "destination_port": portforwarding.destination_port,
            "source_port": portforwarding.source_port,
            "protocol": portforwarding.protocol,
        }}
        response_json = self.os_client.create_portforwarding(
            portforwarding.router_id, portforwarding_json)
        return self._cascaded_build(response_json["portforwarding"], portforwarding.router_id)

    def get(self, portforwarding, router_id=None):
        """
        Getting the portforwarding by the given id in the input criteria.
        :param portforwarding: the portforwarding object as retrieving criteria
        :param router_id: the router if of the portforwarding
        :return: the portforwarding retrieved
        :raise NoneReferenceError: if the input criteria is None
        :raise TypeError: if the input parameter is not the type managed by the
        current manager
        :raise ValueError: if no id is given in the criteria
        """
        if router_id is None:
            if hasattr(portforwarding, "router_id"):
                router_id = portforwarding.router_id
            else:
                raise NoneReferenceError("router of the portforwarding can't be None")
        if not portforwarding:
            raise NoneReferenceError("portforwarding to delete is None!")

        if not isinstance(portforwarding, Portforwarding):
            raise TypeError("%s is not %s instance"
                            % (portforwarding, Portforwarding.__name__))

        if not hasattr(portforwarding, "id") or not portforwarding.id:
            raise ValueError(
                "No id is given in the portforwarding %s" % portforwarding)

        try:
            portforwarding_body_json = self.os_client.show_portforwarding(
                portforwarding.id, router_id)
        except NotFound:
            return None
        return self._cascaded_build(portforwarding_body_json["portforwarding"], router_id)

    def delete(self, portforwarding, router_id=None):
        """
        Delete the given portforwarding from OpenStack
        :param portforwarding: the portforwarding to delete
        :param router_id: the router id of the portforwarding
        :raise NoneReferenceError: if the input parameter is None, or if there
        is no id in the input parameter
        :raise TypeError: if the input parameter is not the Pool
        """
        if router_id is None:
            if hasattr(portforwarding, "router_id"):
                router_id = portforwarding.router_id
            else:
                raise NoneReferenceError("router of the portforwarding to delete can't be None")
        if portforwarding is None:
            raise NoneReferenceError("portforwarding to delete can't be None")

        if not isinstance(portforwarding, Portforwarding):
            raise TypeError(
                "portforwarding %s is not %s instance"
                % (portforwarding, Portforwarding.__name__))

        if not hasattr(portforwarding, "id") or not portforwarding.id:
            raise NoneReferenceError(
                "the id of the portforwarding to delete is None. %s" % portforwarding)
        return self.os_client.delete_portforwarding(
            portforwarding.id, router_id)

    def list(self, router_id):
        """Fetches a list of all portforwardings for a project."""
        if router_id is None:
            raise NoneReferenceError("router of the portforwarding to delete can't be None")

        _params = {}

        portforwardings_json = self.os_client.list_portforwardings(
            router_id, retrieve_all=True, **_params)
        portforwardings = []
        for portforwarding_json in portforwardings_json["portforwardings"]:
            portforwarding = self._cascaded_build(portforwarding_json, router_id)
            portforwardings.append(portforwarding)

        return portforwardings

    def _cascaded_build(self, os_portforwarding_json, router_id):
        os_portforwarding_json["router_id"] = router_id
        portforwarding = Portforwarding(os_resource=os_portforwarding_json)
        return portforwarding


class VpnIkepolicyManager(NeutronResourceManager):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        super(VpnIkepolicyManager, self).__init__(os_client=os_client)
        self.resource_class = VpnIkepolicy
        self.resource_name = "ikepolicy"


class VpnIpsecpolicyManager(NeutronResourceManager):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        super(VpnIpsecpolicyManager, self).__init__(os_client=os_client)
        self.resource_class = VpnIpsecpolicy
        self.resource_name = "ipsecpolicy"


class VpnServiceManager(NeutronResourceManager):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        super(VpnServiceManager, self).__init__(os_client=os_client)
        self.resource_class = VpnService
        self.resource_name = "vpnservice"
        self.router_manager = RouterManager(self.os_client)

    #def create(self, neutron_resource):
    #    super(VpnServiceManager, self).create(neutron_resource)

    def get_status(self, resource_id):
        try:
            resource_body_json = NeutronResourceJsonFactory().get_show_json(
                resource_name=self.resource_name, resource_id=resource_id,
                os_client=self.os_client)
        except NotFound:
            return None
        return resource_body_json["vpnservice"]["status"]

    def get_external_v4_ip(self, neutron_resource):
        if not neutron_resource:
            raise NoneReferenceError("neutron resource to delete is None!")

        if not isinstance(neutron_resource, self.resource_class):
            raise TypeError("neutron resource %s is not %s instance"
                            % (neutron_resource, self.resource_class.__name__))

        if not hasattr(neutron_resource, "id") or not neutron_resource.id:
            raise ValueError(
                "No id is given in the neutron resource %s" % neutron_resource)
        try:
            resource_body_json = NeutronResourceJsonFactory().get_show_json(
                resource_name=self.resource_name, resource_id=neutron_resource.id,
                os_client=self.os_client)
        except NotFound:
            return None
        return resource_body_json[self.resource_name]["external_v4_ip"]


class VpnEndpointGroupManager(NeutronResourceManager):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        super(VpnEndpointGroupManager, self).__init__(os_client=os_client)
        self.resource_class = VpnEndpointGroup
        self.resource_name = "endpoint_group"
        self.subnet_manager = SubnetManager(self.os_client)


class VpnIpsecSiteConnectionManager(NeutronResourceManager):
    # TODO: Test
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        Require ipsecpolicy_id, peer_ep_group_id, ikepolicy_id=, vpnservice_id
        """
        super(VpnIpsecSiteConnectionManager, self).__init__(os_client=os_client)
        self.resource_class = VpnIpsecSiteConnection
        self.resource_name = "ipsec_site_connection"
        self.ipsecpolicy_manager = VpnIpsecpolicyManager(self.os_client)
        self.ikepolicy_manager = VpnIkepolicyManager(self.os_client)
        self.vpnservice_manager = VpnServiceManager(self.os_client)
        self.endpoint_group_manager = VpnEndpointGroupManager(self.os_client)

    def get_status(self, resource_id):
        try:
            resource_body_json = NeutronResourceJsonFactory().get_show_json(
                resource_name=self.resource_name, resource_id=resource_id,
                os_client=self.os_client)
        except NotFound:
            return None
        return resource_body_json["ipsec_site_connection"]["status"]

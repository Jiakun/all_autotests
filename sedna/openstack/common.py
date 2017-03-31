"""
The package contains the common objects for the OpenStack related operations,
like the value object representing the platform resources
"""


class Resource(object):
    """Base class for all OpenStack resources, like user, project, server"""

    def __init__(self, id=None, name=None, os_resource=None):
        """
        Initialization. When os_resource is given ,the id and name will be
        ignored.
        :param id: the unique id of the current resource
        :param name: the name of the current resource
        :param os_resource: the original OpenStack resource
        """
        if id:
            self.id = id
        self.name = name

        if not os_resource:
            return

        if hasattr(os_resource, "id"):
            self.id = os_resource.id
        elif hasattr(os_resource, "__iter__") and "id" in os_resource:
            self.id = os_resource["id"]

        if hasattr(os_resource, "name"):
            self.name = os_resource.name
        elif hasattr(os_resource, "__iter__") and "name" in os_resource:
            self.name = os_resource["name"]

        if hasattr(os_resource, "status"):
            self.status = os_resource.status
        elif hasattr(os_resource, "__iter__") and "status" in os_resource:
            self.status = os_resource["status"]

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.id == self.id

    def __ne__(self, other):
        return not self.__eq__(other)


class User(Resource):
    """The value object indicates the user in the OpenStack."""

    def __init__(self, id=None, name=None, os_resource=None):
        """
        Initialization. When os_user is given ,the id and name will be
        ignored.
        :param id: the unique id of the current user
        :param name: the name of the current user
        :param os_user: the original OpenStack user
        """
        super(User, self).__init__(id=id, name=name, os_resource=os_resource)


class Project(Resource):
    """The value object indicates the project(tenant) in the OpenStack."""

    def __init__(self, id=None, name=None, domain=None, os_resource=None):
        """
        Initialization. When os_project is given ,the id and name will be
        ignored.
        :param id: the unique id of the current project
        :param name: the name of the current project
        :param os_project: the original OpenStack project
        """
        super(Project, self).__init__(
            id=id, name=name, os_resource=os_resource)
        self.domain = domain


class Domain(Resource):
    """The value object indicates the domain in the OpenStack."""

    def __init__(self, id=None, name=None, description=None, enabled=True,
                 os_resource=None):
        """
        Initialization. When os_domain is given ,the id and name will be
        ignored.
        :param id: the unique id of the current domain
        :param name: the name of the current domain
        :param os_domain: the original OpenStack domain
        """
        super(Domain, self).__init__(id, name, os_resource)
        self.enabled = os_resource.enabled if os_resource else enabled
        self.description = \
            os_resource.description if os_resource else description


class Volume(Resource):
    """The value object indicates the volume in the OpenStack."""

    def __init__(self, id=None, name=None, size=None, os_resource=None):
        """
        Initialization. When os_volume is given ,the other parameters will be
        ignored.
        :param id: the unique id of the current volume
        :param name: the volume name
        :param size: the size of volume in GB
        :param os_volume: the original OpenStack volume
        """
        super(Volume, self).__init__(id, name=name, os_resource=os_resource)
        self.size = size


class Snapshot(Resource):
    """The value object indicates the snapshot in the OpenStack."""

    def __init__(self, id=None, name=None, volume=None, os_resource=None):
        """
        Initialization. When os_snapshot is given ,the other parameters will be
        ignored.

        :param id: the id of the current snapshot
        :param name: the name of the current snapshot
        :param volume: the volume which the current snapshot is created from
        :param os_snapshot: the original OpenStack snapshot
        """
        super(Snapshot, self).__init__(id, name=name, os_resource=os_resource)
        self.volume = volume


class Network(Resource):
    """The value object indicates the network in the OpenStack."""
    pass


class Subnet(Resource):
    """The value object indicates the subnet in the OpenStack."""

    def __init__(self, id=None, name=None, network=None, cidr=None,
                 ip_version=4, os_resource=None):
        """
        Initialization. When os_snapshot is given ,the other parameters will be
        ignored.
        :param id: the id of the current subnet
        :param name: the name of the current subnet
        :param network: the network which the subnet belongs to
        :param cidr: the CIDR of the subnet
        :param ip_version: the ip version supported by the subnet
        :param os_resource: the original OpenStack subnet
        """
        super(Subnet, self).__init__(id, name=name, os_resource=os_resource)
        self.network = Network(id=os_resource["network_id"]) \
            if os_resource else network
        self.cidr = os_resource["cidr"] if os_resource else cidr
        self.ip_version = os_resource["ip_version"] \
            if os_resource else ip_version


class Port(Resource):
    """The value object indicates the port in the OpenStack."""

    def __init__(self, id=None, name=None, subnet=None, subnet_id=None,
                 device_id=None, os_resource=None):
        super(Port, self).__init__(id, name=name, os_resource=os_resource)
        self.subnet = subnet
        self.subnet_id = os_resource["fixed_ips"][0]["subnet_id"] if \
            os_resource else subnet_id
        self.device_id = os_resource["device_id"] if \
            os_resource else device_id


class Floatingip(Resource):
    """The value object indicates the floatingip in the OpenStack."""

    def __init__(self, id=None, name=None, port=None,
                 external_net=None, os_resource=None, status=None):
        super(Floatingip, self).__init__(id, name=name,
                                         os_resource=os_resource)
        self.port = Port(id=os_resource["port_id"]) if \
            os_resource else port
        if os_resource:
            self.external_net = Network(
                id=os_resource["floating_network_id"])
        else:
            self.external_net = external_net
        self.status = os_resource["status"] if os_resource else status


class Router(Resource):
    """The value object indicates the router in the OpenStack."""
    def __init__(self, id=None, name=None, admin_state_up=True,
                 external_gateway_info=None, os_resource=None):
        super(Router, self).__init__(id, name=name, os_resource=os_resource)
        self.admin_state_up = os_resource["admin_state_up"] if \
            os_resource else admin_state_up
        self.external_gateway_info = os_resource["external_gateway_info"] if \
            os_resource else external_gateway_info


class Image(Resource):
    """The value object indicates the image in the OpenStack."""

    def __init__(self, id=None, name=None, disk_format=None,
                 container_format="bare", visibility="private",
                 os_resource=None):
        super(Image, self).__init__(id, name=name, os_resource=os_resource)

        self.disk_format =\
            os_resource["disk_format"] if os_resource else disk_format
        self.container_format = os_resource["container_format"]\
            if os_resource else container_format
        self.visibility =\
            os_resource["visibility"] if os_resource else visibility


class Server(Resource):
    """The value object indicates the nova Server in the OpenStack."""

    def __init__(self, id=None, name=None, image=None,
                 flavor=None, nics=None, volume=None, os_resource=None):
        super(Server, self).__init__(id, name=name, os_resource=os_resource)
        self.image = os_resource.image if os_resource else image
        self.flavor = os_resource.flavor if os_resource else flavor
        # todo(sy)
        self.nics = nics
        self.volume = volume


class Flavor(Resource):
    """The value object indicates the nova Flavor in the OpenStack."""

    def __init__(self, id=None, name=None, ram=None,
                 vcpus=None, disk=None, os_resource=None):
        super(Flavor, self).__init__(id, name=name, os_resource=os_resource)
        self.ram = os_resource.ram if os_resource else ram
        self.vcpus = os_resource.vcpus if os_resource else vcpus
        self.disk = os_resource.disk if os_resource else disk


class SecurityGroup(Resource):
    """"""
    def __init__(self, id=None, name=None, os_resource=None):
        super(SecurityGroup, self).__init__(id, name=name,
                                            os_resource=os_resource)


class Keypair(Resource):
    """"""
    def __init__(self, id=None, name=None, os_resource=None):
        super(Keypair, self).__init__(id, name=name, os_resource=os_resource)


class LoadBalancer(Resource):
    """
    param id: the id of this Loadbalancer
    param name: the name of this Loadbalancer
    param vip_subnet: the VIP subnet of this Loadbalancer
    """
    def __init__(self, id=None, name=None, os_resource=None, subnet=None):
        super(LoadBalancer, self).__init__(
            id, name=name, os_resource=os_resource)
        self.subnet = Subnet(os_resource["vip_subnet_id"]) if \
            os_resource else subnet


class LBaaSPool(Resource):
    """
    param id: the id of this Pool
    param name: the name of this Pool
    param lb_algorithm: the algorithm for using LoadBalancer from
    ['ROUND_ROBIN','LEAST_CONNECTIONS','SOURCE_IP']
    param protocol: the protocol of this Pool from ['HTTP','HTTPS','TCP']
    param loadbalancer: the LoadBlancer of this Pool
    ignored param listener: this attribute is ignored at this moment
    and it's an alternative for loadbalancer
    """
    def __init__(self, id=None, name=None, os_resource=None, loadbalancer=None,
                 protocol=None, lb_algorithm=None):
        super(LBaaSPool, self).__init__(id=id, name=name, os_resource=os_resource)
        self.loadbalancer = LoadBalancer(os_resource["loadbalancers"]) if \
            os_resource else loadbalancer
        self.protocol = os_resource["protocol"] if os_resource else protocol
        self.lb_algorithm = os_resource["lb_algorithm"] if \
            os_resource else lb_algorithm


class Listener(Resource):
    """
    param id: the id of this Listener
    param name: the name of this Listener
    param loadbalancer: the LoadBalancer of this Listener
    param protocol: the protocol of this Listener
    param protocol_port: the port of the protocol
    ignored param default_pool: this attribute is ignored at this moment,
    and it's an alternative for loadbalancer
    """
    def __init__(self, id=None, name=None, os_resource=None, loadbalancer=None,
                 protocol=None, protocol_port=None):
        super(Listener, self).__init__(id, name=name, os_resource=os_resource)
        self.loadbalancer = LoadBalancer(os_resource["loadbalancers"]) if \
            os_resource else loadbalancer
        self.protocol = os_resource["protocol"] if os_resource else protocol
        self.protocol_port = os_resource["protocol_port"] if \
            os_resource else protocol_port


class LBaaSHealthMonitor(Resource):
    """
    param id: the id of this HealthMonitor
    param name: the name of this HealthMonitor
    param delay: the delay of this HealthMonitor
    param max_retries: the maximum retries of this HealthMonitor
    param timeout: the time out of this HealthMonitor
    param type: type for HealthMonitor from ['PING', 'TCP', 'HTTP', 'HTTPS']
    param pool: The pool of this HealthMonitor
    """

    def __init__(self, id=None, name=None, os_resource=None, delay=None,
                 max_retries=None, timeout=None, type=None, lbaas_pool=None):
        super(LBaaSHealthMonitor, self).__init__(
            id, name=name, os_resource=os_resource)
        self.pool = LBaaSPool(os_resource["pools"]) if \
            os_resource else lbaas_pool
        self.delay = os_resource["delay"] if os_resource else delay
        self.max_retries = os_resource["max_retries"] if \
            os_resource else max_retries
        self.timeout = os_resource["timeout"] if os_resource else timeout
        self.type = os_resource["type"] if os_resource else type


class LBaaSMember(Resource):
    """
    param id: the id of this Member
    param name: the name of this Member
    param subnet: the subnet of this Member
    param address: the address of this Member
    param protocol_port: the protocol port of this Member
    param pool: The pool of this Member
    """

    def __init__(self, id=None, name=None, os_resource=None, subnet=None,
                 address=None, protocol_port=None, lbaas_pool=None):
        super(LBaaSMember, self).__init__(
            id, name=name, os_resource=os_resource)
        self.pool = LBaaSPool(os_resource["pool_id"]) if \
            os_resource else lbaas_pool
        self.subnet = Subnet(os_resource["subnet_id"]) if \
            os_resource else subnet
        self.address = os_resource["address"] if os_resource else address
        self.protocol_port = os_resource["protocol_port"] if \
            os_resource else protocol_port


class FirewallRule(Resource):
    def __init__(self, id=None, name=None, os_resource=None,
                 protocol=None, action=None):
        super(FirewallRule, self).__init__(id=id, name=name, os_resource=os_resource)
        self.protocol = os_resource["protocol"] if os_resource else protocol
        self.action = os_resource["action"] if os_resource else action


class FirewallPolicy(Resource):
    def __init__(self, id=None, name=None, os_resource=None, firewall_rules=None):
        super(FirewallPolicy, self).__init__(
            id=id, name=name, os_resource=os_resource)
        self.firewall_rules = \
            os_resource["firewall_rules"] if os_resource else firewall_rules


class Firewall(Resource):
    def __init__(self, id=None, name=None, os_resource=None,
                 firewall_policy_id=None, router_ids=None):
        super(Firewall, self).__init__(id=id, name=name, os_resource=os_resource)
        if type(firewall_policy_id) == FirewallPolicy:
            firewall_policy_id = firewall_policy_id.id

        temp_router_ids = []
        if router_ids is not None:
            for router_id in router_ids:
                if type(router_id) == Router:
                    temp_router_ids.append(router_id.id)
                else:
                    temp_router_ids.append(router_id)

        self.firewall_policy_id = \
            os_resource["firewall_policy_id"] if os_resource else firewall_policy_id
        self.router_ids = os_resource["router_ids"] if os_resource else temp_router_ids


class Portforwarding(Resource):
    def __init__(self, id=None, name=None, os_resource=None,
                 destination_ip=None, protocol=None, source_port=None,
                 destination_port=None, router_id=None):
        super(Portforwarding, self).__init__(id=id, name=name, os_resource=os_resource)
        if type(router_id) == Router:
            router_id = router_id.id

        self.router_id = os_resource["router_id"] if os_resource else router_id
        self.destination_ip = os_resource["destination_ip"] if os_resource else destination_ip
        self.protocol = os_resource["protocol"] if os_resource else protocol
        self.source_port = os_resource["source_port"] if os_resource else source_port
        self.destination_port = os_resource["destination_port"] if os_resource else destination_port


class VpnIkepolicy(Resource):
    def __init__(self, id=None, name=None, os_resource=None):
        super(VpnIkepolicy, self).__init__(id=id, name=name, os_resource=os_resource)


class VpnIpsecpolicy(Resource):
    def __init__(self, id=None, name=None, os_resource=None):
        super(VpnIpsecpolicy, self).__init__(id=id, name=name, os_resource=os_resource)


class VpnService(Resource):
    def __init__(self, id=None, name=None, os_resource=None, router_id=None):
        super(VpnService, self).__init__(id=id, name=name, os_resource=os_resource)
        if type(router_id) == Router:
            router_id = router_id.id
        self.router_id = os_resource["router_id"] if os_resource else router_id


class VpnIpsecSiteConnection(Resource):
    def __init__(self, id=None, name=None, os_resource=None, psk=None,
                 ipsecpolicy_id=None, peer_ep_group_id=None, ikepolicy_id=None,
                 vpnservice_id=None, local_ep_group_id=None, peer_address=None,
                 peer_id=None):
        super(VpnIpsecSiteConnection, self).__init__(id=id, name=name, os_resource=os_resource)
        self.psk = os_resource["psk"] if os_resource else psk
        self.ipsecpolicy_id = os_resource["ipsecpolicy_id"] if os_resource else ipsecpolicy_id
        self.peer_ep_group_id = os_resource["peer_ep_group_id"] if os_resource else peer_ep_group_id
        self.ikepolicy_id = os_resource["ikepolicy_id"] if os_resource else ikepolicy_id
        self.vpnservice_id = os_resource["vpnservice_id"] if os_resource else vpnservice_id
        self.local_ep_group_id = os_resource["local_ep_group_id"] if os_resource else local_ep_group_id
        self.peer_address = os_resource["peer_address"] if os_resource else peer_address
        self.peer_id = os_resource["peer_id"] if os_resource else peer_id


class VpnEndpointGroup(Resource):
    def __init__(self, id=None, name=None, os_resource=None, type=None, endpoints=None):
        super(VpnEndpointGroup, self).__init__(id=id, name=name, os_resource=os_resource)
        self.endpoints = os_resource["endpoints"] if os_resource else endpoints
        self.type = os_resource["type"] if os_resource else type


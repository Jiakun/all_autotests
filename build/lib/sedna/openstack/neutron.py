from neutronclient.common.exceptions import NotFound
from sedna.openstack.common import Network, Port, Subnet, \
    Floatingip, Router, Server, SecurityGroup, LoadBalancer, \
    LBaaSPool, Listener, LBaaSHealthMonitor, LBaaSMember
from sedna.error import NoneReferenceError, IllegalStateError

from datetime import datetime
from time import sleep


class NetworkManager(object):
    """Manager class used to manipulate Network resource"""

    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        if os_client is None:
            raise NoneReferenceError("os_client can't be None")
        self.os_client = os_client

    def create(self, network):
        """
        Create a new network based on the given paramter
        :param network: the network to create
        :return: the newly created network
        """
        if network is None:
            raise NoneReferenceError("network to create can't be None")

        if not isinstance(network, Network):
            raise TypeError(
                "network %s is not %s instance"
                % (network, Network.__name__))

        network_json = {"network": vars(network)}

        created_network_json = self.os_client.create_network(network_json)
        created_network = created_network_json["network"]
        return Network(os_resource=created_network)

    def get(self, network):
        """
        Getting the network by the given id in the input criteria.
        :param network: the network object as retrieving criteria
        :return: the network retrieved
        :raise NoneReferenceError: if the input criteria is None
        :raise TypeError: if the input parameter is not the type managed by the
        current manager
        :raise ValueError: if no id is given in the criteria
        """
        if not network:
            raise NoneReferenceError("network to delete is None!")

        if not isinstance(network, Network):
            raise TypeError("network %s is not %s instance"
                            % (network, Network.__name__))

        if not hasattr(network, "id") or not network.id:
            raise ValueError(
                "No id is given in the network %s" % network)

        try:
            network_body_json = self.os_client.show_network(network.id)
        except NotFound:
            return None
        return Network(os_resource=network_body_json["network"])

    def list(self):
        network_json_list = self.os_client.list_networks()
        networks = []
        for network_json in network_json_list["networks"]:
            network = Network(os_resource=network_json)
            networks.append(network)
        return networks

    def delete(self, network):
        """
        Delete the given network from OpenStack
        :param network: the network to delete
        :raise NoneReferenceError: if the input parameter is None, or if there
        is no id in the input parameter
        :raise TypeError: if the input parameter is not the Network
        """
        if network is None:
            raise NoneReferenceError("network to delete can't be None")

        if not isinstance(network, Network):
            raise TypeError(
                "network %s is not %s instance"
                % (network, Network.__name__))

        if not hasattr(network, "id") or not network.id:
            raise NoneReferenceError(
                "the id of the network to delete is None. %s" % network)

        return self.os_client.delete_network(network.id)


class SecurityGroupManager(object):
    """Manager class used to manipulate SecurityGroup resource"""

    def __init__(self, os_client):
        """
        initialization
        :param os_client: Openstack Neutron client
        """
        if os_client is None:
            raise NoneReferenceError("os_client can't be None")
        self.os_client = os_client

    def create(self, security_group):
        """Creates a new security group."""
        if security_group is None:
            raise NoneReferenceError("SecurityGroup to create can't be None")
        body_name = {"security_group": {"name": security_group.name}}
        security_group_json = self.os_client.create_security_group(body_name)
        return self._cascaded_build(security_group_json)

    def list(self):
        securitygroup_json_list = self.os_client.list_security_groups()
        securitygroups = []
        for securitygroup_json in securitygroup_json_list["security_groups"]:
            securitygroup = SecurityGroup(os_resource=securitygroup_json)
            securitygroups.append(securitygroup)
        return securitygroups

    def delete(self, resource):
        """Deletes the specified security group."""
        return self.os_client.delete_security_group(resource.id)

    @staticmethod
    def _cascaded_build(os_security_group_json):
        security_group = SecurityGroup(
            os_resource=os_security_group_json["security_group"])
        return security_group


class SubnetManager(object):
    """Manager class used to manipulate subnet resource"""

    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        if os_client is None:
            raise NoneReferenceError("os_client can't be None")
        self.os_client = os_client
        self.network_manager = NetworkManager(self.os_client)

    def create(self, subnet):
        """
        Create a new subnet based on the given parameter. Subnet's name, cidr,
        ip_version and network are required.
        :param subnet: the subnet to create
        :return: the newly created subnet
        """
        if subnet is None:
            raise NoneReferenceError("subnet to create can't be None")

        if not isinstance(subnet, Subnet):
            raise TypeError(
                "subnet %s is not %s instance"
                % (subnet, Subnet.__name__))

        subnet_json = {"subnet": {
            "name": subnet.name,
            "network_id": subnet.network.id,
            "cidr": subnet.cidr,
            "ip_version": subnet.ip_version,
        }}

        response_json = self.os_client.create_subnet(subnet_json)
        return self._cascaded_build(response_json)

    def get(self, subnet):
        """
        Getting the subnet by the given id in the input criteria.
        :param subnet: the subnet object as retrieving criteria
        :return: the subnet retrieved
        :raise NoneReferenceError: if the input criteria is None
        :raise TypeError: if the input parameter is not the type managed by the
        current manager
        :raise ValueError: if no id is given in the criteria
        """
        if not subnet:
            raise NoneReferenceError("subnet to delete is None!")

        if not isinstance(subnet, Subnet):
            raise TypeError("subnet %s is not %s instance"
                            % (subnet, Subnet.__name__))

        if not hasattr(subnet, "id") or not subnet.id:
            raise ValueError(
                "No id is given in the subnet %s" % subnet)

        try:
            subnet_body_json = self.os_client.show_subnet(subnet.id)
        except NotFound:
            return None
        return self._cascaded_build(subnet_body_json)

    def delete(self, subnet):
        """
        Delete the given subnet from OpenStack
        :param subnet: the subnet to delete
        :raise NoneReferenceError: if the input parameter is None, or if there
        is no id in the input parameter
        :raise TypeError: if the input parameter is not the subnet
        """
        if subnet is None:
            raise NoneReferenceError("subnet to delete can't be None")

        if not isinstance(subnet, Subnet):
            raise TypeError(
                "network %s is not %s instance"
                % (subnet, Subnet.__name__))

        if not hasattr(subnet, "id") or not subnet.id:
            raise NoneReferenceError(
                "the id of the subnet to delete is None. %s" % subnet)
        # TODO(sy): check interface status in subnet, not sleep
        sleep(5)
        return self.os_client.delete_subnet(subnet.id)

    def list(self):
        subnet_json_list = self.os_client.list_subnets()
        subnets = []
        for subnet_json in subnet_json_list["subnets"]:
            subnet = Subnet(os_resource=subnet_json)
            subnets.append(subnet)
        return subnets

    @staticmethod
    def _cascaded_build(os_subnet_json):
        subnet_json = os_subnet_json["subnet"]
        subnet = Subnet(os_resource=subnet_json)
        subnet.network = Network(subnet_json["network_id"])
        return subnet


class PortManager(object):
    """Manager class used to manipulate port resource"""

    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        if os_client is None:
            raise NoneReferenceError("os_client can't be None")
        self.os_client = os_client
        self.subnet_manager = SubnetManager(self.os_client)

    def create(self, port):
        """
        Create a new port based on the given parameter. Subnet's name, subnet,
        are required.
        :param port: the port to create
        :return: the newly created subnet
        """
        if port is None:
            raise NoneReferenceError("port to create can't be None")

        if not isinstance(port, Port):
            raise TypeError("port %s is not %s instance" %
                            (port, Port.__name__))

        port_json = {"port": {
            "name": port.name,
            "network_id": port.subnet.network.id,
            "fixed_ips": [
                {"subnet_id": port.subnet.id},
            ]
        }}

        response_json = self.os_client.create_port(port_json)
        return self._cascaded_build(response_json)

    def get(self, port):
        """
        Getting the port by the given id in the input criteria.
        :param port: the port object as retrieving criteria
        :return: the port retrieved
        :raise NoneReferenceError: if the input criteria is None
        :raise TypeError: if the input parameter is not the type managed by the
        current manager
        :raise ValueError: if no id is given in the criteria
        """
        if not port:
            raise NoneReferenceError("port to delete is None!")

        if not isinstance(port, Port):
            raise TypeError("port %s is not %s instance"
                            % (port, Port.__name__))

        if not hasattr(port, "id") or not port.id:
            raise ValueError(
                "No id is given in the port %s" % port)

        try:
            port_body_json = self.os_client.show_port(port.id)
        except NotFound:
            return None
        return self._cascaded_build(port_body_json)

    def delete(self, port):
        """
        Delete the given port from OpenStack
        :param port: the port to delete
        :raise NoneReferenceError: if the input parameter is None, or if there
        is no id in the input parameter
        :raise TypeError: if the input parameter is not the Port
        """
        if port is None:
            raise NoneReferenceError("port to delete can't be None")

        if not isinstance(port, Port):
            raise TypeError(
                "port %s is not %s instance"
                % (port, Port.__name__))

        if not hasattr(port, "id") or not port.id:
            raise NoneReferenceError(
                "the id of the port to delete is None. %s" % port)

        return self.os_client.delete_port(port.id)

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


class FloatingipManager(object):
    """Manager class to manipulate floatingip resource"""
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        if os_client is None:
            raise NoneReferenceError("os_client can't be None")
        self.os_client = os_client
        self.subnet_manager = SubnetManager(self.os_client)
        self.port_manager = PortManager(os_client=self.os_client)

    def create(self, floatingip):
        """
        Create a new floatingip based on the given parameter.
        Floatingip's name, floating_network_id,
        are required.
        :param floatingip: the floatingip to create
        :return: the newly created Floatingip
        """
        if floatingip is None:
            raise NoneReferenceError("floatingip to create can't be None")

        if not isinstance(floatingip, Floatingip):
            raise TypeError("floatingip %s is not %s instance" %
                            (floatingip, Floatingip.__name__))

        floatingip_json = {"floatingip": {
            "floating_network_id": floatingip.external_net.id
        }}

        response_json = self.os_client.create_floatingip(floatingip_json)
        return self._cascaded_build(response_json)

    def get(self, floatingip):
        """
        Getting the floatingip by the given id in the input criteria.
        :param floatingip: the floatingip object as retrieving criteria
        :return: the floatingip retrieved
        :raise NoneReferenceError: if the input criteria is None
        :raise TypeError: if the input parameter is not the type managed by the
        current manager
        :raise ValueError: if no id is given in the criteria
        """
        if not floatingip:
            raise NoneReferenceError("floatingip to delete is None!")

        if not isinstance(floatingip, Floatingip):
            raise TypeError("floatingip %s is not %s instance"
                            % (floatingip, Floatingip.__name__))

        if not hasattr(floatingip, "id") or not floatingip.id:
            raise ValueError(
                "No id is given in the floatingip %s" % floatingip)

        try:
            floatingip_body_json =\
                self.os_client.show_floatingip(floatingip.id)
        except NotFound:
            return None
        return self._cascaded_build(floatingip_body_json)

    def delete(self, floatingip):
        """
        Delete the given floatingip from OpenStack
        :param floatingip: the floatingip to delete
        :raise NoneReferenceError: if the input parameter is None, or if there
        is no id in the input parameter
        :raise TypeError: if the input parameter is not the Floatingip
        """
        if floatingip is None:
            raise NoneReferenceError("floatingip to delete can't be None")

        if not isinstance(floatingip, Floatingip):
            raise TypeError(
                "floatingip %s is not %s instance"
                % (floatingip, Floatingip.__name__))

        if not hasattr(floatingip, "id") or not floatingip.id:
            raise NoneReferenceError(
                "the id of the floatingip to delete is None. %s" % floatingip)

        return self.os_client.delete_floatingip(floatingip.id)

    def list(self):
        """Fetches a list of all floatingip for a project."""
        _params = {}

        floatingips_json =\
            self.os_client.list_floatingips(retrieve_all=True, **_params)
        floatingips = []
        for floatingip_json in floatingips_json["floatingips"]:
            floatingip = Floatingip(os_resource=floatingip_json)
            floatingips.append(floatingip)

        return floatingips

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

    @staticmethod
    def _cascaded_build(os_floatingip_json):
        floatingip = Floatingip(os_resource=os_floatingip_json["floatingip"])
        return floatingip


class RouterManager(object):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Router client
        """
        if os_client is None:
            raise NoneReferenceError("os_client can't be None")
        self.os_client = os_client
        self.subnet_manager = SubnetManager(self.os_client)

    def create(self, router):
        """
        Create a new router based on the given parameter.
        Router's name, network,
        are required.
        :param router: the router to create
        :return: the newly created Router
        """
        if router is None:
            raise NoneReferenceError("router to create can't be None")

        if not isinstance(router, Router):
            raise TypeError("router %s is not %s instance" %
                            (router, Router.__name__))

        router_json = {"router": {
            "name": router.name,
            "admin_state_up": router.admin_state_up
        }}

        response_json = self.os_client.create_router(router_json)
        return self._cascaded_build(response_json)

    def get(self, router):
        """
        Getting the router by the given id in the input criteria.
        :param router: the router object as retrieving criteria
        :return: the router retrieved
        :raise NoneReferenceError: if the input criteria is None
        :raise TypeError: if the input parameter is not the type managed by the
        current manager
        :raise ValueError: if no id is given in the criteria
        """
        if not router:
            raise NoneReferenceError("router to delete is None!")

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
        return self._cascaded_build(router_body_json)

    def delete(self, router):
        """
        Delete the given router from OpenStack
        :param router: the router to delete
        :raise NoneReferenceError: if the input parameter is None, or if there
        is no id in the input parameter
        :raise TypeError: if the input parameter is not the Router
        """
        if router is None:
            raise NoneReferenceError("router to delete can't be None")

        if not isinstance(router, Router):
            raise TypeError(
                "router %s is not %s instance"
                % (router, Router.__name__))

        if not hasattr(router, "id") or not router.id:
            raise NoneReferenceError(
                "the id of the router to delete is None. %s" % router)

        return self.os_client.delete_router(router.id)

    def list(self):
        """Fetches a list of all routers for a project."""
        _params = {}

        routers_json =\
            self.os_client.list_routers(retrieve_all=True, **_params)
        routers = []
        for router_json in routers_json["routers"]:
            router = Router(os_resource=router_json)
            routers.append(router)

        return routers

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

    @staticmethod
    def _cascaded_build(os_router_json):
        router = Router(os_resource=os_router_json["router"])
        return router


class LoadBalancerManager(object):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        if os_client is None:
            raise NoneReferenceError("os_client can't be None")
        self.os_client = os_client
        self.subnet_manager = SubnetManager(self.os_client)

    def create(self, loadbalancer):
        """
        Create a new loadbalancer based on the given parameter.
        Required param: subnet
        return: the newly created loadbalancer
        """
        if loadbalancer is None:
            raise NoneReferenceError("Loadbalancer to create can't be None")

        if not isinstance(loadbalancer, LoadBalancer):
            raise TypeError("Loadbalancer %s is not %s instance" %
                            (loadbalancer, LoadBalancer.__name__))

        loadbalancer_json = {"loadbalancer": {
            "name": loadbalancer.name,
            "vip_subnet_id": loadbalancer.subnet.id,
            # "provisioning_status": loadbalancer.provisioning_status
        }}

        response_json = self.os_client.create_loadbalancer(loadbalancer_json)

        loadbalancer = self._cascaded_build(response_json)

        expected_status = "ACTIVE"
        timeout = 60
        interval = 1
        start = datetime.now()

        while True:
            lb_info = self.show_loadbalancer_status(loadbalancer)
            loadbalancer_status = lb_info["statuses"]["loadbalancer"]

            loadbalancer_status = loadbalancer_status["provisioning_status"]
            if loadbalancer_status == expected_status:
                return loadbalancer
            delta = datetime.now() - start
            if delta.seconds > timeout:
                raise IllegalStateError(
                    "Failed to wait for resource %s to reach status %s "
                    "in %s sec"
                    % ("loadbalancer", expected_status, delta))
            sleep(interval)

    @staticmethod
    def _cascaded_build(os_loadbalancer_json):
        loadbalancer = LoadBalancer(
            os_resource=os_loadbalancer_json["loadbalancer"])
        return loadbalancer

    def get(self, loadbalancer):
        """
        Getting the loadbalancer by the given id in the input criteria.
        :param loadbalancer: the loadbalancer object as retrieving criteria
        :return: the loadbalancer retrieved
        :raise NoneReferenceError: if the input criteria is None
        :raise TypeError: if the input parameter is not the type managed by the
        current manager
        :raise ValueError: if no id is given in the criteria
        """
        if not loadbalancer:
            raise NoneReferenceError("loadbalancer to delete is None!")

        if not isinstance(loadbalancer, LoadBalancer):
            raise TypeError("loadbalancer %s is not %s instance"
                            % (loadbalancer, LoadBalancer.__name__))

        if not hasattr(loadbalancer, "id") or not loadbalancer.id:
            raise ValueError(
                "No id is given in the loadbalancer %s" % loadbalancer)

        try:
            loadbalancer_body_json = \
                self.os_client.show_loadbalancer(loadbalancer.id)
        except NotFound:
            return None
        return self._cascaded_build(loadbalancer_body_json)

    def delete(self, loadbalancer):
        """
        Delete the given loadbalancer from OpenStack
        :param loadbalancer: the loadbalancer to delete
        :raise NoneReferenceError: if the input parameter is None, or if there
        is no id in the input parameter
        :raise TypeError: if the input parameter is not the loadbalancer
        """
        if loadbalancer is None:
            raise NoneReferenceError("loadbalancer to delete can't be None")

        if not isinstance(loadbalancer, LoadBalancer):
            raise TypeError(
                "loadbalancer %s is not %s instance"
                % (loadbalancer, LoadBalancer.__name__))

        if not hasattr(loadbalancer, "id") or not loadbalancer.id:
            raise NoneReferenceError(
                "the id of the loadbalancer to delete is None. %s"
                % loadbalancer)

        return self.os_client.delete_loadbalancer(loadbalancer.id)

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

    def show_loadbalancer_status(self, loadbalancer=None):
        """
        This function does not test yet. Require further programming.
        Especially for the return of the object
        The client returns a json tree
        :param loadbalancer:
        :return:json
        """
        if loadbalancer is None:
            raise NoneReferenceError(
                "loadbalancer to show status can't be None")

        if not isinstance(loadbalancer, LoadBalancer):
            raise TypeError(
                "%s is not %s instance"
                % (loadbalancer, LoadBalancer.__name__))

        if not hasattr(loadbalancer, "id") or not loadbalancer.id:
            raise NoneReferenceError(
                "the id of the loadbalancer to show status is None. %s"
                % loadbalancer)
        try:
            loadbalancer_status_json = \
                self.os_client.retrieve_loadbalancer_status(loadbalancer.id)
        except NotFound:
            return None
        return loadbalancer_status_json


class LBaaSPoolManager(object):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        if os_client is None:
            raise NoneReferenceError("os_client can't be None")
        self.os_client = os_client
        self.loadbalancer_manager = LoadBalancerManager(self.os_client)

    def create(self, lbaas_pool):
        """
        Create a new pool based lon the given parameter.
        protocol
        lb_algorithm
        loadbalancer
        :param lbaas_pool: the pool to create
        :return: the newly created pool
        """
        if lbaas_pool is None:
            raise NoneReferenceError("lbaas pool to create can't be None")

        if not isinstance(lbaas_pool, LBaaSPool):
            raise TypeError(
                "%s is not %s instance"
                % (lbaas_pool, LBaaSPool.__name__))

        lbaas_pool_json = {"pool": {
            "name": lbaas_pool.name,
            "lb_algorithm": lbaas_pool.lb_algorithm,
            "protocol": lbaas_pool.protocol,
            "loadbalancer_id": lbaas_pool.loadbalancer.id
        }}

        response_json = self.os_client.create_lbaas_pool(lbaas_pool_json)
        return self._cascaded_build(response_json)

    def get(self, lbaas_pool):
        """
        Getting the pool by the given id in the input criteria.
        :param lbaas_pool: the pool object as retrieving criteria
        :return: the pool retrieved
        :raise NoneReferenceError: if the input criteria is None
        :raise TypeError: if the input parameter is not the type managed by the
        current manager
        :raise ValueError: if no id is given in the criteria
        """
        if not lbaas_pool:
            raise NoneReferenceError("lbaas_pool to delete is None!")

        if not isinstance(lbaas_pool, LBaaSPool):
            raise TypeError("%s is not %s instance"
                            % (lbaas_pool, LBaaSPool.__name__))

        if not hasattr(lbaas_pool, "id") or not lbaas_pool.id:
            raise ValueError(
                "No id is given in the lbaas pool %s" % lbaas_pool)

        try:
            lbaas_pool_body_json = self.os_client.show_lbaas_pool(
                lbaas_pool.id)
        except NotFound:
            return None
        return self._cascaded_build(lbaas_pool_body_json)

    def delete(self, lbaas_pool):
        """
        Delete the given pool from OpenStack
        :param lbaas_pool: the pool to delete
        :raise NoneReferenceError: if the input parameter is None, or if there
        is no id in the input parameter
        :raise TypeError: if the input parameter is not the Pool
        """
        if lbaas_pool is None:
            raise NoneReferenceError("pool to delete can't be None")

        if not isinstance(lbaas_pool, LBaaSPool):
            raise TypeError(
                "pool %s is not %s instance"
                % (lbaas_pool, LBaaSPool.__name__))

        if not hasattr(lbaas_pool, "id") or not lbaas_pool.id:
            raise NoneReferenceError(
                "the id of the pool to delete is None. %s" % lbaas_pool)

        return self.os_client.delete_lbaas_pool(lbaas_pool.id)

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


class ListenerManager(object):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        if os_client is None:
            raise NoneReferenceError("os_client can't be None")
        self.os_client = os_client
        self.loadbalancer_manager = LoadBalancerManager(self.os_client)

    def create(self, listener):
        """
        Create a new listener based lon the given parameter.
        --protocol, --protocol-port and --loadbalancer are required
        --default-pool is ignored
        :param listener: the listener to create
        :return: the newly created listener
        """
        if listener is None:
            raise NoneReferenceError("listener to create can't be None")

        if not isinstance(listener, Listener):
            raise TypeError(
                "%s is not %s instance"
                % (listener, Listener.__name__))

        listener_json = {"listener": {
            "name": listener.name,
            "protocol_port": listener.protocol_port,
            "protocol": listener.protocol,
            "loadbalancer_id": listener.loadbalancer.id,
        }}

        response_json = self.os_client.create_listener(listener_json)
        return self._cascaded_build(response_json)

    def get(self, listener):
        """
        Getting the listener by the given id in the input criteria.
        :param listener: the listener object as retrieving criteria
        :return: the listener retrieved
        :raise NoneReferenceError: if the input criteria is None
        :raise TypeError: if the input parameter is not the type managed by the
        current manager
        :raise ValueError: if no id is given in the criteria
        """
        if not listener:
            raise NoneReferenceError("listener to delete is None!")

        if not isinstance(listener, Listener):
            raise TypeError("%s is not %s instance"
                            % (listener, Listener.__name__))

        if not hasattr(listener, "id") or not listener.id:
            raise ValueError(
                "No id is given in the listener %s" % listener)

        try:
            listener_body_json = self.os_client.show_listener(listener.id)
        except NotFound:
            return None
        return self._cascaded_build(listener_body_json)

    def delete(self, listener):
        """
        Delete the given listener from OpenStack
        :param listener: the listener to delete
        :raise NoneReferenceError: if the input parameter is None, or if there
        is no id in the input parameter
        :raise TypeError: if the input parameter is not the Pool
        """
        if listener is None:
            raise NoneReferenceError("listener to delete can't be None")

        if not isinstance(listener, Listener):
            raise TypeError(
                "listener %s is not %s instance"
                % (listener, Listener.__name__))

        if not hasattr(listener, "id") or not listener.id:
            raise NoneReferenceError(
                "the id of the listener to delete is None. %s" % listener)

        # To avoid the following error, we wait for the state changing
        # StateInvalidClient: Invalid state PENDING_UPDATE of loadbalancer
        # TODO: check whether this can be replaced by waiting in lb create

        expected_status = "ACTIVE"
        timeout = 10
        interval = 1
        start = datetime.now()

        while True:
            listener.loadbalancer.status = \
                self.loadbalancer_manager.show_loadbalancer_status(
                    listener.loadbalancer)
            loadbalancer_status = \
                listener.loadbalancer.status["statuses"]["loadbalancer"]
            if loadbalancer_status["provisioning_status"] == expected_status:
                return self.os_client.delete_listener(listener.id)
            delta = datetime.now() - start
            if delta.seconds > timeout:
                raise IllegalStateError(
                    "Failed to wait for resource %s to reach status %s "
                    "in %s sec"
                    % ("loadbalancer", expected_status, delta))
            sleep(interval)

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


class LBaaSHealthMonitorManager(object):
    def __init__(self, os_client):
        """
        initialization
        :param os_client: OpenstStack Neutron client
        """
        if os_client is None:
            raise NoneReferenceError("os_client can't be None")
        self.os_client = os_client
        self.pool_manager = LBaaSPoolManager(self.os_client)

    def create(self, lbaas_healthmonitor):
        """
        Create a new health monitor based lon the given parameter.
        --delay, --max_retries, --timeout, --type and --pool are required
        :param lbaas_healthmonitor: the health monitor to create
        :return: the newly created health monitor
        """
        if lbaas_healthmonitor is None:
            raise NoneReferenceError("health monitor to create can't be None")

        if not isinstance(lbaas_healthmonitor, LBaaSHealthMonitor):
            raise TypeError(
                "%s is not %s instance"
                % (lbaas_healthmonitor, LBaaSHealthMonitor.__name__))

        lbaas_healthmonitor_json = {"healthmonitor": {
            "name": lbaas_healthmonitor.name,
            "delay": lbaas_healthmonitor.delay,
            "max_retries": lbaas_healthmonitor.max_retries,
            "timeout": lbaas_healthmonitor.timeout,
            "type": lbaas_healthmonitor.type,
            "pool_id": lbaas_healthmonitor.pool.id,
        }}

        response_json = self.os_client.create_lbaas_healthmonitor(
            lbaas_healthmonitor_json)
        return self._cascaded_build(response_json)

    def get(self, lbaas_healthmonitor):
        """
        Getting the healthmonitor by the given id in the input criteria.
        :param lbaas_healthmonitor: healthmonitor object as retrieving criteria
        :return: the healthmonitor retrieved
        :raise NoneReferenceError: if the input criteria is None
        :raise TypeError: if the input parameter is not the type managed by the
        current manager
        :raise ValueError: if no id is given in the criteria
        """
        if not lbaas_healthmonitor:
            raise NoneReferenceError("health monitor to delete is None!")

        if not isinstance(lbaas_healthmonitor, LBaaSHealthMonitor):
            raise TypeError("%s is not %s instance"
                            % (lbaas_healthmonitor,
                               LBaaSHealthMonitor.__name__))

        if not hasattr(lbaas_healthmonitor, "id") \
                or not lbaas_healthmonitor.id:
            raise ValueError(
                "No id is given in the health monitor %s"
                % lbaas_healthmonitor)

        try:
            lbaas_healthmonitor_body_json = \
                self.os_client.show_lbaas_healthmonitor(lbaas_healthmonitor.id)
        except NotFound:
            return None
        return self._cascaded_build(lbaas_healthmonitor_body_json)

    def delete(self, lbaas_healthmonitor):
        """
        Delete the given healthmonitor from OpenStack
        :param lbaas_healthmonitor: the healthmonitor to delete
        :raise NoneReferenceError: if the input parameter is None, or if there
        is no id in the input parameter
        :raise TypeError: if the input parameter is not the Pool
        """
        if lbaas_healthmonitor is None:
            raise NoneReferenceError("health monitor to delete can't be None")

        if not isinstance(lbaas_healthmonitor, LBaaSHealthMonitor):
            raise TypeError(
                "healthmonitor %s is not %s instance"
                % (lbaas_healthmonitor, LBaaSHealthMonitor.__name__))

        if not hasattr(lbaas_healthmonitor, "id") \
                or not lbaas_healthmonitor.id:
            raise NoneReferenceError(
                "the id of healthmonitor to delete is None. %s"
                % lbaas_healthmonitor)
        return self.os_client.delete_lbaas_healthmonitor(
            lbaas_healthmonitor.id)

    def list(self):
        """Fetches a list of all healthmonitors for a project."""

        _params = {}

        healthmonitors_json = self.os_client.list_lbaas_healthmonitors(
            retrieve_all=True, **_params)
        healthmonitors = []
        for healthmonitor_json in healthmonitors_json["healthmonitors"]:
            healthmonitor = LBaaSHealthMonitor(os_resource=healthmonitor_json)
            healthmonitors.append(healthmonitor)

        return healthmonitors

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

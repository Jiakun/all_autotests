"""The value objects for communication between components """


class Service(object):
    """
    Value object contains service meta data
    to define a service on a given node.

    """
    # TODO the value object containing the service information across nodes
    # TODO make the class properties immutable

    def __init__(self, name=None, ip=None, methods=None, **entries):
        """
        Initialization of Service class.

        :param name: the string indicating unique name of the current service
        :param ip: the ip indicating node where the service status to check
        :param methods: the list containing the methods how the service
        should be checked
        :param entries: the dictionary containing all parameters

        """
        # TODO parameter verification
        self.name = name
        self.ip = ip
        self.methods = methods

        self.__dict__.update(entries)

    def __eq__(self, other):
        return isinstance(other, Service) \
                and self.name == other.name \
                and self.methods == other.methods \
                and self.ip == other.ip

    def __ne__(self, other):
        return not self.__eq__(other)


class Result(object):
    """
    Value object to record the verification result of one service
    """
    def __init__(self, service=None, status=None, analysis=None):
        """
        Initialization of the result of one service result
        :param service: the service Object,
        including the its name, node, method
        :param status: the status of this service performing in one node
        """
        self.service = service
        self.status = status
        self.analysis = analysis

    def __eq__(self, other):
        return isinstance(other, Result) \
                and self.service == other.service \
                and self.status == other.status \
                and self.analysis == other.analysis

    def __ne__(self, other):
        return not self.__eq__(other)


class NodeResult(object):
    """
    Value object to record the verification results of all services on one node
    """
    # TODO the function should be consistent with the interface change
    def __init__(self, group=None, ip=None, result=None):
        """
        Initialization of the result of service results on one node
        :param node: the IP of one node
        :param result: Result object list,including the status of all services
        and their performing in one node
        """
        self.group = group
        self.ip = ip
        self.result = result

    def __eq__(self, other):
        return isinstance(other, NodeResult) \
               and self.group == other.group \
               and self.ip == other.ip \
               and self.result == other.result

    def __ne__(self, other):
        return not self.__eq__(other)


class Node(object):
    """
    Value object contains the service deployment information of a node
    """

    def __init__(self, group=None, ip=None, services=None, **entries):
        """

        :param group: the node belonging to the group_name
        :param ip: node ip
        :param services: a list contains the
        Services obj whose status should be sampled
        :param entries: the dictionary containing all parameters
        """
        self.group = group
        self.ip = ip
        self.services = services

        self.__dict__.update(entries)

    def __eq__(self, other):
        return isinstance(other, Node) \
               and self.group == other.group \
               and self.ip == other.ip \
               and self.services == other.services

    def __ne__(self, other):
        return not self.__eq__(other)

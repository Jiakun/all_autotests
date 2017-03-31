from sedna.error import NoneReferenceError


class ResourceManager(object):
    """Base class contains shared logic to manipulate openstack resources"""

    def __init__(self, os_client, os_resource_manager_name,
                 resource_class):
        """
        Initialization
        :param os_client: the OpenStack service client to handle
        communication with the cloud
        :param os_resource_manager_name: the OpenStack resource manager name
        within the service client
        :param resource_class: the class type of the resource
        """
        if os_client is None:
            raise NoneReferenceError("os_client can't be None")

        self._os_client = os_client

        if not hasattr(self._os_client, os_resource_manager_name):
            raise ValueError(
                "client %s has no manager named %s"
                % (os_client, os_resource_manager_name))

        self._os_resource_manager = getattr(self._os_client,
                                            os_resource_manager_name)

        if resource_class is None:
            raise NoneReferenceError("resource_class can't be None")
        self._resource_class = resource_class

    def build_resource(self, os_resource):
        return self._resource_class(os_resource=os_resource)

    def create(self, resource):
        """
        Create a new OpenStack resource with the given data
        :param resource: the resource to create
        :return: the newly created resource
        """
        if not resource:
            raise NoneReferenceError("resource to create can't be None")

        if not isinstance(resource, self._resource_class):
            raise TypeError(
                "resource %s is not %s instance"
                % (resource, self._resource_class.__name__))

        return self.build_resource(
            self._os_resource_manager.create(**vars(resource)))

    def delete(self, resource):
        """
        Delete the given resource from OpenStack
        :param resource: the resource to delete
        :raise NoneReferenceError: if the input parameter is None, or if there
        is no id in the input parameter
        :raise TypeError: if the input parameter is not the type managed by
        the current manager
        """
        if not resource:
            raise NoneReferenceError("resource to delete is None!")

        if not isinstance(resource, self._resource_class):
            raise TypeError(
                "resource %s is not %s instance"
                % (resource, self._resource_class.__name__))

        if not hasattr(resource, "id") or not resource.id:
            raise NoneReferenceError(
                "the id of the resource to delete is None. %s" % resource)

        return self._os_resource_manager.delete(resource.id)

    def get(self, resource):
        """
        Getting the resource by the given criteria.
        If the id is given, the resource will be retrieved by id, and the name
        will be ignored. If the id is not given, name will be used.
        NOTE: this method doesn't catch NotFound exception, which occurs when
        no resource is found for the given id, because NotFound errors are
        defined separated across OpenStack service clients.
        :param resource: the resource object as retrieving criteria
        :return: the OpenStack resource retrieved
        :raise NoneReferenceError: if the input criteria is None
        :raise TypeError: if the input parameter is not the type managed by the
        current manager
        :raise ValueError: if neither id or name is given in the criteria
        """
        if not resource:
            raise NoneReferenceError("resource to delete is None!")

        if not isinstance(resource, self._resource_class):
            raise TypeError("resource %s is not %s instance"
                            % (resource, self._resource_class.__name__))

        if not hasattr(resource, "id") or not resource.id:
            raise ValueError(
                "No id is given in the %s" % resource)

        return self._get_by_id(resource.id)

    def _get_by_id(self, id):
        os_resource = self._os_resource_manager.get(id)

        if not os_resource:
            return None

        return self.build_resource(os_resource=os_resource)

    def list(self):
        """
        List the given resource from OpenStack
        :param resource: the resource to list
        :raise NoneReferenceError: if the input parameter is None, or if there
        is no id in the input parameter
        :raise TypeError: if the input parameter is not the type managed by
        the current manager
        """
        resources = self._os_resource_manager.list()
        resource_list = []
        for resource in resources:
            resource_list.append(self._resource_class(id=resource.id,
                                                      name=resource.name))
        return resource_list

    def _check_instance_of_class(self, resource_instance):
        if resource_instance is None:
            raise NoneReferenceError("resource instance to start can't be None")

        if not isinstance(resource_instance, self._resource_class):
            raise TypeError(
                "resource instance %s is not %s instance"
                % (resource_instance, self._resource_class.__name__))

        if not hasattr(resource_instance, "id") or not resource_instance.id:
            raise NoneReferenceError(
                "the id of the resource instance to delete is None. %s"
                % resource_instance)

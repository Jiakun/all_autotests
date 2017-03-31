""" wrapper for keystone client """
from exceptions import TypeError

from keystoneclient.exceptions import NotFound

from sedna.error import NoneReferenceError
from sedna.openstack.base import ResourceManager
from sedna.openstack.common import Domain, Project, User


class KeystoneResourceManager(ResourceManager):
    """Base class contains shared logic to manipulate keystone resources"""

    def get(self, resource):
        """
        Getting the resource by the given criteria.
        If the id is given, the resource will be retrieved by id, and the name
        will be ignored. If the id is not given, name will be used.
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

        if hasattr(resource, "id") and resource.id:
            try:
                return self._get_by_id(resource.id)
            except NotFound:
                return None

        if hasattr(resource, "name") and resource.name:
            return self._get_by_name(resource.name)

        raise ValueError(
            "neither id or name is given in the self._resource_class %s"
            % resource)

    def _get_by_name(self, name):
        os_resources = self._os_resource_manager.list(**{"name": name})

        if not os_resources or len(os_resources) == 0:
            return None

        return self.build_resource(os_resource=os_resources[0])


class UserManager(KeystoneResourceManager):
    """The class contains the logic to manipulate user in OpenStack"""

    def __init__(self, keystone_client):
        """
        Initialization
        :param keystone_client: the OpenStack keystone client to handle
        communication with the cloud
        """
        super(UserManager, self).__init__(keystone_client, "users", User)


class ProjectManager(KeystoneResourceManager):
    """The class contains the logic to manipulate project in OpenStack"""

    def __init__(self, keystone_client):
        """
        Initialization
        :param keystone_client: the OpenStack keystone client to handle
        communication with the cloud
        """
        super(ProjectManager, self).__init__(
            keystone_client, "projects", Project)

        self.domain_manager = DomainManager(self._os_client)

    def build_resource(self, os_resource):
        domain = self.domain_manager.get(Domain(os_resource.domain_id))
        project = Project(os_resource=os_resource)
        project.domain = domain
        return project


class DomainManager(KeystoneResourceManager):
    """The class contains the logic to manipulate domain in OpenStack"""

    def __init__(self, keystone_client):
        """
        Initialization
        :param keystone_client: the OpenStack keystone client to handle
        communication with the cloud
        """
        super(DomainManager, self).__init__(keystone_client, "domains", Domain)

    def update(self, domain):
        if not domain:
            raise NoneReferenceError("domain to update is None")
        if not isinstance(domain, Domain):
            raise TypeError(
                "domain %s is not sedna.comon.Domain instance" % domain)

        if not domain.id:
            raise NoneReferenceError(
                "the id of the domain to update is None. %s" % domain)

        return Domain(self._os_resource_manager.update(
            domain.id, name=domain.name, description=domain.description,
            enabled=domain.enabled))

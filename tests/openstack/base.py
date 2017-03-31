from datetime import datetime
import random
from time import sleep

from keystoneauth1.identity.v3 import Password
from keystoneauth1.session import Session

from sedna.error import NoneReferenceError

from novaclient.client import Client as NovaClient


class ResourceManagerTest(object):
    """
    Base class defines common Test suite for the openstack resource manager
    functions. Please note, this class dose not inherit from a TestCase class,
    so the concrete resouce manager test class should inherit both this class
    and TestCase class.
    """

    def __init__(self):
        """
        Initialization
        """
        self.openstack_client = None
        self.resource_manager = None
        self.resource_class = None
        self.expected_resource_name = None
        self.expected_resource = None
        self.created_resource = None

    def build_resource(self):
        """ method to create resource for test during setUp method"""
        resource_name = self.rand_name("ResourceManagerTest", prefix="sedna")
        return self.resource_class(name=resource_name)

    def set_up(self, openstack_client_class, manager_class, resource_class):
        """
        Setup openstack client and target resource to for the test cases to use
        """
        if not hasattr(self, "openstack_client") or not self.openstack_client:
            self.openstack_client =\
                self._init_openstack_client(openstack_client_class)

        self.resource_manager = manager_class(self.openstack_client)
        self.resource_class = resource_class
        self.expected_resource = self.build_resource()
        self.expected_resource_name = self.expected_resource.name

        self.created_resource =\
            self.resource_manager.create(self.expected_resource)

    def sync_delete(self, resource_manager, resource):
        resource_manager.delete(resource)

        start = datetime.now()
        intervar = 5
        wait = 30

        while True:
            deleting_resource = \
                resource_manager.get(resource)
            if deleting_resource is None:
                return

            delta = datetime.now() - start
            if delta.seconds > wait:
                self.fail(
                    "Failed to delete resource %s " % resource)
            sleep(intervar)

    def tear_down(self):
        """
        clean up the resource created for the test
        """
        self.sync_delete(self.resource_manager, self.created_resource)

    def test_create(self):
        """ test creating a resource"""
        retrieved_resource = self.resource_manager.get(self.created_resource)
        self.assertEqual(retrieved_resource, self.created_resource)
        self.assertEqual(retrieved_resource.name, self.created_resource.name)

    def test_create_none(self):
        """ test error raising when a None is given to create function """
        with self.assertRaises(NoneReferenceError):
            self.resource_manager.create(None)

    def test_create_with_incorrect_type(self):
        """
        test error raising when an object of incorrect type is given to create
        """
        with self.assertRaises(TypeError):
            self.resource_manager.create(object())

    def test_get_by_none(self):
        """ test raising error when a None is given to the get function"""
        with self.assertRaises(NoneReferenceError):
            self.resource_manager.get(None)

    def test_get_without_id(self):
        """
        test raising error when either name or id is given to the get function
        """
        with self.assertRaises(ValueError):
            self.resource_manager.get(self.resource_class())

    def test_get_with_incorrect_type(self):
        """
        test raising error when an object of incorrect type is given to the get
        function
        """
        with self.assertRaises(TypeError):
            self.resource_manager.get(object())

    def test_delete_with_none(self):
        """
        test error raising when delete function get a None
        """
        with self.assertRaises(NoneReferenceError):
            self.resource_manager.delete(None)

    def test_delete_with_incorrect_type(self):
        """
        test error raising when delete parameter's type is incorrect
        """
        with self.assertRaises(TypeError):
            self.resource_manager.delete(object())

    def test_delete_without_id(self):
        """
        test error raising when no valid id is given to the delete
        """
        with self.assertRaises(NoneReferenceError):
            self.resource_manager.delete(self.resource_class())

    def rand_name(self, name='', prefix=None):
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

    def _init_openstack_client(self, openstack_client_class):
        # 10.0.12.12

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
        if openstack_client_class == "NovaClient":
            # this is a temp function to avoid 403 error
            return NovaClient(
                version="2.0", username=admin_username, password=admin_password,
                project_id=admin_project_id, auth_url=auth_url)
        else:
            return openstack_client_class(session=os_session)

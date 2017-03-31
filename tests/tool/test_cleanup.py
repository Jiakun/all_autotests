""" Unit test cases for resource cleaner"""
import random
from unittest2 import TestCase

from keystoneauth1.identity.v3 import Password
from keystoneauth1.session import Session
from keystoneclient.v3.client import Client as KeystoneClient

from sedna.tool.cleanup import ResourceCleaner


class UserCleanerTest(TestCase):
    """ Test cases for user  cleanup"""

    def setUp(self):
        """
        Setup keystone client and target user to clean up
        """
        if not hasattr(self, "keystone_client") or not self.keystone_client:
            self.keystone_client = self._init_keystone_client()

        self.resource_cleaner = ResourceCleaner(self.keystone_client)

        self.user_name = self.rand_name("UserCleanerTest", prefix="sedna")
        self.keystone_client.users.create(self.user_name)
        users = self.keystone_client.users.list(**{"name": self.user_name})
        self.assertGreater(len(users), 0)

        self.user = users[0]

    def tearDown(self):
        """
        Cleanup created user if the normal cleanup process is failed
        """
        users = self.keystone_client.users.list(**{"name": self.user_name})
        for user in users:
            self.keystone_client.users.delete(user)

    def test_cleanup(self):
        """ test cleaning up a user"""
        self.resource_cleaner.cleanup_users([self.user])

        users = self.keystone_client.users.list(**{"name": self.user_name})
        self.assertEqual(len(users), 0)

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

    def _init_keystone_client(self):
        auth_url = "http://lb.2.stage.polex.io:35357/"
        admin_username = "admin"
        admin_password = "f657d7e44ed39057a8d1d1ed"
        admin_project_id = "66124df8b15b46dead4bff69ab35cdfb"
        admin_domain_id = "default"
        # region = "RegionOne"

        auth = Password(auth_url=auth_url + "v3",
                        username=admin_username,
                        password=admin_password,
                        project_id=admin_project_id,
                        user_domain_id=admin_domain_id
                        )

        os_session = Session(auth=auth)
        return KeystoneClient(session=os_session)

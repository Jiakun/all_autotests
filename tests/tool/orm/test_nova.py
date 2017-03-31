""" Nova database ORM classes and manipulation test cases """

from unittest2 import TestCase

from sedna.tool.orm import NovaDAO


class NovaTest(TestCase):
    """Nova database ORM classes and manipulation test cases"""

    def test_get_instances(self):
        """ Test retrieving the instances of a project """
        nova_dao = NovaDAO("mysql+pymysql://root:^polex$@10.0.2.37/nova")
        instances = nova_dao.get_instances("18fb285bfa4f4ddaaebb7512683b6a52")
        self.assertGreater(len(instances), 0)

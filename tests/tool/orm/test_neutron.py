""" Test cases for neutron database manipulation """

from unittest2 import TestCase

from sedna.tool.orm import NeutronDAO


class NeutronDAOTest(TestCase):
    """Test cases for NeutronDAO"""

    def test_get_routers(self):
        """Test retreiving routers for the given project"""
        neutron_dao = NeutronDAO(
                "mysql+pymysql://root:^polex$@10.0.2.37/neutron")
        routers = neutron_dao.get_routers("18fb285bfa4f4ddaaebb7512683b6a52")
        self.assertGreater(len(routers), 0)

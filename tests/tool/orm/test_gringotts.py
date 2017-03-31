"""Test case for gringotts database operation """

from unittest2 import TestCase

from sedna.tool.orm import CinderDAO
from sedna.tool.orm import GringottsDAO


class GringottsDAOTest(TestCase):
    """The test cases on gringotts database operations """

    RESOURCE_ID = None

    @classmethod
    def setUpClass(cls):
        """
        setup the volume resource whose billing data will be checked for
        testing shared across all of the test cases
        """
        cinder_dao = CinderDAO("mysql+pymysql://root:^polex$@10.0.2.37/cinder")
        # TODO move project id to configuration file
        volume = cinder_dao.get_volumes("18fb285bfa4f4ddaaebb7512683b6a52")[0]
        GringottsDAOTest.RESOURCE_ID = volume.id

    def setUp(self):
        """setup gringotts dao whose logic will be tested"""
        self.gringotts_dao =\
            GringottsDAO("mysql+pymysql://root:^polex$@10.0.2.37/gringotts")

    def test_init(self):
        """test class initialization"""
        self.assertIsNotNone(GringottsDAO("test url"))

    def test_get_orders(self):
        """ test getting orders of the given resource"""
        orders = self.gringotts_dao.get_orders(GringottsDAOTest.RESOURCE_ID)
        self.assertIsNotNone(orders)
        self.assertGreater(len(orders), 0)

    def test_get_bills(self):
        """test getting bills of the given order"""
        order = self.gringotts_dao.get_orders(GringottsDAOTest.RESOURCE_ID)[0]
        bills = self.gringotts_dao.get_bills(order.order_id)
        self.assertGreater(len(bills), 0)

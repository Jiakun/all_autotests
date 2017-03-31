""" cinder dao test cases"""

from unittest2 import TestCase

from sedna.tool.orm import CinderDAO


class CinderDAOTest(TestCase):
    """The test cases for cinder database operations"""

    def setUp(self):
        self.cinder_dao =\
                CinderDAO("mysql+pymysql://root:^polex$@10.0.2.37/cinder")

    def test_init(self):
        """Test the initialization of CinderDAO"""
        cinder_dao = CinderDAO("test url")
        self.assertIsNotNone(cinder_dao)

    def test_get_volumes(self):
        """Test retrieving the volumes belonging to the project"""

        # TODO move project id to configuration file
        result_set = self.cinder_dao.get_volumes(
                "18fb285bfa4f4ddaaebb7512683b6a52")

        self.assertGreater(len(result_set), 0)

    def test_get_snapshots(self):
        """test retrieving the snapshots of the given project"""
        snapshots = self.cinder_dao.get_snapshots(
                "18fb285bfa4f4ddaaebb7512683b6a52")
        self.assertGreater(len(snapshots), 0)

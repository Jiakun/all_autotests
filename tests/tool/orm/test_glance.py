""" Test cases for glance database """

from unittest2 import TestCase

from sedna.tool.orm import GlanceDAO


class GlanceDAOTest(TestCase):
    """ Test case for glance DAO"""

    def test_get_images(self):
        """ Test retrieving images of a project """
        glance_dao = GlanceDAO("mysql+pymysql://root:^polex$@10.0.2.37/glance")
        images = glance_dao.get_images("18fb285bfa4f4ddaaebb7512683b6a52")
        self.assertGreater(images.count(), 0)

        for image in images:
            self.assertGreater(len(image.properties), 0)

    def test_get_snapshots(self):
        """
        Test retrieving images which are the snapshots of vms of a project
        """
        glance_dao = GlanceDAO("mysql+pymysql://root:^polex$@10.0.2.37/glance")
        images = glance_dao.get_snapshots("18fb285bfa4f4ddaaebb7512683b6a52")
        self.assertGreater(images.count(), 0)

        for image in images:
            self.assertGreater(len(image.properties), 1)
            is_snapshot = False
            for image_property in image.properties:
                if image_property.value == "snapshot":
                    is_snapshot = True
                    break

            self.assertTrue(is_snapshot,
                            "The image %s is not a snapshot!" % image.id)

from threading import Thread
from datetime import datetime
from time import sleep
from unittest2 import TestCase

from sedna.error import IllegalStateError
from sedna.openstack.util import SyncStateChecker


class SyncStateCheckerTest(TestCase):
    """The test suite for SyncStateChecker"""

    def __init__(self, mtheodName="runTest"):
        super(SyncStateCheckerTest, self).__init__(mtheodName)
        self.resource_is_ready = False
        self.expected_status = "ready"

    class DummyResource(object):
        """The dummy resource used in test case """
        def __init__(self):
            self.status = "creating"

    def dummy_get(self, resource):
        """The dummy getter function to get the expected status in test case"""
        if self.resource_is_ready:
            resource.status = self.expected_status

        return resource

    def test_check_status(self):
        """
        Test checker logic when the resource reaches expected status in time
        """
        expected_timeout = 5
        expected_interval = 1
        checker = SyncStateChecker(
            timeout=expected_timeout, interval=expected_interval)

        target_resource = SyncStateCheckerTest.DummyResource()

        def change_status():
            sleep(expected_timeout / 2)
            target_resource.status = self.expected_status

        Thread(target=change_status).start()

        start = datetime.now()
        resource = checker.wait_for_status(
            target_resource, self.expected_status, self.dummy_get)
        delta = datetime.now() - start

        self.assertEqual(self.expected_status, resource.status)
        self.assertGreater(expected_timeout + expected_interval, delta.seconds)

    def test_failed_to_reach_status(self):
        """
        Test checker logic when the resource doesn't expected status in time
        """
        expected_timeout = 5
        expected_interval = 1
        checker = SyncStateChecker(
            timeout=expected_timeout, interval=expected_interval)

        target_resource = SyncStateCheckerTest.DummyResource()

        start = datetime.now()

        with self.assertRaises(IllegalStateError):
            checker.wait_for_status(
                target_resource, self.expected_status, self.dummy_get)

        delta = datetime.now() - start

        self.assertGreaterEqual(
            expected_timeout + expected_interval * 1.5, delta.seconds)

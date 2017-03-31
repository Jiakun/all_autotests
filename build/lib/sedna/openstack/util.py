""" This module contains utilities used across openstack integration"""
from datetime import datetime
from time import sleep

from sedna.error import IllegalStateError, NoneReferenceError


class SyncStateChecker(object):
    """
    check whether the given resource reaches the expected status within given
    period
    """

    def __init__(self, timeout=30, interval=5):
        """
        Initialization.
        :param timeout: the period in seconds when the check should stop.
        Default is 30 seconds.
        :param interval: the interval between 2 checks in second. Default is 5.
        """
        if timeout < 1:
            raise ValueError("Illegal timeout %s" % timeout)
        if interval < 1 or interval > timeout:
            raise ValueError("Illegal check interval %s" % interval)

        self.timeout = timeout
        self.interval = interval

    def wait_for_status(self, resource, expected_status, getter):
        """
        Check the resource status periodically before the timeout is reached.
        :param resource: the resource show status is to check
        :param expected_status: the expected status the resource should reach
        :param getter: the method used to get the latest data of the resource
        :return: the latest resource data after the checking.
        :raise IllegalStateError: the error raises when the resource doesn't
        reach the exptected status within the timeout period.
        """
        if not resource:
            raise NoneReferenceError("resource to check can't be None!")

        if not hasattr(resource, "status"):
            raise ValueError(
                "resource to check %s has not attribute named status"
                % resource)

        start = datetime.now()

        while True:
            resource = getter(resource)
            if resource.status == expected_status:
                return resource

            delta = datetime.now() - start
            if delta.seconds > self.timeout:
                raise IllegalStateError(
                    "Failed to wait for resource %s to reach status %s "
                    "in %s sec"
                    % (resource, expected_status, delta))
            sleep(self.interval)

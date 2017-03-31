"""Test cases for sedna common module"""

from unittest2 import TestCase

from sedna.common import Service
from sedna.common import Result
from sedna.common import NodeResult
from sedna.common import Node

TEST_PORT = "10000"
TEST_SERVICE_NAME = "$$test_service_name$$"
TEST_METHOD = "$$test_method$$"
TEST_GROUP = "$$test_group$$"
TEST_IP = "$$test_ip$$"
TEST_ANALYSIS = "$$test_analysis$$"
TEST_SERVICE = Service()
TEST_STATUS = "$$test_status$$"
TEST_RESULT = Result(service=TEST_SERVICE, status=TEST_STATUS)


class ServiceTest(TestCase):
    """
    The test cases to check the value object behaviors like initialization and
    equality
    """

    def test_equalty(self):
        """
        The test case to check the equality of 2 Service objects
        """
        service1_1 =\
            Service(name=TEST_SERVICE_NAME, ip=TEST_IP,
                    methods=TEST_METHOD)
        service1_2 =\
            Service(name=TEST_SERVICE_NAME, ip=TEST_IP,
                    methods=TEST_METHOD)
        self.assertEqual(service1_1, service1_2)
        self.assertFalse(service1_1 != service1_2)
        self.assertFalse([service1_1, service1_1] != [service1_2, service1_2])
        self.assertFalse({"services": [service1_1, service1_1]} !=
                         {"services": [service1_2, service1_1]})
        # TODO check the negative cases

    def test_entires_init(self):
        """
        The test case to check the initialization approaches through parameters
        and dictionary entries
        """
        expected_service_name = TEST_SERVICE_NAME
        expected_ip = TEST_IP
        expected_methods = TEST_METHOD
        expected_service = Service(
                name=expected_service_name,
                ip=expected_ip,
                methods=expected_methods)

        service_dict = {
            "name": expected_service_name,
            "ip": expected_ip,
            "methods": expected_methods
        }
        actual_service = Service(**service_dict)

        self.assertEqual(expected_service, actual_service)


class ResultTest(TestCase):
    """
    The test cases to check the value object behaviors like initialization and
    equality
    """

    def test_equalty(self):
        """
        The test case to check the equality of 2 Result objects
        """
        result1_1 =\
            Result(service=TEST_SERVICE,
                   status=TEST_STATUS,
                   analysis=TEST_ANALYSIS)
        result1_2 =\
            Result(service=TEST_SERVICE,
                   status=TEST_STATUS,
                   analysis=TEST_ANALYSIS)
        self.assertEqual(result1_1, result1_2)
        self.assertFalse(result1_1 != result1_2)
        self.assertFalse([result1_1, result1_1] != [result1_2, result1_2])
        self.assertFalse({"results": [result1_1, result1_1]} !=
                         {"results": [result1_2, result1_1]})
        # TODO check the negative cases

    def test_entires_init(self):
        """
        The test case to check the initialization approaches
        through parameters and dictionary entries.
        """
        expected_service = TEST_SERVICE
        expected_status = TEST_STATUS
        expected_analysis = TEST_ANALYSIS
        expected_service = Service(
                expected_service,
                expected_status,
                expected_analysis)

        expected_result =\
            Result(service=expected_service,
                   status=expected_status,
                   analysis=expected_analysis)

        result_dict = {
            "service": expected_service,
            "status": TEST_STATUS,
            "analysis": TEST_ANALYSIS
        }
        actual_result = Result(**result_dict)

        self.assertEqual(expected_result, actual_result)


class NodeResultTest(TestCase):
    """
    The test cases to check the value object behaviors like initialization and
    equality
    """

    def test_equalty(self):
        """
        The test case to check the equality of 2 NodeResult objects
        """
        node_result1_1 =\
            NodeResult(group=TEST_GROUP, ip=TEST_IP, result=[TEST_RESULT])
        node_result1_2 =\
            NodeResult(group=TEST_GROUP, ip=TEST_IP, result=[TEST_RESULT])
        self.assertEqual(node_result1_1, node_result1_2)
        self.assertFalse(node_result1_1 != node_result1_2)
        self.assertFalse([node_result1_1, node_result1_1] !=
                         [node_result1_2, node_result1_2])
        self.assertFalse({"node_result": [node_result1_1, node_result1_1]} !=
                         {"node_result": [node_result1_2, node_result1_1]})
        # TODO check the negative cases

    def test_entires_init(self):
        """
        The test case to check the initialization approaches through parameters
        and dictionary entries
        """
        expected_group = TEST_GROUP
        expected_ip = TEST_IP
        expected_node_result = NodeResult(group=TEST_GROUP,
                                          ip=TEST_IP,
                                          result=[TEST_RESULT])

        node_result_dict = {
            "group": expected_group,
            "ip": expected_ip,
            "result": [TEST_RESULT]
        }
        actual_node_result = NodeResult(**node_result_dict)

        self.assertEqual(expected_node_result, actual_node_result)


class NodeTest(TestCase):
    """
    The test cases to check the value object behaviors like initialization and
    equality
    """

    def test_equalty(self):
        """
        The test case to check the equality of 2 Node objects
        """
        node1_1 = Node(group=TEST_GROUP, ip=TEST_IP, services=[TEST_SERVICE])
        node1_2 = Node(group=TEST_GROUP, ip=TEST_IP, services=[TEST_SERVICE])
        self.assertEqual(node1_1, node1_2)
        self.assertFalse(node1_1 != node1_2)
        self.assertFalse([node1_1, node1_1] != [node1_2, node1_2])
        self.assertFalse({"node": [node1_1, node1_1]} !=
                         {"node": [node1_2, node1_1]})
        # TODO check the negative cases

    def test_entires_init(self):
        """
        The test case to check the initialization approaches through parameters
        and dictionary entries
        """
        expected_group = TEST_GROUP
        expected_ip = TEST_IP
        expected_services = [TEST_SERVICE]
        expected_node = Node(
                group=expected_group,
                ip=expected_ip,
                services=expected_services)

        node_dict = {
            "group": expected_group,
            "ip": expected_ip,
            "services": [TEST_SERVICE]
        }
        actual_node = Node(**node_dict)

        self.assertEqual(expected_node, actual_node)

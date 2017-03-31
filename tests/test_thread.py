from unittest2 import TestCase
import random
import logging

from sedna.common import Service
from sedna.common import Node
from sedna.config import SednaConfig
from sedna.master import XmlRPCClient
from sedna.thread import CheckerThread

TEST_IP = "127.0.0.1"
TEST_SERVICE_NAME = "$$test_name$$"
TEST_METHOD = "$$test_method$$"
TEST_GROUP = "$$test_group$$"
TEST_STATUS = "$$test_status$$"
TEST_ANALYSIS = "$$test_analysis$$"

LOG = logging.getLogger("tester")


class CheckerThreadTest(TestCase):
    def setUp(self):
        self.TEST_PORT = str(random.randint(10000, 65535))
        expected_service = Service(name=TEST_SERVICE_NAME, ip=TEST_IP,
                                   methods=TEST_METHOD)
        self.expected_services = [expected_service, expected_service]
        expected_node = Node(group=TEST_GROUP, ip=TEST_IP,
                             services=self.expected_services)
        self.expected_node = expected_node
        self.expected_nodes = [expected_node, expected_node, expected_node]

        self.mocked_xml_rpc_client = CheckerThreadTest._MockedXmlRPCClient()

        self.sedna_config_value =\
            SednaConfig(port=self.TEST_PORT, nodes=self.expected_nodes)

    def test_run_thread(self):
        threads = []
        results = []
        for node in self.expected_nodes:
            t = CheckerThread(node=node, rpc_client=self.mocked_xml_rpc_client,
                              sedna_config_value=self.sedna_config_value)
            threads.append(t)
        for t in threads:
            t.start()
            t.join()

        for t in threads:
            results.append(t.get_result())

        self.assertTrue(self.mocked_xml_rpc_client.is_rpc_client_called,
                        "The XMLRPCClient is not called!")
        self.assertEquals(self.expected_services,
                          self.mocked_xml_rpc_client.node_services)
        self.assertEquals(len(results),
                          len(self.expected_nodes),
                          "Fail to get result from all nodes!")

    class _MockedXmlRPCClient(XmlRPCClient):
        """
        The MockedXmlRPCClient inheriting from XmlRPCClient contains stubs to
        check the communication inner status
        """
        def __init__(self):
            self.is_rpc_client_called = False
            self.node_services = None
            self.sedna_kill_service_config_value = None

            super(CheckerThreadTest._MockedXmlRPCClient, self).__init__()

        def connect(self, ip, group, port, node_services):
            """
            The method inheriting from NodeSampler can
            check whether the method called by Master
            and mock the return results of sampler.
            :param ip:
            :param group:
            :param port:
            :param node_services:
            :return: return the mocked results to check the communication
            """
            self.is_rpc_client_called = True
            self.node_services = node_services

            self.sample(services=node_services, name=TEST_METHOD,
                        klass=CheckerThreadTest.MockedMethodChecker)

            return []

    class MockedMethodChecker(object):
        """
        The MockedMethodChecker to return the mock service-status result.
        """

        def __init__(self):
            self.is_mock_checker_called = False
            self.service = None

        def execute(self, service):
            self.is_mock_checker_called = True
            self.service = service

            return [TEST_STATUS, TEST_ANALYSIS]

from threading import Thread
from unittest2 import TestCase
import random
import logging

from sedna.common import Node
from sedna.common import Service
from sedna.common import Result
from sedna.master import Master
from sedna.config import SednaConfig
from sedna.sampler import NodeSampler
from sedna.server import NodeServer
from tests.test_master import MockedMethodChecker

TEST_METHOD = "$$test_method$$"
TEST_SERVICE_NAME = "$$test_service_name$$"
TEST_GROUP = "$$test_group$$"
TEST_STATUS = "$$test_status$$"
TEST_ANALYSIS = "$$test_analysis$$"
TEST_IP = "127.0.0.1"

LOG = logging.getLogger("tester")


class CommunicationTest(TestCase):
    """
    The test case to check the communication between master and sampler
    """
    def test(self):
        TEST_PORT = str(random.randint(10000, 65535))
        expected_services = [
            Service(name=TEST_SERVICE_NAME,
                    ip="localhost",
                    methods=TEST_METHOD)
        ]

        expected_nodes = [Node(services=expected_services, ip="localhost")]

        mocked_sampler = CommunicationTest._MockedNodeSampler()
        mocked_sampler.register_service(TEST_METHOD, MockedMethodChecker)
        server = NodeServer(port=int(TEST_PORT), sampler=mocked_sampler)

        def start_server():
            server.start()

        server_thread = Thread(target=start_server)
        server_thread.setDaemon(True)
        server_thread.start()

        sedna_config_object = SednaConfig()
        sedna_config_object.port = TEST_PORT
        sedna_config_object.nodes = expected_nodes
        master = Master()
        master.verify_nodes(sedna_config_object)
        self.assertTrue(mocked_sampler.is_sample_called,
                        "The sampler is no called!")
        self.assertSequenceEqual(expected_services,
                                 mocked_sampler.actual_services)

    class _MockedNodeSampler(NodeSampler):
        """
        The mocked NodeSampler inheriting from NodeSampler contains stubs to
        check the communication inner status
        """

        def __init__(self):
            self.is_sample_called = False
            self.actual_services = None
            super(CommunicationTest._MockedNodeSampler, self).__init__()

        def sample(self, services):
            self.is_sample_called = True
            self.actual_services = services
            # TODO return the mocked results to check the communication
            return []


class SednaIntegrateTest(TestCase):
    """
    The test cases to test the Conmunicate between Master
    and Sampler.
    """
    def setUp(self):
        self.TEST_PORT = str(random.randint(10000, 65535))
        self.expected_service =\
            Service(name=TEST_SERVICE_NAME,
                    ip=TEST_IP,
                    methods=TEST_METHOD)
        self.expected_services = [self.expected_service, self.expected_service]
        self.expected_node = Node(group=TEST_GROUP,
                                  ip=TEST_IP,
                                  services=self.expected_services)
        self.expected_nodes = [self.expected_node]

        node_sampler = NodeSampler()
        node_sampler_server = \
            NodeServer(port=int(self.TEST_PORT), sampler=node_sampler)

        def start_server():
            node_sampler_server.start()

        server_thread = Thread(target=start_server)
        server_thread.setDaemon(True)
        server_thread.start()

        node_sampler.register_service(TEST_METHOD, MockedMethodChecker)

    def test_communicate(self):
        sedna_config_value =\
            SednaConfig(port=self.TEST_PORT, nodes=self.expected_nodes)

        LOG.info("{port:%s, nodes:%s}" %
                 (sedna_config_value.port, sedna_config_value.nodes))

        master = Master()
        results = master.verify_nodes(sedna_config_value)
        LOG.info("Sampler Server results: %s" % results)

        self.assertEquals(results[0].group, self.expected_node.group,
                          'Fail when test_get_nodes information')
        self.assertEquals(results[0].ip, self.expected_node.ip,
                          'Fail when test_get_nodes information')

        expected_result =\
            Result(status=TEST_STATUS,
                   service=self.expected_service,
                   analysis=TEST_ANALYSIS)
        for result in results[0].result:
            self.assertEquals(result, expected_result)

    def tearDown(self):
        pass

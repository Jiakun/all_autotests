from unittest2 import TestCase
from threading import Thread
import random
import logging

from sedna.master import Master
from sedna.server import NodeServer
from sedna.common import Service
from sedna.common import Node
from sedna.config import SednaConfig, KillerConfig, ServiceCommandConfig, \
    HAConfig
from sedna.master import XmlRPCClient

TEST_IP = "127.0.0.1"
TEST_SERVICE_NAME = "$$test_name$$"
TEST_METHOD = "$$test_method$$"
TEST_GROUP = "$$test_group$$"
TEST_STATUS = "$$test_status$$"
TEST_ANALYSIS = "$$test_analysis$$"

LOG = logging.getLogger("tester")


class XmlRPCClientTest(TestCase):
    """
    The test cases to test the capibility of xmlrpclib.
    """
    def setUp(self):
        self.TEST_PORT = str(random.randint(10000, 65535))
        self._mock_sampler = XmlRPCClientTest._MockedSampler()

        self._mock_server = \
            NodeServer(port=int(self.TEST_PORT),
                       sampler=self._mock_sampler)

        def start_server():
            self._mock_server.start()

        server_thread = Thread(target=start_server)
        server_thread.setDaemon(True)
        server_thread.start()

        self.xmlrpc_client = XmlRPCClient()
        self.fake_node_services =\
            [Service(name="$$test_service_a$$",
                     ip=TEST_IP, methods=TEST_METHOD),
             Service(name="$$test_service_b$$",
                     ip=TEST_IP, methods=TEST_METHOD)]

        self.expected_respond = [{"name": "$$test_service_a$$",
                                  "ip": TEST_IP,
                                  "methods": TEST_METHOD},
                                 {"name": "$$test_service_b$$",
                                  "ip": TEST_IP,
                                  "methods": TEST_METHOD}]
        self.sedna_kill_service_config_value = None

    def test_connect(self):
        """
        The test case to check the capability of xmlrpclib
        when "ip" attribute of Service obj is string type.
        :return:
        """
        node_result = self.xmlrpc_client.connect(
            ip=TEST_IP, group=TEST_GROUP,
            port=self.TEST_PORT, node_services=self.fake_node_services)
        self.assertEquals(node_result, self.expected_respond)

    def test_connect_kill_service(self):
        """
        Test the variable passing
        :return:
        """
        self.sedna_kill_service_config_value =\
            KillerConfig(port=self.TEST_PORT, ip=TEST_IP,
                         services=self.fake_node_services)

        node_result = self.xmlrpc_client.connect_kill_service(
            self.sedna_kill_service_config_value)
        results = []
        for result in node_result:
            results.append(result["service"])
        self.assertEquals(results, self.expected_respond)

    def test_connect_service_command(self):
        """
        :return: 'status' and 'analysis'
        """
        fake_service = {'name': "$$test_service_a$$",
                        'ip': TEST_IP,
                        'methods': "systemd"
                        }
        self.sedna_service_command_config = ServiceCommandConfig(
            operation="restart", service=fake_service,
            port=self.TEST_PORT, ip=TEST_IP)
        node_result = self.xmlrpc_client.connect_service_command(
            self.sedna_service_command_config)
        self.assertEquals(len(node_result), 2)

    class _MockedSampler(XmlRPCClient):
        """
        The mocked NodeSampler inheriting from NodeSampler of XmlRPCClient
        contains stubs to check the communication inner status.
        """
        def sample(self, services=None, name=None, klass=None):
            return services


class HATest(TestCase):
    def setUp(self):
        self.TEST_PORT = str(random.randint(10000, 65535))
        self._mock_xmlrpc_client = self._MockedXmlRPCClient()

        self._mock_server = \
            NodeServer(port=int(self.TEST_PORT))

        def start_server():
            self._mock_server.start()

        server_thread = Thread(target=start_server)
        server_thread.setDaemon(True)
        server_thread.start()

        self.scenario = "RouterCreate"

        self.fake_service = {'name': "$$test_service_a$$",
                             'ip': TEST_IP,
                             'methods': "systemd"
                             }
        self.ha_config = HAConfig(ip=TEST_IP, port=self.TEST_PORT,
                                  scenario=self.scenario,
                                  service=self.fake_service,
                                  operation="kill")

    def test_connect_ha_scenario(self):
        try:
            self._mock_xmlrpc_client.connect_ha_scenario(self.ha_config)
        except:
            raise Exception

        if self._mock_xmlrpc_client.connect_ha_scenario_status(self.ha_config):
            return
        else:
            raise Exception

    class _MockedXmlRPCClient(XmlRPCClient):
        def connect_ha_scenario(self, ha_config):
            return ha_config.scenario

        def connect_ha_scenario_status(self, ha_config):
            return True


class MasterTest(TestCase):
    """
    The test case to test the Master Class.
    """
    def setUp(self):
        """
        The wrapper of sample method to build a fake Sampler and a fake
        Sedna config file with the relevant information of its test case.
        """
        self.TEST_PORT = str(random.randint(10000, 65535))
        expected_service = Service(name=TEST_SERVICE_NAME, ip=TEST_IP,
                                   methods=TEST_METHOD)
        self.expected_services = [expected_service, expected_service]
        expected_node = Node(group=TEST_GROUP, ip=TEST_IP,
                             services=self.expected_services)
        self.expected_nodes = [expected_node, expected_node, expected_node]

        self.mocked_xml_rpc_client = MasterTest._MockedXmlRPCClient()

        self.sedna_config_value =\
            SednaConfig(port=self.TEST_PORT, nodes=self.expected_nodes)

        self.sedna_kill_service_config_value = None

        self.sedna_service_command_config = None

    def test_master_all_node(self):
        """
        The test case to test whether master class can set up
        a Master object and get result from all node.
        :return:
        """
        self.master = Master(rpc_client=self.mocked_xml_rpc_client)
        master_verify_result =\
            self.master.verify_nodes(
                sedna_config_value=self.sedna_config_value)

        self.assertTrue(self.mocked_xml_rpc_client.is_rpc_client_called,
                        "The XMLRPCClient is not called!")
        self.assertEquals(self.expected_services,
                          self.mocked_xml_rpc_client.node_services)

        self.assertEquals(len(master_verify_result),
                          len(self.expected_nodes),
                          "Fail to get result from all nodes!")

    def test_master_with_exception(self):
        # TODO: return None for error
        self.master = Master()

        # with self.assertRaises(Exception):
        #        self.master.verify_nodes(
        #            sedna_config_value=self.sedna_config_value)

    def test_kill_service(self):
        """
        :return:
        """
        self.master = Master(rpc_client=self.mocked_xml_rpc_client)
        self.sedna_kill_service_config_value = \
            KillerConfig(port=self.TEST_PORT, ip=TEST_IP,
                         services=self.expected_services)
        master_kill_service_results =\
            self.master.kill_service(self.sedna_kill_service_config_value)

        self.assertTrue(self.mocked_xml_rpc_client.is_rpc_client_called,
                        "The XMLRPCClient is not called!")

        results = self.mocked_xml_rpc_client.killer.kill_services(
            self.expected_services)
        for result, service in results, self.expected_services:
            self.assertEquals(result, service)

        self.assertEquals(len(master_kill_service_results),
                          len(self.expected_services),
                          "Fail to get result from all nodes!")

    def test_run_service_command(self):
        self.master = Master(rpc_client=self.mocked_xml_rpc_client)
        fake_service = Service(name=TEST_SERVICE_NAME, ip=TEST_IP,
                               methods="systemd")
        self.sedna_service_command_config = ServiceCommandConfig(
            operation="restart", port=self.TEST_PORT,
            service=fake_service, ip=TEST_IP)
        master_service_command_result = \
            self.master.run_service_command(self.sedna_service_command_config)

        self.assertTrue(self.mocked_xml_rpc_client.is_rpc_client_called,
                        "The XMLRPCClient is not called!")

        self.assertEquals(len(master_service_command_result), 2,
                          "Fail to get result from all nodes!")

    def test_run_ha_scenario(self):
        self.master = Master(rpc_client=self.mocked_xml_rpc_client)
        fake_service = Service(name=TEST_SERVICE_NAME, ip=TEST_IP,
                               methods="systemd")
        scenario = "VolumeCreate"
        ha_config = HAConfig(ip=TEST_IP, port=self.TEST_PORT,
                             scenario=scenario, service=fake_service,
                             operation="kill")
        result = self.master.run_ha_scenario(ha_config=ha_config)
        self.assertTrue(self.mocked_xml_rpc_client.is_rpc_client_called,
                        "The XMLRPCClient is not called!")
        self.assertEquals(result, 0,
                          "Fail to get result from all nodes!")

    def teardown(self):
        pass

    class _MockedXmlRPCClient(XmlRPCClient):
        """
        The MockedXmlRPCClient inheriting from XmlRPCClient contains stubs to
        check the communication inner status
        """
        def __init__(self):
            self.is_rpc_client_called = False
            self.node_services = None
            self.sedna_kill_service_config_value = None
            self.register_service = None

            super(MasterTest._MockedXmlRPCClient, self).__init__()

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
                        klass=MockedMethodChecker)

            return []

        def connect_kill_service(self, sedna_kill_service_config_value):
            self.is_rpc_client_called = True
            return self.kill(services=sedna_kill_service_config_value.services)

        def connect_service_command(self, s_command_config):
            self.is_rpc_client_called = True
            return self.run_service_command(
                service=s_command_config.service,
                operation=s_command_config.operation)

        def connect_ha_scenario(self, ha_config, times=None):
            self.is_rpc_client_called = True
            result = self.run_ha_scenario(
                scenario_class=ha_config.scenario, times=1)
            return result


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


class MasterRestfulTest(TestCase):
    """
    The test cases to test MasterRestfulTest.
    """
    def setUp(self):
        pass

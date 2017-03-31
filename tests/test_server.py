from unittest2 import TestCase
from threading import Thread
from xmlrpclib import ServerProxy
import random
import logging

from sedna.server import NodeServer
from sedna.sampler import NodeSampler


TEST_IP = "127.0.0.1"
TEST_SERVICE_NAME = "openstack-$$test_name$$.service"
TEST_METHOD = "$$test_method$$"

LOG = logging.getLogger("tester")


class NodeServerTest(TestCase):
    """
    The test cases to test the capacity of Server start on some occassions.
    """
    def setUp(self):
        self.TEST_PORT = str(random.randint(10000, 65535))
        _mocked_node_sampler = _MockedNodeSampler()
        self.node_sampler_server =\
            NodeServer(port=self.TEST_PORT,
                       sampler=_mocked_node_sampler)

        def start_server():
            self.node_sampler_server.start()

        server_thread = Thread(target=start_server)
        server_thread.setDaemon(True)

        server_thread.start()

    def test_sample_server(self):
        """
        This test case to test sampler response.
        :return:
        """
        fake_uri = "http://localhost:" + self.TEST_PORT + "/"
        proxy = ServerProxy(fake_uri)

        dict_service_a = {"name": "$$test_service_a$$",
                          "ip": TEST_IP,
                          "methods": TEST_METHOD}
        dict_service_b = {"name": "$$test_service_b$$",
                          "ip": TEST_IP,
                          "methods": TEST_METHOD}

        fake_services = [dict_service_a, dict_service_b]
        self.assertEquals(proxy.sample(fake_services), 1,
                          "Failed to return result from sampler.")

    def test_run_service_command(self):
        """
        :return: 'status' and 'analysis'
        """
        fake_uri = "http://localhost:" + self.TEST_PORT + "/"
        proxy = ServerProxy(fake_uri)
        dict_service_a = {"name": "$$test_service_a$$",
                          "ip": TEST_IP,
                          "methods": "systemd"}
        operation = "restart"
        result = proxy.run_service_command(dict_service_a, operation)
        self.assertEquals(len(result), 2,
                          "Failed to return result from sampler.")

    def tearDown(self):
        pass


class HATest(TestCase):
    def setUp(self):
        self.TEST_PORT = str(random.randint(10000, 65535))
        self.node_sampler_server =\
            NodeServer(port=self.TEST_PORT)

        def start_server():
            self.node_sampler_server.start()

        server_thread = Thread(target=start_server)
        server_thread.setDaemon(True)

        server_thread.start()

    def test_ha_scenario_with_class_error(self):
        fake_uri = "http://localhost:" + self.TEST_PORT + "/"
        proxy = ServerProxy(fake_uri)

        scenario_class = "Test"
        times = "1"
        result = proxy.run_ha_scenario(scenario_class, times)

        self.assertEquals(result, -1,
                          "Failed to return result from server.")

    def test_run_ha_scenario_positive(self):
        fake_uri = "http://localhost:" + self.TEST_PORT + "/"
        proxy = ServerProxy(fake_uri)

        scenario_class = "VolumeCreate"
        times = "1"
        result = proxy.run_ha_scenario(scenario_class, times)

        self.assertEquals(result, 0,
                          "Failed to return result from server.")

    def test_get_ha_daemon_thread(self):
        fake_uri = "http://localhost:" + self.TEST_PORT + "/"
        proxy = ServerProxy(fake_uri)

        scenario_class = "VolumeCreate"
        times = "1"
        proxy.run_ha_scenario(scenario_class, times)

        scenario = proxy.get_ha_daemon_thread()

        self.assertEquals(scenario, scenario_class,
                          "Failed to return result from sampler.")

    def test_get_ha_scenario_status(self):
        fake_uri = "http://localhost:" + self.TEST_PORT + "/"
        proxy = ServerProxy(fake_uri)

        scenario_class = "VolumeCreate"
        times = "1"
        proxy.run_ha_scenario(scenario_class, times)

        status = proxy.get_ha_scenario_status()

        if status not in [True, False]:
            raise Exception("Failed to return result from sampler.")


class _MockedNodeSampler(NodeSampler):
    """
    The mocked NodeSampler inheriting from NodeSampler contains stubs to
    imitate sampler class.
    """
    def sample(self, services, flag=None):
        return 1

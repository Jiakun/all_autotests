from unittest2 import TestCase
from threading import Thread
from xmlrpclib import ServerProxy
import random
import logging

from sedna.ha.services import ServiceKiller, ServiceCommand, \
    NodeHATest
from sedna.server import NodeServer

from sedna.observer import ObserverInfoType, LoggerObserver, \
    Observable

TEST_SERVICE_NAME = "openstack-glance-api.service"
TEST_IP = "127.0.0.1"
TEST_METHOD = "KILL"

LOG = logging.getLogger("tester")


class ServiceKillerTest(TestCase):
    """
    The test cases to test class NodeSampler
    """
    def setUp(self):
        self.TEST_PORT = str(random.randint(10000, 65535))
        _mocked_node_killer = _MockedNodeKiller()
        self.node_server = \
            NodeServer(port=self.TEST_PORT,
                       killer=_mocked_node_killer)

        def start_server():
            self.node_server.start()

        server_thread = Thread(target=start_server)
        server_thread.setDaemon(True)

        server_thread.start()

        self.service_killer = ServiceKiller()

    def test_kill_services(self):
        """
        Test case to test kill multiple services by service names on a node.
        :return:
        """
        fake_uri = "http://localhost:" + self.TEST_PORT + "/"
        proxy = ServerProxy(fake_uri)

        dict_service_a = {"name": TEST_SERVICE_NAME,
                          "ip": TEST_IP,
                          "methods": TEST_METHOD}
        fake_services = [dict_service_a]
        self.assertEquals(proxy.kill(fake_services), 0,
                          "Failed to return result from sampler.")

    def tearDown(self):
        pass


class ServiceCommandTest(TestCase):
    """
    The test cases to test class SystemedCommand
    """
    def setUp(self):
        self.TEST_PORT = str(random.randint(10000, 65535))
        _mocked_node_s_commander = _MockedNodeServiceCommander()
        self.node_server =\
            NodeServer(port=self.TEST_PORT,
                       s_commander=_mocked_node_s_commander)

        def start_server():
            self.node_server.start()

        server_thread = Thread(target=start_server)
        server_thread.setDaemon(True)

        server_thread.start()

        self.service_command = ServiceCommand()

    def test_execute(self):
        """
        TODO: test does not pass without the command
        Test case to test "start", "restart", "stop" a service by
        its names on a node.
        :return:
        """
        fake_uri = "http://localhost:" + self.TEST_PORT + "/"
        proxy = ServerProxy(fake_uri)

        dict_service_a = {"name": TEST_SERVICE_NAME,
                          "ip": TEST_IP,
                          "methods": "systemd"}
        fake_services = dict_service_a
        self.assertEquals(
            len(proxy.run_service_command(fake_services, "start")), 2,
            "Failed to return result from sampler.")

        self.assertEquals(
            len(proxy.run_service_command(fake_services, "restart")), 2,
            "Failed to return result from sampler.")

        self.assertEquals(
            len(proxy.run_service_command(fake_services, "stop")), 2,
            "Failed to return result from sampler.")

    def tearDown(self):
        pass


class NodeHATestTest(TestCase):
    def setUp(self):
        self.TEST_PORT = str(random.randint(10000, 65535))
        self.node_server =\
            NodeServer(port=self.TEST_PORT)

        def start_server():
            self.node_server.start()

        server_thread = Thread(target=start_server)
        server_thread.setDaemon(True)

        server_thread.start()

        self.observable = Observable()
        self.step_observable = Observable()
        self.observer = LoggerObserver(LOG, ObserverInfoType.HA)
        self.step_observer = LoggerObserver(LOG, ObserverInfoType.SCENARIO_STEP)
        self.observable.register_observer(self.observer)
        self.step_observable.register_observer(self.step_observer)

        self.ha_tester = NodeHATest(observable=self.observable,
                                    step_observable=self.observable)

    def test_run_ha_scenario(self):
        self.assertEqual(
            self.ha_tester.run_ha_scenario(
                scenario_class="HAVolumeCreateScenario", times="1"),
            0)

    def tearDown(self):
        pass


class _MockedNodeServiceCommander:
    def __init__(self):
        pass

    def execute(self, service=None, s_command=None):
        return [0]


class _MockedNodeKiller:
    def __init__(self):
        pass

    def kill_services(self, services=None):
        return 0

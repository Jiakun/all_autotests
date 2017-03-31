from unittest2 import TestCase
from threading import Thread
from xmlrpclib import ServerProxy
import random
import logging

from sedna.server import NodeServer
from sedna.sampler import NodeSampler
from sedna.sampler import SystemdChecker
from sedna.sampler import PacemakerChecker
from sedna.sampler import InitdChecker
from sedna.common import Service

TEST_IP = "127.0.0.1"
TEST_SERVICE_NAME = "openstack-$$test_name$$.service"
TEST_METHOD = "$$test_method$$"

LOG = logging.getLogger("tester")


class NodeSamplerTest(TestCase):
    """
    The test cases to test class NodeSampler
    """
    def setUp(self):
        self.node_sampler = NodeSampler()

    def test_systemd_unknown_service_name_checker(self):
        self.node_sampler.register_service("systemd", SystemdChecker)
        self.service = Service(name=TEST_SERVICE_NAME,
                               methods="systemd",
                               ip=TEST_IP)
        self.fake_services = [self.service]
        results = self.node_sampler.sample(services=self.fake_services)
        self.assertEquals(len(results), len(self.fake_services))

    def test_systemd_positive_checker(self):
        self.node_sampler.register_service("systemd", SystemdChecker)
        self.service = Service(name="openstack-nova-api.service",
                               methods="systemd",
                               ip=TEST_IP)
        self.fake_services = [self.service]
        results = self.node_sampler.sample(services=self.fake_services)
        self.assertEquals(len(results), len(self.fake_services))

    def test_pacemaker_unknown_service_name_checker(self):
        self.node_sampler.register_service("pacemaker", PacemakerChecker)
        self.service = Service(name=TEST_SERVICE_NAME,
                               methods="pacemaker",
                               ip=TEST_IP)
        self.fake_services = [self.service]
        results = self.node_sampler.sample(services=self.fake_services)
        self.assertEquals(len(results), len(self.fake_services))

    def test_pacemaker_service_name_without_openstack_checker(self):
        self.node_sampler.register_service("pacemaker", PacemakerChecker)
        self.service = Service(name="$$test_name$$",
                               methods="pacemaker",
                               ip=TEST_IP)
        self.fake_services = [self.service]
        results = self.node_sampler.sample(services=self.fake_services)
        self.assertEquals(len(results), len(self.fake_services))

    def test_pacemaker_positive_checker(self):
        self.node_sampler.register_service("pacemaker", PacemakerChecker)
        self.service = Service(name="openstack-nova-api.service",
                               methods="pacemaker",
                               ip=TEST_IP)
        self.fake_services = [self.service]
        results = self.node_sampler.sample(services=self.fake_services)
        self.assertEquals(len(results), len(self.fake_services))

    def test_initd_checker(self):
        self.node_sampler.register_service("init.d", InitdChecker)
        self.service = Service(name=TEST_SERVICE_NAME,
                               methods="init.d",
                               ip=TEST_IP)
        self.fake_services = [self.service]
        with self.assertRaises(NotImplementedError):
            self.node_sampler.sample(services=self.fake_services)

    def test_unknown_checker(self):
        self.service = Service(name=TEST_SERVICE_NAME,
                               methods="unknown_checker",
                               ip=TEST_IP)
        self.fake_services = [self.service]
        with self.assertRaises(Exception):
            self.node_sampler.sample(services=self.fake_services)


class NodeSamplerServerStartTest(TestCase):
    """
    The test cases to test class NodeSamplerServer.
    """
    def setUp(self):
        self.TEST_PORT = str(random.randint(10000, 65535))
        _mocked_node_sampler = _MockedNodeSampler()
        self.node_sampler_server =\
            NodeServer(port=self.TEST_PORT,
                       sampler=_mocked_node_sampler)

    def test_listen_port(self):
        """
        The test case to test the server
        created by NodeSamplerServer class.
        :return:
        """

        def start_server():
            self.node_sampler_server.start()

        server_thread = Thread(target=start_server)
        server_thread.setDaemon(True)
        server_thread.start()

        fake_uri = "http://localhost:" + self.TEST_PORT + "/"
        proxy = ServerProxy(fake_uri)

        service_a = Service(name="$$service_a$$",
                            methods=TEST_METHOD,
                            ip=TEST_IP)
        service_b = Service(name="$$service_b$$",
                            methods=TEST_METHOD,
                            ip=TEST_IP)
        service_c = Service(name="$$service_c$$",
                            methods=TEST_METHOD,
                            ip=TEST_IP)
        fake_services = [service_a, service_b, service_c]
        self.assertEquals(
            proxy.sample(fake_services), 1,
            "NodeSamplerServer cannot create object.")


class _MockedNodeSampler(NodeSampler):
    """
    The mocked NodeSampler inheriting from NodeSampler contains stubs to
    imitate sampler class.
    """
    def sample(self, services, flag=None):
        return 1

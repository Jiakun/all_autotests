from unittest import TestCase

from threading import Thread
import requests
import mock

from sedna.common import NodeResult
from sedna.common import Result
from sedna.common import Service
from sedna.rest.master import MasterRestful
from sedna.rest.master import run
from sedna.rest.master import PORT


TEST_NAME = "$$test_name$$"
TEST_METHOD = "$$test_method$$"
TEST_GROUP = "$$test_group$$"
TEST_IP = "$$test_ip$$"
TEST_STATUS = "$$test_status$$"


class ServiceCheckerRestTest(TestCase):
    """
    The test cases to test code in rest_1.py.
    """
    def setUp(self):
        expected_service = Service(name=TEST_NAME, ip=TEST_IP,
                                   methods=TEST_METHOD)
        expected_result = Result(service=expected_service, status=TEST_STATUS)
        expected_results = [expected_result]

        node_result = NodeResult(group=TEST_GROUP, ip=TEST_IP,
                                 result=expected_results)
        self.fake_results = [node_result]

        self.master_restful = MasterRestful()

        dict_service = {'name': TEST_NAME,
                        'ip': TEST_IP,
                        'methods': TEST_METHOD
                        }
        self.service_fake_result = {'status': "status",
                                    'service': dict_service
                                    }
        self.kill_fake_result = [self.service_fake_result]

        def start_rest_server():
            run()

        server_thread = Thread(target=start_rest_server)
        server_thread.setDaemon(True)

        server_thread.start()

    @mock.patch.object(MasterRestful, 'get_results')
    def test_restful_get_all(self, mock_get_results):

        mock_get_results.return_value = self.fake_results
        self.assertEquals(self.master_restful.get_results(), self.fake_results)

        result = requests.get('http://localhost:' + str(PORT) +
                              '/master/api/v1.0/results')
        self.assertEquals(result.status_code, 200)

        self.assertGreater(len(result.text), 0)

    @mock.patch.object(MasterRestful, 'get_kill_service_results')
    def test_get_kill_results(self, mock_get_results):
        mock_get_results.return_value = self.kill_fake_result
        kill_result = self.master_restful.get_kill_service_results()
        self.assertEqual(kill_result, self.kill_fake_result)

        result = requests.get('http://localhost:' + str(PORT) +
                              '/master/api/v1.0/service_command/'
                              'name=openstack-nova-consoleauth.service&'
                              'ip=10.0.1.42&operation=kill')
        self.assertEqual(result.status_code, 200)

        self.assertGreater(len(result.text), 0)

    @mock.patch.object(MasterRestful, 'get_service_command_results')
    def test_get_systemed_restart_result(self, mock_get_results):
        mock_get_results.return_value = self.service_fake_result
        restart_result = self.master_restful.get_service_command_results()
        self.assertEqual(restart_result, self.service_fake_result)

        result = requests.get('http://localhost:' + str(PORT) +
                              '/master/api/v1.0/service_command/'
                              'name=openstack-nova-consoleauth.service&'
                              'ip=10.0.1.42&operation=restart')
        self.assertEqual(result.status_code, 200)

    @mock.patch.object(MasterRestful, 'get_service_command_results')
    def test_get_systemed_start_result(self, mock_get_results):
        mock_get_results.return_value = self.service_fake_result
        restart_result = self.master_restful.get_service_command_results()
        self.assertEqual(restart_result, self.service_fake_result)

        result = requests.get('http://localhost:' + str(PORT) +
                              '/master/api/v1.0/service_command/'
                              'name=openstack-nova-consoleauth.service&'
                              'ip=10.0.1.42&operation=start')
        self.assertEqual(result.status_code, 200)

    @mock.patch.object(MasterRestful, 'get_service_command_results')
    def test_get_systemed_stop_result(self, mock_get_results):
        mock_get_results.return_value = self.service_fake_result
        restart_result = self.master_restful.get_service_command_results()
        self.assertEqual(restart_result, self.service_fake_result)

        result = requests.get('http://localhost:' + str(PORT) +
                              '/master/api/v1.0/service_command/'
                              'name=openstack-nova-consoleauth.service&'
                              'ip=10.0.1.42&operation=stop')
        self.assertEqual(result.status_code, 200)


class ScenarioRunnerRestTest(TestCase):
    """
    The test cases to test code in rest_1.py.
    """

    def setUp(self):

        def start_rest_server():
            run()

        server_thread = Thread(target=start_rest_server)
        server_thread.setDaemon(True)

        server_thread.start()

    def test_scenario_tests(self):
        request_result = requests.get(
            'http://localhost:' + str(PORT) + '/master/api/v1.0/run_scenarios')
        self.assertEquals(request_result.status_code, 200)


class HARestTest(TestCase):
    def setUp(self):
        def start_rest_server():
            run()

        self.master_restful = MasterRestful()

        server_thread = Thread(target=start_rest_server)
        server_thread.setDaemon(True)

        server_thread.start()

    @mock.patch.object(MasterRestful, 'get_ha_results')
    def test_ha_tests(self, mock_get_results):
        mock_get_results.return_value = None
        result = self.master_restful.get_ha_results()
        self.assertEquals(result, None)

        result = requests.get('http://localhost:' + str(PORT) +
                              '/master/api/v1.0/ha/'
                              'name=openstack-nova-consoleauth.service&'
                              'ip=10.0.1.42&operation=stop')
        self.assertEquals(result.status_code, 200)

from unittest2 import TestCase
import sys
import os

from sedna.common import NodeResult
from sedna.common import Result
from sedna.common import Service
from sedna.console.master import FormatedResult
from sedna.console.master import main
from sedna.master import Master
from tests.console.test_sampler import get_package_abpath
from tests.console.test_sampler import MockedSednaConfigParser

TEST_IP = "127.0.0.1"
TEST_SERVICE_NAME = "$$test_name$$"
TEST_METHOD = "$$test_method$$"
TEST_GROUP = "$$test_group$$"
TEST_STATUS = "$$test_status$$"
TEST_ANALYSIS = "$$test_analysis$$"


class FormatedResultTest(TestCase):
    """
    The test cases to test the output of Sedna result
    """
    def setUp(self):
        """
        Set up fake results  from 3 node.
        """
        service = Service(name="$$test_service_a$$", ip=TEST_IP)
        service_result_a =\
            Result(service=service,
                   status=TEST_STATUS,
                   analysis=TEST_ANALYSIS)
        service_result_b = \
            Result(service=service,
                   status="active",
                   analysis=TEST_ANALYSIS)
        service_result_c = \
            Result(service=service,
                   status="inactive",
                   analysis=TEST_ANALYSIS)
        result_a = [service_result_a, service_result_b]
        result_b = [service_result_c]
        node_result_a =\
            NodeResult("$$test_group_a$$", "$$test_ip_a$$", result_a)
        node_result_b =\
            NodeResult("$$test_group_b$$", "$$test_ip_b$$", result_b)
        self.node_results = [node_result_a, node_result_b]
        self.formated_result = FormatedResult()

    def test_format_output_log(self):
        """
        The test case to test the log to display results from all nodes.
        The result of the test case should be check in
        sedna/tests/log/sedna.log
        :return:
        """
        self.formated_result.format_output_log(node_results=self.node_results)


class MasterMainTest(TestCase):
    """
    The test case to test main function in sampler.
    """
    def setUp(self):
        self.sys_argv = sys.argv
        sys.argv = []
        os.environ['SEDNA_CONF'] = "fake_path_sedna.conf"
        os.environ['SEDNA_LOG_CONF'] = get_package_abpath("./logging.conf")

    def test_command_line_arguments_default(self):
        sys.argv.append("sedna.console.master")
        main(config_paser_class=MockedSednaConfigParser,
             master_class=MockedMaster,
             format_output_class=MockedFormatedResult)

        self.assertEquals(MockedSednaConfigParser.config_path_stub,
                          "fake_path_sedna.conf")

    def test_command_line_arguments_config_path_defined(self):
        sys.argv.append("sedna.console.master")
        sys.argv.append("--config_path")
        sys.argv.append("defined_fake_path_sedna.conf")
        main(config_paser_class=MockedSednaConfigParser,
             master_class=MockedMaster,
             format_output_class=MockedFormatedResult)

        self.assertEquals(MockedSednaConfigParser.config_path_stub,
                          "defined_fake_path_sedna.conf")

    def tearDown(self):
        sys.argv = self.sys_argv


class MockedMaster(Master):
    """
    This class to mock class Master in main function of master console.
    """
    def __init__(self):
        pass

    def verify_nodes(self, sedna_config_value):
        pass


class MockedFormatedResult(FormatedResult):
    """
    This class to mock class FormateResult in main function of master console.
    """
    def format_output_log(self, node_results):
        pass

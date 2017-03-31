from unittest2 import TestCase
import os
import sys

from sedna.config import SednaConfigParser
from sedna.console.sampler import main
from sedna.server import NodeServer


def get_package_abpath(relative_path):
    """
    This function is to get absolute file path
    in the repository and user-defined to get
    the absolute path of user-defined path.
    :param relative_path:  the path should relatively
    start from sedna repository.
    :return:
    """
    list_package_path = []
    package_path = ""
    for item in os.getcwd().split(os.sep):
        list_package_path.append(item)
        if item == "sedna":
            package_path = os.sep.join(list_package_path)
            break
    return package_path + os.sep + relative_path.strip('./')


class SamplerConsoleTest(TestCase):
    """
    The test cases to test main function in sampler.
    """
    def setUp(self):
        self.sys_argv = sys.argv
        sys.argv = []
        os.environ['SEDNA_CONF'] = "fake_path_sedna.conf"
        os.environ['SEDNA_LOG_CONF'] = get_package_abpath("./logging.conf")

    def test_command_line_arguments_default(self):
        sys.argv.append("sedna.console.sampler")
        main(config_paser_class=MockedSednaConfigParser,
             node_server=MockedNodeServer)

        self.assertEquals(MockedSednaConfigParser.config_path_stub,
                          "fake_path_sedna.conf")

    def test_command_line_arguments_config_path_defined(self):

        sys.argv.append("sedna.console.sampler")
        sys.argv.append("--config_path")
        sys.argv.append("defined_fake_path_sedna.conf")
        main(config_paser_class=MockedSednaConfigParser,
             node_server=MockedNodeServer)

        self.assertEquals(MockedSednaConfigParser.config_path_stub,
                          "defined_fake_path_sedna.conf")

    def tearDown(self):
        sys.argv = self.sys_argv


class MockedSednaConfigParser(SednaConfigParser):
    """
    This class to mock class SednaConfigParser in main of sampler console.
    """
    config_path_stub = None

    def __init__(self, config_dir):
        MockedSednaConfigParser.config_path_stub = config_dir
        self.nodes = "mock_node"
        self.port = 1

    def get_sedna_config(self):
        pass


class MockedNodeServer(NodeServer):
    """
    This class to mock class NodeSamplerServer in main of sampler console.
    """
    def __init__(self, port, sampler):
        pass

    def start(self):
        pass

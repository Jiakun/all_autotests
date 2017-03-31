import unittest2
from ConfigParser import ConfigParser

from sedna.config import SednaConfigParser
from sedna.common import Node
from sedna.common import Service
from tests.console.test_sampler import get_package_abpath


class GetConfigTest(unittest2.TestCase):
    """
    The test cases to test Config class
    when config file is configured correctly.
    """
    def setUp(self):
        fake_config_dir =\
            get_package_abpath("./tests/test_config/positive_config_test.conf")
        self.fake_sedna_config = SednaConfigParser(fake_config_dir)

        self.config = ConfigParser()
        self.config.read(fake_config_dir)

        self.sedna_config_object = self.fake_sedna_config.get_sedna_config()

    def test_get_port(self):
        self.assertEquals(self.sedna_config_object.port,
                          self.config.get("sampler", "port"),
                          'Fail when get port.')

    def test_get_nodes(self):
        nodes_num = 0
        for option in self.config.options("groups"):
            group_addresses =\
                self.config.get("groups", option).split(", ")
            nodes_num += len(group_addresses)

        node_list = self.sedna_config_object.nodes

        self.assertEquals(len(node_list), nodes_num,
                          'Fail when test_get_nodes information')

    def test_get_nodes_content_stdout(self):
        node_list = self.sedna_config_object.nodes
        print node_list[3].group
        print node_list[3].ip
        for service in node_list[3].services:
            print service.name
            print service.ip
            print service.methods

    def test_get_nodes_content(self):
        expected_service_a_1 =\
            Service(name="service_a", ip="192.168.0.1",
                    methods="systemd")
        expected_service_a_2 = \
            Service(name="service_a", ip="192.168.0.2",
                    methods="systemd")
        expected_service_a_3 = \
            Service(name="service_a", ip="192.168.0.3",
                    methods="systemd")
        expected_service_b_1 =\
            Service(name="service_b", ip="192.168.0.1",
                    methods="pacemaker")
        expected_service_b_2 = \
            Service(name="service_b", ip="192.168.0.2",
                    methods="pacemaker")
        expected_service_b_3 = \
            Service(name="service_b", ip="192.168.0.3",
                    methods="pacemaker")
        expected_service_c_4 = \
            Service(name="service_c", ip="192.168.0.4",
                    methods="init.d")
        expected_service_c_5 = \
            Service(name="service_c", ip="192.168.0.5",
                    methods="init.d")
        expected_service_d_4 = \
            Service(name="service_d", ip="192.168.0.4",
                    methods="$$unknown_method$$")
        expected_service_d_5 = \
            Service(name="service_d", ip="192.168.0.5",
                    methods="$$unknown_method$$")

        expected_service_list_1 = [expected_service_a_1, expected_service_b_1]
        expected_service_list_2 = [expected_service_a_2, expected_service_b_2]
        expected_service_list_3 = [expected_service_a_3, expected_service_b_3]
        expected_service_list_4 = [expected_service_c_4, expected_service_d_4]
        expected_service_list_5 = [expected_service_c_5, expected_service_d_5]

        expected_node_1 =\
            Node(group="test_group_a", ip="192.168.0.1",
                 services=expected_service_list_1)
        expected_node_2 =\
            Node(group="test_group_a", ip="192.168.0.2",
                 services=expected_service_list_2)
        expected_node_3 =\
            Node(group="test_group_a", ip="192.168.0.3",
                 services=expected_service_list_3)
        expected_node_4 =\
            Node(group="test_group_b", ip="192.168.0.4",
                 services=expected_service_list_4)
        expected_node_5 =\
            Node(group="test_group_b", ip="192.168.0.5",
                 services=expected_service_list_5)

        expected_nodes =\
            [expected_node_1, expected_node_2, expected_node_3,
             expected_node_4, expected_node_5]

        node_list = self.sedna_config_object.nodes

        self.assertEquals(node_list, expected_nodes,
                          'Fail when test_get_nodes information')

    def test_get_scenario_available(self):
        available_scenario = self.fake_sedna_config.get_scenario_available()
        expected_scenario = "testscenario"
        self.assertEqual(available_scenario[0], expected_scenario)

    def test_get_auth_info(self):
        auth_info = self.fake_sedna_config.get_auth_info()
        self.assertEqual(len(auth_info), 7)


class GetConfigNegtiveTest(unittest2.TestCase):
    """
    The test cases to test Negtive case
    when config file is configured correctly.
    Negtive cases:(a,,b),(a,b),("   8000")
    """

    def setUp(self):
        self.fake_sedna_config = ConfigParser()
        self.fake_sedna_config.read(
            get_package_abpath(
                "./tests/test_config/config_test_with_negligible_faults.conf"))

    def test_get_elements_with_negligible_fault_format(self):
        config = SednaConfigParser(config_dir=get_package_abpath(
            "./tests/test_config/config_test_with_negligible_faults.conf"))
        sedna_config_object = config.get_sedna_config()
        self.assertEquals(sedna_config_object.port,
                          "10000",
                          'Fail when get port.')
        nodes_num = 0
        for option in self.fake_sedna_config.options("groups"):
            group_addresses = []
            for ip in self.fake_sedna_config.get("groups", option).split(","):
                each_ip = ip.strip()
                if each_ip == "":
                    raise Exception("The %s's result of 'groups' "
                                    "has extra spaces " % option)
                group_addresses.append(each_ip)
            nodes_num += len(group_addresses)
        node_list = sedna_config_object.nodes
        self.assertEquals(len(node_list), nodes_num,
                          'Fail when test_get_nodes information')

    def test_non_existent_file(self):
        with self.assertRaises(Exception):
            SednaConfigParser(
                config_dir=get_package_abpath("./non_existent_file"))

    def test_no_group_section(self):
        with self.assertRaises(Exception):
            SednaConfigParser(config_dir=get_package_abpath(
                "./tests/test_config/config_test_no_group_section.conf"))

    def test_no_service_section(self):
        with self.assertRaises(Exception):
            SednaConfigParser(config_dir=get_package_abpath(
                "./tests/test_config/config_test_no_service_section.conf"))

    def test_no_method_section(self):
        with self.assertRaises(Exception):
            SednaConfigParser(config_dir=get_package_abpath(
                "./tests/test_config/config_test_no_method_section.conf"))

    def test_no_group_option(self):
        with self.assertRaises(Exception):
            SednaConfigParser(config_dir=get_package_abpath(
                "./tests/test_config/config_test_no_group_option.conf"))

    def test_no_service_option(self):
        with self.assertRaises(Exception):
            SednaConfigParser(config_dir=get_package_abpath(
                "./tests/test_config/config_test_no_service_option.conf"))

    def test_no_method_option(self):
        with self.assertRaises(Exception):
            SednaConfigParser(config_dir=get_package_abpath(
                "./tests/test_config/config_test_no_method_option.conf"))

    def test_no_sampler_section(self):
        with self.assertRaises(Exception):
            SednaConfigParser(config_dir=get_package_abpath(
                "./tests/test_config/config_test_no_sampler_section.conf"))

    def test_no_sampler_option(self):
        with self.assertRaises(Exception):
            SednaConfigParser(config_dir=get_package_abpath(
                "./tests/test_config/config_test_no_sampler_option.conf"))

    def test_illegal_sampler_value(self):
        with self.assertRaises(Exception):
            SednaConfigParser(config_dir=get_package_abpath(
                "./tests/test_config/"
                "config_test_port_illegal_value.conf"))

    def test_group_configuration_with_wrong_delimiter(self):
        with self.assertRaises(Exception):
            SednaConfigParser(config_dir=get_package_abpath(
                "./tests/test_config/"
                "group_config_test_with_wrong_delimiter.conf"))

    def test_services_configuration_with_wrong_delimiter(self):
        with self.assertRaises(Exception):
            SednaConfigParser(config_dir=get_package_abpath(
                "./tests/test_config/"
                "service_config_test_with_wrong_delimiter.conf"))

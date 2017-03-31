# Filename: Config.py
"""
Read config file
to get groups information in openstack cluster.
"""
import ConfigParser
import os
import logging

from sedna.common import Service
from sedna.common import Node

LOG = logging.getLogger("")

SEDNA_CONF = os.environ.get("SEDNA_CONF", "/etc/sedna/sedna.conf")
SEDNA_LOG_CONF = os.environ.get("SEDNA_LOG_CONF", "/etc/sedna/logging.conf")


class SednaConfigParser(object):
    """
    The class is to get information from config file
    """

    def __init__(self, config_dir):
        """
        Class initialization
        :param config_dir:the directory of config file
        """
        self._config_dir = config_dir
        self.nodes = self._get_nodes()
        self.port = self._get_port()
        self.ha = self._get_ha()

    def get_sedna_config(self):
        """
        To get a object
        :return:the object include a list of nodes and the value of port
        """
        sedna_config_object = SednaConfig()
        sedna_config_object.nodes = self.nodes
        sedna_config_object.port = self.port
        sedna_config_object.ha = self.ha
        return sedna_config_object

    def _get_port(self):
        """
        To get the port from config file
        :return:the number of port
        """
        config = ConfigParser.ConfigParser()
        config.read(self._config_dir)
        if not config.has_section("sampler"):
            LOG.error("NoSectionError, "
                      "there is no section named 'sampler'")
            raise Exception("NoSectionError, "
                            "there is no section named 'sampler'")
        if not config.items("sampler"):
            LOG.error("NoOptionError, "
                      "there is no option in named "
                      "'sampler' of section")
            raise Exception("NoOptionError, "
                            "there is no option in named "
                            "'sampler' of section")

        if not config.has_option("sampler", "port"):
            LOG.error("NoOptionError, "
                      "there is no option named 'port' "
                      "in named 'sampler' of section")
            raise Exception("NoOptionError, "
                            "there is no option named 'port' "
                            "in named 'sampler' of section")
        if not int(config.get("sampler", "port")):
            LOG.error("ErrorOptionValue, "
                      "there is illegal value "
                      "in named 'sampler' of section")
            raise Exception("ErrorOptionValue, "
                            "there is illegal value "
                            "in named 'sampler' of section")
        port = config.get("sampler", "port")
        return port

    def _get_nodes(self):
        """
        This method is to read the contents of the configuration file
        :return: a list contains many Node Instance(ip, group,a sub list)
        and the sub list contains (services_name, check-method, ip)
        """
        config = ConfigParser.ConfigParser()
        if not os.path.isfile(self._config_dir) \
                or not os.path.exists(self._config_dir):
            LOG.error("%s is not a file or it doesn't exist." %
                      self._config_dir)
            raise Exception("%s is not a file or it doesn't exist." %
                            self._config_dir)
        config.read(self._config_dir)
        nodes = []
        list_number = 0
        if not config.has_section("groups"):
            LOG.error("NoSectionError, "
                      "there is no section named 'groups'")
            raise Exception("NoSectionError, "
                            "there is no section named 'groups'")
        if not config.items("groups"):
            LOG.error("NoOptionError, "
                      "there is no option in named "
                      "'groups' of section")
            raise Exception("NoOptionError, "
                            "there is no option in named "
                            "'groups' of section")
        for option in config.options("groups"):
            ips = []
            services_names = []
            for ip in config.get("groups", option).split(","):
                count = 0
                each_ip = ip.strip()
                if each_ip == "":
                    LOG.error("The %s's result of 'groups' "
                              "has extra spaces " % option)
                    raise Exception("The %s's result of 'groups' "
                                    "has extra spaces " % option)
                for each_char in each_ip:
                    if each_char == ".":
                        count += 1
                if count != 3:
                    LOG.error("ErrorIP, "
                              "there is bad formatted ip in named "
                              "'groups' of section")
                    raise Exception("ErrorIP, "
                                    "there is bad formatted ip in named"
                                    "'groups' of section")
                ips.append(each_ip)
            if not config.has_section("services"):
                LOG.error("NoSectionError, "
                          "there is no section named 'services'")
                raise Exception("NoSectionError, "
                                "there is no section named 'services'")
            if not config.has_option("services", option):
                LOG.error("NoOptionError, "
                          "there is no option named %s in named "
                          "'services' of section" % option)
                raise Exception("NoOptionError, "
                                "there is no option named %s in named "
                                "'services' of section" % option)
            for service_name in config.get("services", option).split(","):
                each_service = service_name.strip()
                if each_service == "":
                    LOG.error("The %s's result of 'services' "
                              "has extra spaces " % option)
                    raise Exception("The %s's result of 'services' "
                                    "has extra spaces " % option)
                services_names.append(each_service)
            for ip in ips:
                services = []
                for service_name in services_names:
                    if not config.has_section("method"):
                        LOG.error("NoSectionError, "
                                  "there is no section named 'method'")
                        raise Exception("NoSectionError, "
                                        "there is no section named 'method'")
                    if not config.has_option("method", service_name):
                        LOG.error("NoOptionError, "
                                  "there is no option named %s in named "
                                  "'method' of section" % service_name)
                        raise Exception("NoOptionError, "
                                        "there is no option named %s in named "
                                        "'method' of section" % service_name)
                    method = config.get("method", service_name)
                    service = Service(name=service_name,
                                      methods=method, ip=ip)
                    services.append(service)
                node = Node(group=option, ip=ip)
                node.services = services
                nodes.append(node)
                list_number += 1
        return nodes

    def _get_ha(self):
        config = ConfigParser.ConfigParser()
        if not os.path.isfile(self._config_dir) \
                or not os.path.exists(self._config_dir):
            LOG.error("%s is not a file or it doesn't exist." %
                      self._config_dir)
            raise Exception("%s is not a file or it doesn't exist." %
                            self._config_dir)
        config.read(self._config_dir)
        if not config.has_section("ha"):
            LOG.error("NoSectionError, "
                      "there is no section named 'ha'")
            raise Exception("NoSectionError, "
                            "there is no section named 'ha'")
        if not config.items("ha"):
            LOG.error("NoOptionError, "
                      "there is no option in named "
                      "'ha' of section")
            raise Exception("NoOptionError, "
                            "there is no option in named "
                            "'ha' of section")
        services = dict()
        for option in config.options("ha"):
            scenario = config.get("ha", option).strip()
            if scenario == "":
                    LOG.error("The %s's result of 'ha' "
                              "has extra spaces " % option)
                    raise Exception("The %s's result of 'ha' "
                                    "has extra spaces " % option)
            services[option] = scenario
        return services

    def get_scenario_available(self):
        """
        To get the port from config file
        :return:the number of port
        """
        config = ConfigParser.ConfigParser()
        config.read(self._config_dir)
        if not config.has_section("steps_of_scenario"):
            LOG.error("NoSectionError, "
                      "there is no section named 'steps_of_scenario'")
            raise Exception("NoSectionError, "
                            "there is no section named 'steps_of_scenario'")
        # TODO(sy):need to check whether these scenarios class exist or not

        return config.options("steps_of_scenario")

    def get_auth_info(self):
        config = ConfigParser.ConfigParser()
        config.read(self._config_dir)
        if not config.has_section("auth_info"):
            LOG.error("NoSectionError, "
                      "there is no section named 'auth_info'")
            raise Exception("NoSectionError, "
                            "there is no section named 'auth_info'")

        auth_info_list = config.options("auth_info")
        auth_info = dict()
        for info in auth_info_list:
            value = config.get("auth_info", info).strip()
            auth_info[info] = value

        return auth_info

    def get_external_network_id(self):
        config = ConfigParser.ConfigParser()
        config.read(self._config_dir)
        if not config.has_section("network"):
            LOG.error("NoSectionError, "
                      "there is no section named 'network'")
            raise Exception("NoSectionError, "
                            "there is no section named 'network'")

        external_network_id = config.get("network", "external_network_id").strip()
        return str(external_network_id)


class SednaConfig(object):
    """
    The class is to get a object about the list of nodes and the value of port
    """

    def __init__(self, nodes=None, port=None):
        """
        Class initialization
        :param nodes:a list contains many Node Instance(ip, group,a sub list)
        and the sub list contains (services_name, check-method, ip)
        :param port:the value of port
        """
        self.nodes = nodes
        self.port = port


class KillerConfig(object):
    def __init__(self, ip=None, port=None, services=None):
        self.ip = ip
        self.port = port
        self.services = services


class ServiceCommandConfig(object):
    def __init__(self, ip=None, port=None, service=None, operation=None):
        self.ip = ip
        self.port = port
        self.service = service
        self.operation = operation


class HAConfig(object):
    def __init__(self, ip=None, port=None, scenario=None, service=None,
                 operation=None):
        self.ip = ip
        self.port = port
        self.scenario = scenario
        self.operation = operation
        self.service = service

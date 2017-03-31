""" the main classes for master node """
from xmlrpclib import ServerProxy
import logging.config

from sedna.server import NodeServiceProvider

from thread import CheckerThread


LOG = logging.getLogger("")


class XmlRPCClient(object):
    """
    The class to provide Sedna Remote Procedure Call.
    """
    def connect(self, ip, group, port, node_services):
        url = "http://" + ip + ":" + port
        LOG.debug(
            "Sent from Master-node_services: %s -url: %s -group: %s " %
            (node_services, url, group))

        proxy = ServerProxy(url)
        raw_node_result = proxy.sample(node_services)
        LOG.info(
            "Raw Info received from Server:  %s" % raw_node_result)
        return raw_node_result

    def connect_kill_service(self, sedna_kill_service_config_value):
        url = "http://" + sedna_kill_service_config_value.ip + ":" +\
              sedna_kill_service_config_value.port
        LOG.debug(
            "Sent from Master-node_services: %s -url: %s "
            % (sedna_kill_service_config_value.services, url))

        proxy = ServerProxy(url)
        node_result = proxy.kill(sedna_kill_service_config_value.services)
        LOG.info(
            "Kill command Info received from Server:  %s" % node_result)
        return node_result

    def connect_service_command(self, s_command_config):
        url = "http://" + s_command_config.ip + ":" +\
              s_command_config.port
        LOG.debug(
            "Sent from Master-node_services: %s -url: %s "
            % (s_command_config.service["name"], url))

        proxy = ServerProxy(url)
        node_result = proxy.run_service_command(s_command_config.service,
                                                s_command_config.operation)
        LOG.info(
            "Service command Info received from Server:  %s" % node_result)
        return node_result

    def connect_ha_scenario(self, ha_config):
        url = "http://" + ha_config.ip + ":" + ha_config.port
        LOG.debug(
            "Sent from Master-node_services: %s -url: %s "
            % (ha_config.scenario, url))

        proxy = ServerProxy(url)
        node_result = proxy.run_ha_scenario(ha_config.scenario)
        LOG.info(
            "HA scenario Info received from Server:  %s" % node_result)
        return node_result

    def connect_get_ha_daemon_thread_status(self, ha_config):
        url = "http://" + ha_config.ip + ":" + ha_config.port
        LOG.debug(
            "Sent from Master-node_services: %s -url: %s "
            % (ha_config.scenario, url))

        proxy = ServerProxy(url)
        node_result = proxy.get_ha_daemon_thread_status()
        LOG.info(
            "HA scenario daemon thread status Info received from Server:  %s"
            % node_result)
        return node_result

    def connect_get_ha_scenario_status(self, ha_config):
        url = "http://" + ha_config.ip + ":" + ha_config.port
        LOG.debug(
            "Sent from Master-node_services: %s -url: %s "
            % (ha_config.scenario, url))

        proxy = ServerProxy(url)
        node_result = proxy.get_ha_scenario_status()
        LOG.info(
            "HA scenario status Info received from Server:  %s"
            % node_result)
        return node_result


class Master(object):
    """
    The master dispatches service sample tasks across the nodes, and check the
    healthy of the cluster
    """
    def __init__(self, rpc_client=None):

        if rpc_client is None:
            rpc_client = XmlRPCClient()

        self._rpc_client = rpc_client

    def verify_nodes(self, sedna_config_value):
        """
        Verify the status of the given nodes
        :param sedna_config_value:the SednaConfig Object
        containing the info of port and nodes
        :return: the verification result of nodes
        """
        node_results = []
        threads = []

        for node in sedna_config_value.nodes:
            t = CheckerThread(node=node, rpc_client=self._rpc_client,
                              sedna_config_value=sedna_config_value)
            threads.append(t)

        for t in threads:
            # t.setDaemon(True)
            t.start()
            t.join()

        for t in threads:
            node_results.append(t.get_result())
        LOG.debug("Master return:%s" % node_results)
        return node_results

    def kill_service(self, sedna_kill_service_config_value):
        """
        Kill services on a given node
        :param sedna_kill_service_config_value:
        :return:
        """
        try:
            raw_node_result = self._rpc_client.connect_kill_service(
                sedna_kill_service_config_value)
        except Exception, e:
                LOG.error(e)
                raise Exception("%s\nWarning: kill cannot be finished.",
                                sedna_kill_service_config_value.ip)

        node_services_result = []

        for service_result in raw_node_result:
            node_services_result.append(service_result)

        LOG.debug("Master return:%s" % node_services_result)
        return node_services_result

    def run_service_command(self, service_command_config):
        """
        Kill services on a given node
        :param service_command_config:
        :return:
        """
        try:
            node_result = self._rpc_client.connect_service_command(
                service_command_config)
        except Exception, e:
            LOG.error(e)
            raise Exception("%s command cannot be finished.",
                            service_command_config.operation)

        LOG.debug("Master return:%s" % node_result)
        return node_result

    def run_ha_scenario(self, ha_config):
        try:
            node_result = self._rpc_client.connect_ha_scenario(
                ha_config=ha_config)
        except Exception, e:
            LOG.error(e)
            raise Exception("%s scenario cannot run.",
                            ha_config.scenario)
        return node_result

    def get_ha_daemon_thread_status(self, ha_config):
        try:
            node_result = self._rpc_client.connect_get_ha_daemon_thread_status(
                ha_config=ha_config)
        except Exception, e:
            LOG.error(e)
            raise Exception("%s scenario thread cannot be connected.",
                            ha_config.scenario)
        return node_result

    def get_ha_scenario_status(self, ha_config):
        try:
            node_result = self._rpc_client.connect_get_ha_scenario_status(
                ha_config=ha_config)
        except Exception, e:
            LOG.error(e)
            raise Exception("%s scenario thread cannot be connected.",
                            ha_config.scenario)
        return node_result

    def clean_up_resource(self, sedna_config_value):
        # TODO:
        pass

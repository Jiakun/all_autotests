from threading import Thread

from sedna.common import Service
from sedna.common import Result
from sedna.common import NodeResult

import logging.config

LOG = logging.getLogger("")


def verify_nodes_thread(node, sedna_config_value, _rpc_client):
    try:
        raw_node_result = _rpc_client.connect(
            ip=node.ip, group=node.group, port=sedna_config_value.port,
            node_services=node.services)

    except Exception, e:
        LOG.error(e)
        # raise Exception("%s\nWarning:Node %s cannot be finished."
        #  %(e, node.ip))
        service = Service(name="***", ip=node.ip, methods="***")
        result = [Result(service=service, status="unknown",
                         analysis=str(e))]
        return NodeResult(group=node.group, ip=node.ip, result=result)

    node_services_result = []

    for service_result in raw_node_result:
        service = Service(**service_result["service"])
        result = \
            Result(service=service, status=service_result["status"],
                   analysis=service_result["analysis"])
        node_services_result.append(result)
    node_result = \
        NodeResult(group=node.group, ip=node.ip,
                   result=node_services_result)
    return node_result


class CheckerThread(Thread):
    """
    This class sets the functions for threading for checkers
    """
    def __init__(self, node, sedna_config_value, rpc_client):
        Thread.__init__(self)
        self.node = node
        self.sedna_config_value = sedna_config_value
        self.node_result = None
        self._rpc_client = rpc_client

    def run(self):
        self.node_result = verify_nodes_thread(
            node=self.node, _rpc_client=self._rpc_client,
            sedna_config_value=self.sedna_config_value)

    def get_result(self):
        return self.node_result


class HAScenarioThread(Thread):
    """
    This class allows controls for running ha scenario thread from outside
    """
    def __init__(self, scenario=None, ha_tester=None, times=None):
        """
        :param scenario: scenario for HA
        :param server: node server
        :param times: times for scenario restart
        """
        Thread.__init__(self)
        self.node_result = None
        self.scenario = scenario
        self.ha_tester = ha_tester
        self.times = times

    def run(self):
        """
        This function runs ha scenario
        :return:
        """
        self.ha_tester.set_ha_scenario_start()
        self.node_result = self.ha_tester.run_ha_scenario(
            scenario_class=self.scenario, times=self.times)

    def stop(self):
        """
        This function stops the running ha scenario
        :return:
        """
        self.ha_tester.set_ha_scenario_stop()
        self.ha_tester.set_unexecuted_status()

    def get_result(self):
        """
        :return: result from ha scenario (True: succeed; False: failed)
        """
        result = self.node_result
        self.node_result = None
        return result

    def get_executed_status(self):
        return self.ha_tester.get_executed_status()


class HADaemonThread:
    """
    This class registers ha thread on a node
    """
    def __init__(self):
        self.ha_thread = None
        self.scenario = None

    def register_thread(self, ha_thread=None, scenario=None):
        self.ha_thread = ha_thread
        self.scenario = scenario

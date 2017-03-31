from time import sleep
import re
from SimpleXMLRPCServer import SimpleXMLRPCServer

from sedna.common import Service
from sedna.sampler import NodeSampler
from sedna.ha.services import ServiceKiller, ServiceCommand, NodeHATest
from sedna.thread import HADaemonThread, HAScenarioThread
from sedna.ha.ha import HAResult, HAStep, HAStage
from sedna.scenario.scenario import Status
from sedna.observer import Observable, LoggerObserver, ObserverInfoType

import logging.config

LOG = logging.getLogger("")

# allow register for ha daemon thread
ha_daemon_thread = HADaemonThread()


class NodeServiceProvider(object):
    """
    The class to provide services on the node server
    """
    def __init__(self):
        self.killer = None
        self.service_commander = None
        self.sampler = None
        self.ha_tester = None

    def sample(self, services=None, name=None, klass=None):
        self.sampler = NodeSampler()
        self.sampler.register_service(name=name, klass=klass)
        return self.sampler.sample(services=services)

    def kill(self, services):
        self.killer = ServiceKiller()
        return self.killer.kill_services(services)

    def run_service_command(self, service, operation):
        self.service_commander = ServiceCommand()
        if service.methods == "systemd":
            return self.service_commander.execute(
                service.name, "systemctl " + operation + " ")

    def run_ha_scenario(self, scenario_class=None, times=None):
        self.ha_tester = NodeHATest()
        return self.ha_tester.run_ha_scenario(
            scenario_class=scenario_class, times=times)


class NodeServer(object):
    """
    The server wrapper of node services
    """
    def __init__(self, port, sampler=None, killer=None, s_commander=None,
                 ha_tester=None, observable=None):
        """
        Server initializer.

        :param port: the port the server listen to
        :param sampler: the sampler instance
        :param killer:
        :param s_commander:
        """
        self._port = int(port)

        self._server = SimpleXMLRPCServer(("0.0.0.0", self._port))
        self._server.register_multicall_functions()
        self._server.register_instance(self)

        if sampler is None:
            self._sampler = NodeSampler()
        else:
            self._sampler = sampler

        if killer is None:
            self._killer = ServiceKiller()
        else:
            self._killer = killer

        if s_commander is None:
            self._service_commander = ServiceCommand()
        else:
            self._service_commander = s_commander

        if ha_tester is None:
            self._ha_tester = NodeHATest()
        else:
            self._ha_tester = ha_tester

        if observable is not None:
            self.observable = observable
        else:
            # Default observer
            self.observable = Observable()
            self.observable.register_observer(
                LoggerObserver(logger=LOG, info_type=ObserverInfoType.HA))

        self.ha_daemon_thread = HADaemonThread()

    def start(self):
        """
        Start the server.
        """
        LOG.info("Listening in port %s." % self._port)

        self._server.serve_forever()

    def sample(self, services):
        """
        The wrapper of sample method to convert service
        dictionaries to service object.
        :param services: the list of Service dicts
        which is transformed from Service Obj to dict form .
        :return: services sample result
        """
        list_services = []

        LOG.info("Receive raw info from Master:  %s" % services)
        for service in services:
            list_services.append(Service(**service))

        LOG.info("Receive format info from Master:  %s" %
                 list_services)

        return self._sampler.sample(list_services)

    def kill(self, services):
        """
        The wrapper of sample method to convert service
        dictionaries to service object.
        Then run to kill a service
        :param services:
        :return:
        """
        list_services = []

        LOG.info("Receive raw info from Master:  %s" % services)
        for service in services:
            list_services.append(Service(**service))

        LOG.info("Receive format info from Master:  %s" %
                 list_services)
        return self._killer.kill_services(list_services)

    def run_service_command(self, service, operation):
        """
        :param service:
        :param operation:
        :return:
        """
        if service["methods"] == "systemd":
            raw_result = self._service_commander.execute(
                service["name"], "systemctl " + operation + " ")
            result = {'status': raw_result[0],
                      'service': service
                      }
            return result

    def run_ha_scenario(self, scenario, times=None):
        """

        :param scenario: scenario class
        :param times: scenario running times
        :param observer
        :return:
        """

        def create_ha_thread():
            self.observable.notify_observer(
                HAResult(name=scenario,
                         step="start",
                         stage=HAStage.EXECUTING,
                         status=Status.SUCCEEDED))
            create_thread = None
            try:
                create_thread = HAScenarioThread(
                    ha_tester=self._ha_tester, scenario=scenario,
                    times=times)
                create_thread.setDaemon(True)
                create_thread.start()

                # wait for the first scenario
                while create_thread.get_executed_status() is False:
                    if create_thread.get_result() == -1:
                        self.observable.notify_observer(
                            HAResult(name=scenario,
                                     step="start",
                                     stage=HAStage.EXECUTED,
                                     status=Status.FAILED))
                        return -1
                    elif create_thread.get_result() == 0:
                        break

                    sleep(1)
            except:
                self.observable.notify_observer(
                    HAResult(name=scenario,
                             step="start",
                             stage=HAStage.EXECUTED,
                             status=Status.FAILED))
                return -1

            self.observable.notify_observer(
                HAResult(name=scenario,
                         step="start",
                         stage=HAStage.EXECUTED,
                         status=Status.SUCCEEDED))
            self.ha_daemon_thread.register_thread(
                ha_thread=create_thread, scenario=scenario)
            return 0

        # check whether the thread failed
        if scenario == self.ha_daemon_thread.scenario:
            if not self.ha_daemon_thread.ha_thread.is_alive:
                return create_ha_thread()
        else:
            # determine whether to kill the previous daemon thread
            self.observable.notify_observer(
                HAResult(name=scenario,
                         step="stop",
                         stage=HAStage.EXECUTING,
                         status=Status.SUCCEEDED))

            if self.ha_daemon_thread.ha_thread is not None:
                # stop previous daemon thread
                try:
                    self.ha_daemon_thread.ha_thread.stop()
                    while self.ha_daemon_thread.ha_thread.get_result() is None:
                        # TODO: failed scenario is acceptable?
                        sleep(1)
                except:
                    self.observable.notify_observer(
                        HAResult(name=scenario,
                                 step="stop",
                                 stage=HAStage.EXECUTED,
                                 status=Status.FAILED))
                    return -1

                self.observable.notify_observer(
                    HAResult(name=scenario,
                             step="stop",
                             stage=HAStage.EXECUTED,
                             status=Status.SUCCEEDED))

        return create_ha_thread()

    def get_ha_scenario_status(self):
        if self.ha_daemon_thread.ha_thread.is_alive:
            self.observable.notify_observer(
                HAResult(name="scenario check",
                         step="check",
                         stage="alive",
                         status=Status.SUCCEEDED))
            return True
        else:
            self.observable.notify_observer(
                HAResult(name="scenario check",
                         step="check",
                         stage="stopped",
                         status=Status.SUCCEEDED))
            return False

    def get_ha_daemon_thread(self):
        return self.ha_daemon_thread.scenario

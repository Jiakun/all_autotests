from sedna.ha.ha import HAResult, HAStage, HAStep
from sedna.observer import Observable
from sedna.observer import LoggerObserver
from sedna.observer import WebSocketObserver
from sedna.observer import ObserverInfoType
from sedna.scenario.scenario import Status
from time import sleep, clock

from sedna.config import HAConfig
from sedna.config import SEDNA_CONF
from sedna.config import SednaConfigParser
from sedna.config import KillerConfig
from sedna.config import ServiceCommandConfig

from sedna.master import Master
from flask import jsonify
from flask import abort
from flask import make_response
from flask import url_for


def make_public_results(results):
    if len(results) == 0:
        abort(404)

    new_results = {}
    for field in results:
        if field == 'id':
            new_results['uri'] = url_for('get_results',
                                         results_id=results['id'],
                                         _external=True)
        else:
            new_results[field] = results[field]
    return new_results


class MasterHATest(object):
    def __init__(self, observable=None, operation=None, service=None, ip=None):
        if observable is None:
            # register observers
            ha_web_observer = WebSocketObserver(info_type=ObserverInfoType.HA)
            ha_log_observer = LoggerObserver(info_type=ObserverInfoType.HA)
            self.observable = Observable()
            self.observable.register_observer(ha_web_observer)
            self.observable.register_observer(ha_log_observer)
        else:
            self.observable = observable

        self.operation = operation
        self.service = service
        self.ip = ip

        self.sedna_config_value = None
        self.ha_config = None
        self.master = None

        self.MAX_TIME = 10

    def get_fomatted_result(self, status=None, name=None, analysis=None):
        results = []
        results.append({'status': status})
        results.append({'analysis': analysis})
        results.append({'name': name})
        results.append({'ip': self.ip})
        results.append({'operation': self.operation})
        return jsonify({'ha_results': map(make_public_results,
                                          results)})

    def get_failed_result(self, step=None):
        return self.get_fomatted_result(
            name=self.service['name'],
            status="failed",
            analysis="cannot run " + step)

    def restart_scenario(self):
        # record recovery time
        start_time = clock()
        while not self.get_ha_scenario_status(HAStep.STEP_4):
            if clock() - start_time > self.MAX_TIME:
                return self.get_failed_result(HAStep.STEP_4)
            self.master.run_ha_scenario(ha_config=self.ha_config)
            sleep(1)

        end_time = clock()
        return end_time-start_time

    def get_config(self):
        self.observable.notify_observer(
            HAResult(name=self.service['name'], step=HAStep.STEP_1,
                     stage=HAStage.EXECUTING, status=Status.SUCCEEDED))
        # get config
        try:
            config = SednaConfigParser(SEDNA_CONF)
            self.sedna_config_value = config.get_sedna_config()
            self.master = Master()
        except:
            self.observable.notify_observer(
                HAResult(name=self.service['name'], step=HAStep.STEP_1,
                         stage=HAStage.EXECUTED, status=Status.FAILED))
            return self.get_failed_result(HAStep.STEP_1)
        self.observable.notify_observer(
            HAResult(name=self.service['name'], step=HAStep.STEP_1,
                     stage=HAStage.EXECUTED, status=Status.SUCCEEDED))
        return Status.SUCCEEDED

    def run_scenario(self):
        # start scenario
        scenario = None
        self.observable.notify_observer(
            HAResult(name=self.service['name'], step=HAStep.STEP_2,
                     stage=HAStage.EXECUTING, status=Status.SUCCEEDED))
        try:
            scenario = self.sedna_config_value.ha[self.service["name"]]
            self.ha_config = HAConfig(
                ip=self.ip, port=self.sedna_config_value.port,
                scenario=scenario, service=self.service,
                operation=self.operation)
            try:
                self.master.run_ha_scenario(ha_config=self.ha_config)
            except:
                self.observable.notify_observer(
                    HAResult(name=self.service['name'], step=HAStep.STEP_2,
                             stage=HAStage.EXECUTING,
                             status=Status.FAILED + ": Cannot run scenario"))
                return self.get_failed_result(HAStep.STEP_2)
        except:
            self.observable.notify_observer(
                HAResult(name=self.service['name'], step=HAStep.STEP_2,
                         stage=HAStage.EXECUTING,
                         status=Status.FAILED + ": Unable to set config"))
            return self.get_failed_result(HAStep.STEP_2)
        return Status.SUCCEEDED

    def get_ha_daemon_thread_status(self, step):
        # check scenario status
        if self.master.get_ha_daemon_thread_status(ha_config=self.ha_config):
            self.observable.notify_observer(
                HAResult(name=self.service['name'], step=step + ": Thread status",
                         stage=HAStage.EXECUTED, status=Status.SUCCEEDED))
        else:
            self.observable.notify_observer(
                HAResult(name=self.service['name'], step=step,
                         stage=HAStage.EXECUTED,
                         status=Status.FAILED + ": Unable to run scenario"))
            return self.get_failed_result(step)
        return Status.SUCCEEDED

    def get_ha_scenario_status(self, step):
        # check ha scenario result
        if self.master.get_ha_scenario_status(ha_config=self.ha_config):
            self.observable.notify_observer(
                HAResult(name=self.service['name'], step=step + ": Scenario result",
                         stage=HAStage.EXECUTED, status=Status.SUCCEEDED))
        else:
            self.observable.notify_observer(
                HAResult(name=self.service['name'], step=step,
                         stage=HAStage.EXECUTED,
                         status=Status.FAILED + ": Unable to get scenario result"))
            return self.get_failed_result(step)
        return Status.SUCCEEDED

    def run_service_command(self):
        # service operation
        self.observable.notify_observer(
            HAResult(name=self.service['name'], step=HAStep.STEP_3,
                     stage=HAStage.EXECUTING, status=Status.SUCCEEDED))

        if self.operation == 'kill':
            try:
                services = [self.service]
                killer_config = KillerConfig(
                    port=self.sedna_config_value.port, ip=self.ip, services=services)
                kill_result = self.master.kill_service(killer_config)

                if kill_result[0]["status"] == "successful":
                    self.observable.notify_observer(
                        HAResult(name=self.service['name'], step=HAStep.STEP_3,
                                 stage=HAStage.EXECUTED,
                                 status=Status.SUCCEEDED))
                else:
                    self.observable.notify_observer(
                        HAResult(name=self.service['name'], step=HAStep.STEP_3,
                                 stage=HAStage.EXECUTED, status=Status.FAILED))
                    return self.get_failed_result(HAStep.STEP_3)
            except:
                self.observable.notify_observer(
                    HAResult(name=self.service['name'], step=HAStep.STEP_3,
                             stage=HAStage.EXECUTING, status=Status.FAILED))
                return self.get_failed_result(HAStep.STEP_3)

        elif self.operation == 'restart':
            try:
                self.service["methods"] = "systemd"
                config = ServiceCommandConfig(
                    ip=self.service["ip"],
                    port=self.sedna_config_value.port,
                    service=self.service, operation=self.operation)
                result = self.master.run_service_command(
                    service_command_config=config)
                if result["status"] == "successful":
                    self.observable.notify_observer(
                        HAResult(name=self.service['name'], step=HAStep.STEP_3,
                                 stage=HAStage.EXECUTED,
                                 status=Status.SUCCEEDED))
                else:
                    self.observable.notify_observer(
                        HAResult(name=self.service['name'], step=HAStep.STEP_3,
                                 stage=HAStage.EXECUTED, status=Status.FAILED))
                    return self.get_failed_result(HAStep.STEP_3)
            except:
                self.observable.notify_observer(
                    HAResult(name=self.service['name'], step=HAStep.STEP_3,
                             stage=HAStage.EXECUTING, status=Status.FAILED))
                return self.get_failed_result(HAStep.STEP_3)

        elif self.operation == 'start' or self.operation == 'stop':
            try:
                self.service["methods"] = "systemd"
                config = ServiceCommandConfig(
                    ip=self.service["ip"],
                    port=self.sedna_config_value.port,
                    service=self.service, operation=self.operation)
                result = self.master.run_service_command(
                    service_command_config=config)
                if result["status"] == "successful":
                    self.observable.notify_observer(
                        HAResult(name=self.service['name'],
                                 step=HAStep.STEP_3,
                                 stage=HAStage.EXECUTED,
                                 status=Status.SUCCEEDED))
                else:
                    self.observable.notify_observer(
                        HAResult(name=self.service['name'], step=HAStep.STEP_3,
                                 stage=HAStage.EXECUTED, status=Status.FAILED))
                    return self.get_failed_result(HAStep.STEP_3)
            except:
                self.observable.notify_observer(
                    HAResult(name=self.service['name'], step=HAStep.STEP_3,
                             stage=HAStage.EXECUTING, status=Status.FAILED))
                return self.get_failed_result(HAStep.STEP_3)

    def check_ha_scenario_status(self):
        self.observable.notify_observer(HAResult(
            name=self.service['name'], step=HAStep.STEP_4,
            stage=HAStage.EXECUTING, status=Status.SUCCEEDED))

        if self.operation in ["kill", "restart"]:
            restart_time = self.restart_scenario()
            status = ": after " + str(restart_time) + "s"
            self.observable.notify_observer(HAResult(
                name=self.service['name'], step=HAStep.STEP_4,
                stage=HAStage.EXECUTED, status=Status.SUCCEEDED + status))

        elif self.operation in ["start", "stop"]:
            try:
                if self.get_ha_scenario_status(HAStep.STEP_4) == Status.SUCCEEDED:
                    self.observable.notify_observer(
                        HAResult(name=self.service['name'], step=HAStep.STEP_4,
                                 stage=HAStage.EXECUTED,
                                 status=Status.SUCCEEDED))
                else:
                    self.observable.notify_observer(
                        HAResult(name=self.service['name'], step=HAStep.STEP_4,
                                 stage=HAStage.EXECUTED,
                                 status=Status.FAILED))
                    return self.get_failed_result(HAStep.STEP_4)
            except:
                self.observable.notify_observer(
                    HAResult(name=self.service['name'], step=HAStep.STEP_4,
                             stage=HAStage.EXECUTING, status=Status.FAILED))
                return self.get_failed_result(HAStep.STEP_4)
        return self.get_fomatted_result(name=self.service['name'],
                                        status="successful",
                                        analysis="none")

    def run(self):
        get_config_result = self.get_config()
        if get_config_result != Status.SUCCEEDED:
            return get_config_result

        run_scenario_result = self.run_scenario()
        if run_scenario_result != Status.SUCCEEDED:
            return run_scenario_result

        sleep(5)
        if self.get_ha_daemon_thread_status(HAStep.STEP_2) != Status.SUCCEEDED or \
                self.get_ha_scenario_status(HAStep.STEP_2) != Status.SUCCEEDED:
            return self.get_failed_result(HAStep.STEP_2)

        run_service_command_result = self.run_service_command()
        if run_service_command_result != Status.SUCCEEDED:
            return run_service_command_result

        sleep(5)
        if self.get_ha_daemon_thread_status(HAStep.STEP_4) != Status.SUCCEEDED or \
                self.get_ha_scenario_status(HAStep.STEP_4) != Status.SUCCEEDED:
            return self.get_failed_result(HAStep.STEP_4)

        return self.check_ha_scenario_status

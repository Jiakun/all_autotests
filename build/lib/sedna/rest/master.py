#!/usr/bin/python
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import url_for
from threading import Thread
from time import sleep, clock

import logging.config
import os
import requests

from sedna.config import SednaConfigParser, KillerConfig, \
    ServiceCommandConfig, HAConfig
from sedna.master import Master
from sedna.scenario.openstack.openstack import ServerCreateScenario, \
    ServerAttachVolumeScenario, ServerRebootScenario,  \
    PortCreateScenario, SnapshotCreateScenario, VolumeCreateScenario,\
    UserCreateScenario, DomainCreateScenario, ProjectCreateScenario, \
    SecurityGroupCreateScenario, AssociateFloatingipScenario,\
    KeypairCreateScenario, LoadBalancerCreateScenario,\
    LBaaSPoolCreateScenario, LBaaSMemberCreateScenario,\
    ListenerCreateScenario, LBaaSHealthMonitorCreateScenario
from sedna.scenario.scenario import Status, ScenarioList
from sedna.ha.ha import HAResult, HAStage, HAStep
from sedna.observer import Observable, LoggerObserver, WebSocketObserver, \
    ObserverInfoType

DEFUALT_SCENARIOS_LIST = [UserCreateScenario, DomainCreateScenario,
                          SecurityGroupCreateScenario, ProjectCreateScenario,
                          ServerCreateScenario, ServerAttachVolumeScenario,
                          ServerRebootScenario, PortCreateScenario,
                          SnapshotCreateScenario, VolumeCreateScenario,
                          AssociateFloatingipScenario,
                          KeypairCreateScenario, LoadBalancerCreateScenario,
                          ListenerCreateScenario, LBaaSPoolCreateScenario,
                          LBaaSHealthMonitorCreateScenario,
                          LBaaSMemberCreateScenario]

PORT = 10001

LOG = logging.getLogger("")

observable = Observable()


class MasterRestful(object):
    """
    The class to return master results.
    """
    def get_results(self):
        logging.config.fileConfig(os.environ["SEDNA_LOG_CONF"])
        config = SednaConfigParser(os.environ["SEDNA_CONF"])
        sedna_config_value = config.get_sedna_config()
        master = Master()
        return master.verify_nodes(sedna_config_value=sedna_config_value)

    def get_kill_service_results(self, ip=None, services=None):
        logging.config.fileConfig(os.environ["SEDNA_LOG_CONF"])
        config = SednaConfigParser(os.environ["SEDNA_CONF"])
        sedna_config_value = config.get_sedna_config()
        config = KillerConfig(port=sedna_config_value.port, ip=ip,
                              services=services)
        master = Master()
        return master.kill_service(sedna_kill_service_config_value=config)

    def get_service_command_results(self, service=None, operation=None):
        logging.config.fileConfig(os.environ["SEDNA_LOG_CONF"])
        config = SednaConfigParser(os.environ["SEDNA_CONF"])
        sedna_config_value = config.get_sedna_config()
        config = ServiceCommandConfig(ip=service["ip"],
                                      port=sedna_config_value.port,
                                      service=service, operation=operation)
        master = Master()
        return master.run_service_command(service_command_config=config)

    def get_ha_results(self, operation=None, service=None, ip=None):
        def get_fomatted_result(status=None, name=None, analysis=None):
            LOG.info(
                "HA[Results]: {service: %s, ip: %s, operation: %s, "
                "status: %s, analysis: %s}"
                % (service, ip, operation, status, analysis))

            results = []
            results.append({'status': status})
            results.append({'analysis': analysis})
            results.append({'name': name})
            results.append({'ip': ip})
            results.append({'operation': operation})
            return jsonify({'ha_results': map(make_public_results,
                                              results)})

        def get_failed_result(step=None):
            return get_fomatted_result(
                name=service['name'],
                status="failed",
                analysis="cannot run " + step)

        def restart_scenario():
            observable.notify_observer(HAResult(
                name=service['name'], step=HAStep.STEP_4,
                stage=HAStage.EXECUTING, status=Status.SUCCEEDED))

            # record recovery time
            start_time = clock()
            while not master.get_ha_scenario_status:
                master.run_ha_scenario(ha_config=ha_config)
                sleep(1)

            end_time = clock()
            status = ": after " + str(end_time - start_time) + "s"
            observable.notify_observer(HAResult(
                name=service['name'], step=HAStep.STEP_4,
                stage=HAStage.EXECUTED, status=Status.SUCCEEDED + status))
            return get_fomatted_result(name=service['name'],
                                       status="successful",
                                       analysis="none")

        # register observers
        ha_web_observer = WebSocketObserver(ObserverInfoType.HA)
        ha_log_observer = LoggerObserver(LOG, ObserverInfoType.HA)
        observable.register_observer(ha_web_observer)
        observable.register_observer(ha_log_observer)

        observable.notify_observer(
            HAResult(name=service['name'],step=HAStep.STEP_1,
                     stage=HAStage.EXECUTING, status=Status.SUCCEEDED))

        # get config
        sedna_config_value = None
        master = None
        try:
            logging.config.fileConfig(os.environ["SEDNA_LOG_CONF"])
            config = SednaConfigParser(os.environ["SEDNA_CONF"])
            sedna_config_value = config.get_sedna_config()
            master = Master()
        except:
            observable.notify_observer(
                HAResult(name=service['name'], step=HAStep.STEP_1,
                         stage=HAStage.EXECUTED, status=Status.FAILED))
            return get_failed_result(HAStep.STEP_1)
        observable.notify_observer(
            HAResult(name=service['name'], step=HAStep.STEP_1,
                     stage=HAStage.EXECUTED, status=Status.SUCCEEDED))

        # start scenario
        ha_config = None
        scenario = None
        observable.notify_observer(
            HAResult(name=service['name'], step=HAStep.STEP_2,
                     stage=HAStage.EXECUTING, status=Status.SUCCEEDED))
        try:
            scenario = sedna_config_value.ha[service["name"]]
            ha_config = HAConfig(ip=ip, port=sedna_config_value.port,
                                 scenario=scenario, service=service,
                                 operation=operation)
            try:
                master.run_ha_scenario(ha_config=ha_config)
            except:
                observable.notify_observer(
                    HAResult(name=service['name'], step=HAStep.STEP_2,
                             stage=HAStage.EXECUTING,
                             status=Status.FAILED + ": Cannot run scenario"))
                return get_failed_result(HAStep.STEP_2)
        except:
            observable.notify_observer(
                HAResult(name=service['name'], step=HAStep.STEP_2,
                         stage=HAStage.EXECUTING,
                         status=Status.FAILED + ": Unable to set config"))
            return get_failed_result(HAStep.STEP_2)

        # check scenario status
        if master.get_ha_scenario_status(ha_config=ha_config):
            observable.notify_observer(
                HAResult(name=service['name'], step=HAStep.STEP_2,
                         stage=HAStage.EXECUTED, status=Status.SUCCEEDED))
        else:
            observable.notify_observer(
                HAResult(name=service['name'], step=HAStep.STEP_2,
                         stage=HAStage.EXECUTED,
                         status=Status.FAILED + ": Unable to run scenario"))
            return get_failed_result(HAStep.STEP_2)

        # service operation
        # TODO(Jiakun): Wait?
        # sleep(5)
        observable.notify_observer(
            HAResult(name=service['name'], step=HAStep.STEP_3,
                     stage=HAStage.EXECUTING, status=Status.SUCCEEDED))

        if operation == 'kill':
            try:
                services = [service]
                killer_config = KillerConfig(
                    port=sedna_config_value.port, ip=ip, services=services)
                kill_result = master.kill_service(killer_config)

                if kill_result[0]["status"] == "successful":
                    observable.notify_observer(
                        HAResult(name=service['name'], step=HAStep.STEP_3,
                                 stage=HAStage.EXECUTED, status=Status.SUCCEEDED))
                else:
                    observable.notify_observer(
                        HAResult(name=service['name'], step=HAStep.STEP_3,
                                 stage=HAStage.EXECUTED, status=Status.FAILED))
                    return get_failed_result(HAStep.STEP_3)
            except:
                observable.notify_observer(
                    HAResult(name=service['name'], step=HAStep.STEP_3,
                             stage=HAStage.EXECUTING, status=Status.FAILED))
                return get_failed_result(HAStep.STEP_3)

            # TODO: wait a while for response?
            # sleep(5)
            return restart_scenario()

        elif operation == 'restart':
            try:
                service["methods"] = "systemd"
                config = ServiceCommandConfig(
                    ip=service["ip"],
                    port=sedna_config_value.port,
                    service=service, operation=operation)
                result = master.run_service_command(
                    service_command_config=config)
                if result["status"] == "successful":
                    observable.notify_observer(
                        HAResult(name=service['name'], step=HAStep.STEP_3,
                                 stage=HAStage.EXECUTED, status=Status.SUCCEEDED))
                else:
                    observable.notify_observer(
                        HAResult(name=service['name'], step=HAStep.STEP_3,
                                 stage=HAStage.EXECUTED, status=Status.FAILED))
                    return get_failed_result(HAStep.STEP_3)
            except:
                observable.notify_observer(
                    HAResult(name=service['name'], step=HAStep.STEP_3,
                             stage=HAStage.EXECUTING, status=Status.FAILED))
                return get_failed_result(HAStep.STEP_3)

            # check scenario status

            # TODO: wait a while for response?
            # sleep(5)
            return restart_scenario()

        elif operation == 'start' or operation == 'stop':
            try:
                service["methods"] = "systemd"
                config = ServiceCommandConfig(
                    ip=service["ip"],
                    port=sedna_config_value.port,
                    service=service, operation=operation)
                result = master.run_service_command(
                    service_command_config=config)
                if result["status"] == "successful":
                    observable.notify_observer(
                        HAResult(name=service['name'], step=HAStep.STEP_3,
                                 stage=HAStage.EXECUTED, status=Status.SUCCEEDED))
                else:
                    observable.notify_observer(
                        HAResult(name=service['name'], step=HAStep.STEP_3,
                                 stage=HAStage.EXECUTED, status=Status.FAILED))
                    return get_failed_result(HAStep.STEP_3)
            except:
                observable.notify_observer(
                    HAResult(name=service['name'], step=HAStep.STEP_3,
                             stage=HAStage.EXECUTING, status=Status.FAILED))
                return get_failed_result(HAStep.STEP_3)

            # check scenario status

            # TODO: wait a while for response?
            # sleep(5)

            observable.notify_observer(
                HAResult(name=service['name'], step=HAStep.STEP_4,
                         stage=HAStage.EXECUTING, status=Status.SUCCEEDED))
            try:
                if master.get_ha_scenario_status(ha_config=ha_config):
                    observable.notify_observer(
                        HAResult(name=service['name'], step=HAStep.STEP_4,
                                 stage=HAStage.EXECUTED, status=Status.SUCCEEDED))
                else:
                    observable.notify_observer(
                        HAResult(name=service['name'], step=HAStep.STEP_4,
                                 stage=HAStage.EXECUTED, status=Status.FAILED))
                    return get_failed_result(HAStep.STEP_4)
            except:
                observable.notify_observer(
                    HAResult(name=service['name'], step=HAStep.STEP_4,
                             stage=HAStage.EXECUTING, status=Status.FAILED))
                return get_failed_result(HAStep.STEP_4)

        # return positive result
        return get_fomatted_result(name=service['name'],
                                   status="successful",
                                   analysis="none")

    def get_resource_clean_up_result(self):
        logging.config.fileConfig(os.environ["SEDNA_LOG_CONF"])
        config = SednaConfigParser(os.environ["SEDNA_CONF"])
        sedna_config_value = config.get_sedna_config()
        master = Master()
        return master.clean_up_resource(sedna_config_value=sedna_config_value)


def convert_to_dicts(objs):
    """
    The function to convert object list from Object list to Dict list.
    :param objs: Object list
    :return: a list of dict to display the content of objs
    """
    obj_list = []

    for obj in objs:
        dict = {}
        dict.update(obj.__dict__)
        obj_list.append(dict)

    return obj_list


def convert_to_dict(obj):
    """
    The function to convert object list from Object to Dict.
    :param obj: Object
    :return: a dict to display the content of obj
    """

    dict = {}
    dict.update(obj.__dict__)
    return dict


app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


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


@app.route('/master/api/v1.0/results', methods=['GET'])
def get_results():
    master_restful = MasterRestful()
    raw_nodes_results = master_restful.get_results()
    for node_result in raw_nodes_results:
        for result in node_result.result:
            result.service = convert_to_dict(result.service)
        node_result.result = convert_to_dicts(node_result.result)
    result_dict = convert_to_dicts(raw_nodes_results)
    return jsonify({'results': map(make_public_results, result_dict)})


def format_output(raw_result, method=None):
    results = []
    results.append({'status': raw_result["status"]})
    results.append({'name': raw_result["service"]["name"]})
    results.append({'ip': raw_result["service"]["ip"]})
    results.append({'operation': method})
    return jsonify({'command_results': map(make_public_results,
                                           results)})


@app.route('/master/api/v1.0/service_command/<service_command>',
           methods=['GET'])
def get_command_results(service_command):
    """
    Kill a service by a given name on a node (ip)
    :param service_command:
    :return:
    """
    tokens = []
    for url_token in service_command.split('&'):
        tokens.append(url_token.split('='))
    dict_tokens = dict(tokens)
    master_restful = MasterRestful()
    dict_service = {"name": dict_tokens['name'],
                    "ip": dict_tokens['ip'],
                    "methods": ""}

    if dict_tokens['operation'] == 'kill':
        # kill a service
        dict_service["methods"] = "kill"
        services = [dict_service]
        raw_nodes_results = master_restful.get_kill_service_results(
            ip=dict_tokens['ip'], services=services)
        return format_output(raw_nodes_results[0],
                             dict_tokens['operation'])
    elif dict_tokens['operation'] in ['restart', 'start', 'stop']:
        # restart a service
        dict_service["methods"] = "systemd"
        raw_nodes_results =\
            master_restful.get_service_command_results(
                service=dict_service, operation=dict_tokens['operation'])
        return format_output(raw_nodes_results,
                             dict_tokens['operation'])


@app.route('/master/api/v1.0/run_scenarios', methods=['GET'])
def run_scenario_tests():
    def start_scenarios():

        scenario_observable = Observable()

        front_end_observer = WebSocketObserver(
            info_type=ObserverInfoType.SCENARIO)
        scenario_observable.register_observer(front_end_observer)

        # log_observer = ScenarioLoggerObserver(LOG)
        # scenario_observable.register_observer(log_observer)

        scenario_list = ScenarioList(scenario_observable)
        scenario_list.register_scenario(DEFUALT_SCENARIOS_LIST)
        scenario_list.run_scenario_tests()

    server_thread = Thread(target=start_scenarios)
    server_thread.setDaemon(True)

    server_thread.start()

    return jsonify({'run_scenarios': "ok"})


@app.route('/master/api/v1.0/ha/<service_command>', methods=['GET'])
def run_ha_tests(service_command):
    tokens = []
    for url_token in service_command.split('&'):
        tokens.append(url_token.split('='))
    dict_tokens = dict(tokens)
    master_restful = MasterRestful()
    dict_service = {"name": dict_tokens['name'],
                    "ip": dict_tokens['ip'],
                    "methods": dict_tokens['operation']}
    result = master_restful.get_ha_results(
        ip=dict_tokens['ip'], service=dict_service,
        operation=dict_tokens['operation'])
    return result


@app.route('/master/api/v1.0/scenario_end_and_cleanup', methods=['GET'])
def end_ha_tests():
    observable.clear_observable(ObserverInfoType.END)
    # TODO: delete all resources


def run():
    app.run(host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

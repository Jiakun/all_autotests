#!/usr/bin/python
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import url_for
from threading import Thread

from sedna.master import Master
from sedna.scenario.scenario import ScenarioList

from sedna.observer import Observable
from sedna.observer import LoggerObserver
from sedna.observer import WebSocketObserver
from sedna.observer import ObserverInfoType

from sedna.config import SednaConfigParser
from sedna.config import KillerConfig
from sedna.config import ServiceCommandConfig
from sedna.config import SEDNA_CONF
from sedna.rest.hatest import MasterHATest

from sedna.scenario.openstack.openstack import ServerCreateScenario, \
    ServerAttachVolumeScenario, ServerRebootScenario, \
    PortCreateScenario, SnapshotCreateScenario, VolumeCreateScenario, \
    UserCreateScenario, DomainCreateScenario, ProjectCreateScenario, \
    SecurityGroupCreateScenario, AssociateFloatingipScenario, \
    KeypairCreateScenario, LoadBalancerCreateScenario, \
    LBaaSPoolCreateScenario, LBaaSMemberCreateScenario, \
    ListenerCreateScenario, LBaaSHealthMonitorCreateScenario

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

observable = Observable()


class MasterRestful(object):
    """
    The class to return master results.
    """
    def get_results(self):
        config = SednaConfigParser(SEDNA_CONF)
        sedna_config_value = config.get_sedna_config()
        master = Master()
        return master.verify_nodes(sedna_config_value=sedna_config_value)

    def get_kill_service_results(self, ip=None, services=None):
        config = SednaConfigParser(SEDNA_CONF)
        sedna_config_value = config.get_sedna_config()
        config = KillerConfig(port=sedna_config_value.port, ip=ip,
                              services=services)
        master = Master()
        return master.kill_service(sedna_kill_service_config_value=config)

    def get_service_command_results(self, service=None, operation=None):
        config = SednaConfigParser(SEDNA_CONF)
        sedna_config_value = config.get_sedna_config()
        config = ServiceCommandConfig(ip=service["ip"],
                                      port=sedna_config_value.port,
                                      service=service, operation=operation)
        master = Master()
        return master.run_service_command(service_command_config=config)

    def get_ha_results(self, operation=None, service=None, ip=None):
        ha_tester = MasterHATest(operation=operation,
                                 service=service,
                                 ip=ip)
        return ha_tester.run()

    def get_resource_clean_up_result(self):
        config = SednaConfigParser(SEDNA_CONF)
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


@app.route('/master/api/v1.0/scenarios/available_scenarios', methods=['GET'])
def get_scenario_available():
    sedna_config_parser = SednaConfigParser(SEDNA_CONF)
    scenario_name_list = sedna_config_parser.get_scenario_available()
    return jsonify({'scenarios_available': scenario_name_list})


@app.route('/master/api/v1.0/scenarios/run_scenarios/<scenario_name>',
           methods=['GET'])
def run_scenario_tests(scenario_name):
    scenario_to_run = scenario_name.split('=')[1].split('&')

    if scenario_to_run is None:
        return jsonify({'run_scenarios': "Please select an scenario to run!"})

    scenarios_class_selected = []
    if str(scenario_to_run[0]) == "all":
        scenarios_class_selected = DEFUALT_SCENARIOS_LIST
    else:
        defualt_scenario_class_name = []
        for scenario_class in DEFUALT_SCENARIOS_LIST:
            defualt_scenario_class_name.append(scenario_class.__name__.lower())

        for scenario_name in scenario_to_run:
            if scenario_name.lower() not in defualt_scenario_class_name:
                return jsonify(
                    {'run_scenarios': scenario_name +
                                      "doesn't exist! "
                                      "Please check option name of "
                                      "[steps_of_scenario] in sedna.conf."})

        for scenario_class in DEFUALT_SCENARIOS_LIST:
            if scenario_class.__name__.lower() in scenario_to_run:
                scenarios_class_selected.append(scenario_class)

    def start_scenarios():

        scenario_observable = Observable()
        scenario_step_observable = Observable()

        front_end_observer = WebSocketObserver(
            info_type=ObserverInfoType.SCENARIO)
        scenario_observable.register_observer(front_end_observer)

        log_observer = LoggerObserver(info_type=ObserverInfoType.SCENARIO)
        scenario_observable.register_observer(log_observer)

        front_end_step_observer = WebSocketObserver(
            info_type=ObserverInfoType.SCENARIO_STEP)
        scenario_step_observable.register_observer(front_end_step_observer)

        log_step_observer = LoggerObserver(info_type=ObserverInfoType.SCENARIO_STEP)
        scenario_step_observable.register_observer(log_step_observer)

        scenario_list = ScenarioList(
            scenario_observable, scenario_step_observable)
        scenario_list.register_scenario(scenarios_class_selected)
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


@app.route('/master/api/v1.0/ha/scenario_end_and_cleanup', methods=['GET'])
def end_ha_tests():
    observable.clear_observable(ObserverInfoType.END)
    # TODO: delete all resources


def run():
    app.run(host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

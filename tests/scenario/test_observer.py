from unittest import TestCase

from threading import Thread
import requests

from flask import jsonify

from sedna.rest.master import run
from sedna.rest.master import app
from sedna.rest.master import PORT
from sedna.scenario.observer import ScenarioList
from sedna.observable import Observable
from sedna.rest.master import DEFUALT_SCENARIOS_LIST


class ScenarioRunnerRestTest(TestCase):
    """
    The test cases to test code in rest_1.py.
    """

    def setUp(self):

        def start_rest_server():
            run()

        server_thread = Thread(target=start_rest_server)
        server_thread.setDaemon(True)

        server_thread.start()

    def test_scenario_tests(self):
        request_result = \
            requests.get("http://localhost:" + str(PORT) +
                         "/master/api/v1.0/mockedRunScenarioTests")
        self.assertEquals(request_result.status_code, 200)


@app.route('/master/api/v1.0/mockedRunScenarioTests', methods=['GET'])
def mocked_run_scenario_tests():
    front_end_observer = _MockedObserver()
    mocked_obserable = Observable()
    mocked_obserable.register_observer(front_end_observer)

    scenario_list = ScenarioList(mocked_obserable)
    scenario_list.register_scenario(DEFUALT_SCENARIOS_LIST)
    scenario_list.run_scenario_tests()
    return jsonify({'run scenario': "ok"})


class _MockedObserver(object):
    def update(self, result):
        return result

    def end(self):
        return True

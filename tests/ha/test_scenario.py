from sedna.ha.scenario import HAScenarioList, HAVolumeCreateScenario
from sedna.observer import Observable, LoggerObserver, ObserverInfoType
from sedna.scenario.scenario import Status
from unittest2 import TestCase
from threading import Thread
from xmlrpclib import ServerProxy
import random
import logging.config
from sedna.config import SEDNA_LOG_CONF

LOG = logging.getLogger("tester")
logging.config.fileConfig(SEDNA_LOG_CONF)


class HAScenarioTest(TestCase):
    def setUp(self):
        self.observable = Observable()
        self.step_observable = Observable()
        self.observer = LoggerObserver(LOG, ObserverInfoType.HA)
        self.step_observer = LoggerObserver(LOG, ObserverInfoType.SCENARIO_STEP)
        self.observable.register_observer(self.observer)
        self.step_observable.register_observer(self.step_observer)

        self.ha_scenario_list = HAScenarioList(
            observable=self.observable, step_observable=self.step_observable)

    def test_execute(self):
        self.ha_scenario_list.register_scenario([HAVolumeCreateScenario])
        self.ha_scenario_list.run_scenario_tests()

    def tearDown(self):
        pass

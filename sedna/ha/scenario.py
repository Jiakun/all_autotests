from sedna.scenario.openstack.openstack import ServerCreateScenario, \
    VolumeCreateScenario, KeypairCreateScenario
from sedna.observer import Observable, WebSocketObserver, LoggerObserver, \
    ObserverInfoType
from sedna.scenario.scenario import ScenarioList


class HAScenarioList(ScenarioList):
    """Base class contains shared logic to manipulate HA scenarios"""
    def __init__(self, observable, step_observable):
        super(HAScenarioList, self).__init__(observable, step_observable)

    def run_scenario_tests(self):
        for scenario in self.scenario_list:
            scenario.execute(observable=self.observable,
                             step_observable=self.step_observable,
                             is_clean_up=False)
            if scenario == self.scenario_list[-1]:
                self.observable.notify_observer(ObserverInfoType.END)
                self.step_observable.notify_observer(ObserverInfoType.END)


class HATokenCreateScenario:
    def __init__(self):
        pass


class HAVolumeCreateScenario(VolumeCreateScenario):
    def __init__(self):
        super(HAVolumeCreateScenario, self).__init__()


class HAServerCreateScenario(ServerCreateScenario):
    def __init__(self):
        super(HAServerCreateScenario, self).__init__()


class HAKeypairCreateScenario(KeypairCreateScenario):
    def __init__(self):
        super(HAKeypairCreateScenario, self).__init__()

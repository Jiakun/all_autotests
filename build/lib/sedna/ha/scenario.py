from sedna.scenario.openstack.openstack import RouterCreateScenario
from sedna.scenario.openstack.openstack import ServerCreateScenario
from sedna.scenario.openstack.openstack import VolumeCreateScenario
from sedna.scenario.openstack.openstack import KeypairCreateScenario
from sedna.observer import Observable, WebSocketObserver, LoggerObserver, \
    ObserverInfoType


class HAScenario(object):
    """Base class contains shared logic to manipulate HA scenarios"""
    def __init__(self, scenario_class, observable=None):
        if observable is None:
            self.observable = Observable()
            # Default logger observer
            self.observable.register_observer(
                LoggerObserver(ObserverInfoType.HA))
        else:
            self.observable = observable

        self._scenario_class = scenario_class()

    def execute(self):
        return self._scenario_class.execute(self.observable)


class HAKeypairCreateScenario(object):
    def execute(self, observable):
        keypair = KeypairCreateScenario()
        keypair.execute(observable)
        return keypair.scenario.status


class HAVolumeCreateScenario(object):
    def execute(self, observable):
        volume = VolumeCreateScenario()
        volume.execute(observable)
        return volume.scenario.status


class HARouterCreateScenario(object):
    def execute(self, observable):
        router = RouterCreateScenario()
        router.execute(observable)
        return router.scenario.status


class HAServerCreateScenario(object):
    def execute(self, observable):
        server = ServerCreateScenario()
        server.execute(observable)
        return server.scenario.status

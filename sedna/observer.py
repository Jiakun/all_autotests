import requests
import logging.config
from sedna.config import SEDNA_LOG_CONF


class ObserverInfoType:
    def __init__(self):
        pass

    SCENARIO = "Scenario test"
    SCENARIO_STEP = "Scenario test result by step"
    HA = "HA test"
    END = "End"


class Observable:
    def __init__(self):
        self.registered_observers = []

    def register_observer(self, observer):
        if observer not in self.registered_observers:
            self.registered_observers.append(observer)

    def cancel_observer(self, observer):
        self.registered_observers.remove(observer)

    def notify_observer(self, context):
        for observer in self.registered_observers:
            observer.update(context)

    def clear_observable(self, info):
        for observer in self.registered_observers:
            observer.update(info)
        self.registered_observers = []


class Observer:
    def __init__(self, info_type=None):
        self.info_type = info_type

    def _format_info(self, info):
        pass

    def update(self, info):
        pass


class WebSocketObserver(Observer):
    """
    The class to ask the request to send info to node.js.
    """
    def __init__(self, info_type=None):
        Observer.__init__(self, info_type=info_type)

    def _format_info(self, info):
        """
        format result to json
        :param result:
        :return:
        """
        return {"name": info.name,
                "step": info.step,
                "stage": info.stage,
                "status": info.status}

    def update(self, info):
        """
        Update status through websocket
        :param info:
        :return:
        """

        # Send end info
        if info == ObserverInfoType.END:
            if self.info_type == ObserverInfoType.SCENARIO:
                requests.get('http://localhost:9999/end_scenario')
            elif self.info_type == ObserverInfoType.HA:
                requests.get('http://localhost:9999/end_ha_status')
            elif self.info_type == ObserverInfoType.SCENARIO_STEP:
                requests.get('http://localhost:9999/end_scenario_step')
            else:
                raise Exception("Cannot find the type of info.")
            return

        # Update info
        if self.info_type == ObserverInfoType.SCENARIO:
            requests.post('http://localhost:9999/scenario_result',
                          json=self._format_info(info))
        elif self.info_type == ObserverInfoType.HA:
            # update result for HA scenario
            requests.post('http://localhost:9999/ha_status_result',
                          json=self._format_info(info))
        elif self.info_type == ObserverInfoType.SCENARIO_STEP:
            requests.post('http://localhost:9999/scenario_step_result',
                          json=self._format_info(info))
        else:
            raise Exception("Cannot find the type of info.")


class LoggerObserver(Observer):
    """
    Log observer: record logs
    """
    def __init__(self, logger=None, info_type=None):
        Observer.__init__(self, info_type=info_type)
        if logger is None:
            self.logger = logging.getLogger("")
            logging.config.fileConfig(SEDNA_LOG_CONF)
        else:
            self.logger = logger

    def _format_info(self, info):
        return ("Name: %s, Step: %s, Stage: %s, Status: %s" %
                (info.name, info.step, info.stage, info.status))

    def update(self, info):
        """
        :param info:
        :return:
        """

        # Send end info
        if info == ObserverInfoType.END:
            if self.info_type == ObserverInfoType.SCENARIO:
                self.logger.info("********* Scenario End *********")
            elif self.info_type == ObserverInfoType.HA:
                self.logger.info("********* HA Test End *********")
            elif self.info_type == ObserverInfoType.SCENARIO_STEP:
                self.logger.info("********* Scenario Step End *********")
            else:
                raise Exception("Cannot find the type of info.")
            return

        # Update info
        if self.info_type == ObserverInfoType.SCENARIO:
            self.logger.info(
                "[ScenarioTest]: " + self._format_info(info))
        elif self.info_type == ObserverInfoType.HA:
            self.logger.info(
                "[HATest]: " + self._format_info(info))
        elif self.info_type == ObserverInfoType.SCENARIO_STEP:
            self.logger.info(
                "[ScenarioTest-Step]: " + self._format_info(info))
        else:
            raise Exception("Cannot find the type of info.")


class DefaultObservable(object):
    def __init__(self, info_type):
        self.observable = Observable()
        self.observable.register_observer(
            LoggerObserver(info_type=info_type))
        self.observable.register_observer(
            WebSocketObserver(info_type))
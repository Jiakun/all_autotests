import requests


class ObserverInfoType:
    def __init__(self):
        pass

    SCENARIO = "Scenario test"
    SCENARIO_END = "The end of scenario test"
    HA = "HA test"
    HA_END = "The end of HA test"
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
        if info == ObserverInfoType.END:
            if self.info_type == ObserverInfoType.SCENARIO:
                self.info_type = ObserverInfoType.SCENARIO_END
            elif self.info_type == ObserverInfoType.HA:
                self.info_type = ObserverInfoType.HA_END

        if self.info_type == ObserverInfoType.SCENARIO:
            # Update result for scenario test
            requests.post('http://localhost:9999/scenario_result',
                          json=self._format_info(info))
        elif self.info_type == ObserverInfoType.SCENARIO_END:
            # Send end request to close websocket
            requests.get('http://localhost:9999/end_scenario')
        elif self.info_type == ObserverInfoType.HA:
            # update result for HA scenario
            requests.post('http://localhost:9999/ha_status_result',
                          json=self._format_info(info))
        elif self.info_type == ObserverInfoType.HA_END:
            # Send end request to close websocket
            requests.get('http://localhost:9999/end_ha_status')

        else:
            raise Exception("Cannot find the type of info.")


class LoggerObserver(Observer):
    """
    Log observer: record logs
    """
    def __init__(self, logger=None, info_type=None):
        Observer.__init__(self, info_type=info_type)
        self.logger = logger

    def _format_info(self, info):
        return ("Service: %s, Step: %s, Stage: %s, Status: %s" %
                (info.name, info.step, info.stage, info.status))

    def update(self, info):
        """
        :param info:
        :return:
        """
        if info == ObserverInfoType.END:
            if self.info_type == ObserverInfoType.SCENARIO:
                self.info_type = ObserverInfoType.SCENARIO_END
            elif self.info_type == ObserverInfoType.HA:
                self.info_type = ObserverInfoType.HA_END

        if self.info_type == ObserverInfoType.SCENARIO:
            # Update info
            self.logger.info(
                "[ScenarioTest]: " + self._format_info(info))
        elif self.info_type == ObserverInfoType.SCENARIO_END:
            # Send end info
            self.logger.info("********* Scenario End *********")
        elif self.info_type == ObserverInfoType.HA:
            self.logger.info(
                "[HA_result]: " + self._format_info(info))
        elif self.info_type == ObserverInfoType.HA_END:
            self.logger.info("********* HA Test End *********")
        else:
            raise Exception("Cannot find the type of info.")

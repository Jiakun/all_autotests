from sedna.scenario.scenario import ScenarioResult
from sedna.ha.scenario import HAServerCreateScenario, HAVolumeCreateScenario


class HAStep(object):
    def __init__(self):
        pass

    STEP_1 = "Config Setting"
    STEP_2 = "Scenario Test Start"
    STEP_3 = "Service Operation"
    STEP_4 = "Scenario Test Check"
    Finished = "Finished"


class HAStage(object):
    def __init__(self):
        pass

    EXECUTING = "executing"
    EXECUTED = "executed"


class HAResult(ScenarioResult):
    def __init__(self, name, step, stage, status):
        super(HAResult, self).__init__(name, step, stage, status)


HA_SCENARIO_LIST = [HAVolumeCreateScenario, HAServerCreateScenario]


class ScenarioChecker(object):
    def __init__(self):
        pass

    @staticmethod
    def get_scenario_class(scenario_class_list, scenario_name):
        for scenario_class in scenario_class_list:
            if scenario_class.__name__.lower() == scenario_name.lower():
                return scenario_class
        raise Exception("Cannot find the scenario class.")

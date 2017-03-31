from sedna.scenario.scenario import ScenarioResult
from sedna.ha.scenario import HAServerCreateScenario, HAVolumeCreateScenario


class HAStep():
    STEP_1 = "Config Setting"
    STEP_2 = "Scenario Test Start"
    STEP_3 = "Service Operation"
    STEP_4 = "Scenario Test Check"


class HAStage():
    EXECUTING = "executing"
    EXECUTED = "executed"


class HAResult(ScenarioResult):
    def __init__(self, name, step, stage, status):
        super(HAResult, self).__init__(name, step, stage, status)


class HAScenarioMap(object):
    HA_SCENARIO_MAP= {
        "VolumeCreate": HAVolumeCreateScenario(),
        "ServerCreate": HAServerCreateScenario()
    }
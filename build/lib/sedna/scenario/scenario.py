"""
this module defines the execution process and class structure for scenario test
"""
from abc import abstractmethod
import logging
import sys
from sedna.error import NoneReferenceError
from sedna.observer import ObserverInfoType

LOG = logging.getLogger("sedna.scenario")


class Stage(object):
    """Class contains enumerations defining stages of the test process"""
    QUEUED = "queued"

    EXECUTING = "executing"

    EXECUTED = "executed"

    CLEANING_UP = "cleaning_up"

    FINISHED = "finished"


class Status(object):
    """
    Class contains enumerations defining status of the test scenario and steps
    """
    PENDING = "pending"

    SUCCEEDED = "succeeded"

    FAILED = "failed"


class ScenarioResult(object):
    """
    The class defines the attributes in the scenario test
    """
    def __init__(self, name=None, step=None, stage=None, status=None, info_type=None):
        self.name = name
        self.step = step
        self.stage = stage
        self.status = status
        self.info_type = info_type


class Scenario(object):
    """
    The class defines the whole process. The test logic should be in steps.
    Scenario will execute steps one by one, and pass the execution context
    across the steps.
    """

    def __init__(self, name, steps, context, observable):
        """
        Initialization.
        :param name: the string name of the scenario
        :param steps: the steps to execute in this scenario
        :param context: the execution context shared across the steps
        :param observable: the Observeable object
        response requests from observable
        """
        if not name:
            raise NoneReferenceError("name can't be None!")
        self.name = name

        if not steps:
            raise NoneReferenceError("steps can't be None")

        if len(steps) < 1:
            raise ValueError("steps are empty!")

        self.steps = steps

        if not context:
            raise NoneReferenceError("context can't be None!")

        self.context = context

        self.observable = observable

        self.stage = Stage.QUEUED
        self.status = Status.PENDING

    def execute(self):
        """
        The method defines the scenario test process.
        It executes the steps one by one,  changes its own and steps' status
        properly. And then it will call steps' cleanup method in reversed order
        one by one.
        """
        self.stage = Stage.EXECUTING
        final_status = Status.SUCCEEDED

        for step in self.steps:
            if not step:
                self.observable.notify_observer(
                    ScenarioResult(name=self.name, step="no steps",
                                   stage=self.stage, status=self.status))

                raise NoneReferenceError("step can't be None")

            if not isinstance(step, Step):
                self.observable.notify_observer(
                    ScenarioResult(name=self.name, step="no step instance",
                                   stage=self.stage, status=self.status))

                raise ValueError(
                    "step %s is not the instance of %s", (step, Step))

            try:
                step.stage = Stage.EXECUTING
                step.execute(self.context)
            except Exception, e:
                LOG.exception(
                    "Exception occurs during executing test step %s: %s"
                    % (step, e))

                step.status = Status.FAILED
                final_status = Status.FAILED

                step.execution_error_info = ErrorInfo(e, sys.exc_traceback)

                break
            finally:
                step.stage = Stage.EXECUTED

            step.status = Status.SUCCEEDED

        self.stage = Stage.CLEANING_UP

        for cleanup_step in reversed(self.steps):
            if cleanup_step.stage is Stage.QUEUED:
                continue

            try:
                cleanup_step.stage = Stage.CLEANING_UP
                cleanup_step.cleanup(self.context)
            except Exception, e:
                LOG.exception(
                    "Exception occurs during cleanup test step %s: %s"
                    % (cleanup_step, e))
                cleanup_step.status = Status.FAILED
                final_status = Status.FAILED

                cleanup_step.cleanup_error_info =\
                    ErrorInfo(e, sys.exc_traceback)
                break

            cleanup_step.stage = Stage.FINISHED

        self.stage = Stage.FINISHED
        self.status = final_status
        self.observable.notify_observer(
            ScenarioResult(name=self.name, step="steps end",
                           stage=self.stage, status=self.status))


class Step(object):
    """Abstract class defines test steps."""

    def __init__(self, name):
        """
        Initialization
        :param name: the string name of the current step
        """
        if not name:
            raise NoneReferenceError("name can't be null!")
        self.name = name

        self.status = Status.PENDING
        self.stage = Stage.QUEUED

        self.execution_error_info = None
        self.cleanup_error_info = None

    @abstractmethod
    def execute(self, context):
        """
        The test logic of the current step. If the step fails, it should raise
        an exception.
        :param context: the test context shared across steps.
        """
        raise NotImplementedError("execute")

    @abstractmethod
    def cleanup(self, context):
        """
        The cleanup method of the current step.
        :param context: the test context shared across steps
        :return:
        """
        raise NotImplementedError("cleanup")


class Context(object):
    """The abstract class to contain context variables across test steps"""
    def __init__(self, name, os_session):
        self.name = name
        self.os_session = os_session


class ErrorInfo(object):

    def __init__(self, error, traceback):
        if not error:
            raise NoneReferenceError("error can't be None!")

        if not isinstance(error, Exception):
            raise ValueError("error %s is not an Exception " % error)

        if not traceback:
            raise NoneReferenceError("traceback can't be None!")

        self.error = error
        self.traceback = traceback


class ScenarioList(object):
    """
    Run a group of scenarios from list
    """
    def __init__(self, observable):
        self.scenario_list = []
        self.observable = observable

    def register_scenario(self, scenario_classes):
        for scenario_class in scenario_classes:
            scenario = scenario_class()
            self.scenario_list.append(scenario)

    def run_scenario_tests(self):
        for scenario in self.scenario_list:
            scenario.execute(observable=self.observable)
            if scenario == self.scenario_list[-1]:
                self.observable.notify_observer(ObserverInfoType.END)

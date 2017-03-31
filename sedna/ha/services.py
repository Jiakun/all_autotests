import re
import shlex
import subprocess
from time import sleep

from sedna.common import Service
from sedna.common import Result
from sedna.ha.ha import ScenarioChecker, HA_SCENARIO_LIST, HAResult
from sedna.observer import Observable, WebSocketObserver, LoggerObserver, ObserverInfoType,\
    DefaultObservable

from sedna.scenario.scenario import Status, ScenarioResult, Stage

import logging

LOG = logging.getLogger("")


class KillStep(object):
    Init = "Initialization"
    GetPid = "Get pid of the service"
    KillPid = "Kill the pid of the service"
    CheckPid = "Check the existing of the pid of the service"


class SystemdContralStep(object):
    Init = "Initialization"
    Run = "Run systemd command"


class ServiceKiller(object):
    """
    Service Killer
    """
    def __init__(self, observable=None):
        if observable is None:
            self.observable = DefaultObservable(
                info_type=ObserverInfoType.HA).observable
        else:
            self.observable = observable

    def kill_services(self, services):
        """
        This class kills a group of services on a node
        :param services:
        :return:
        """
        service_results = []

        self.observable.notify_observer(
            HAResult(name=self.__class__.__name__, step=KillStep.Init,
                     stage=Stage.EXECUTING, status=Status.SUCCEEDED))

        for service in services:
            service_result = self.execute(service_name=service.name)
            service_result = \
                Result(service=service,
                       status=service_result[0],
                       analysis=service_result[1])
            service_results.append(service_result)

        LOG.debug("NodeSampler return :%s" % service_results)
        # self._formated_output(service_results)
        return service_results

    def _formated_output(self, results):
        """
        This function formats results from killer to log
        :param results:
        :return:
        """
        failed_count = 0
        passed_count = 0
        for result in results:
            self.observable.notify_observer(
                HAResult(name=self.__class__.__name__, step="",
                         stage=Stage.FINISHED, status=result.status + ": " + result.analysis))

            if result.status == Status.FAILED:
                failed_count += 1
            if result.status == Status.SUCCEEDED:
                passed_count += 1
        count_output_str = (": %s services was killed by the server. %s services failed to be killed",
                            str(passed_count), str(failed_count))
        self.observable.notify_observer(
            HAResult(name=self.__class__.__name__, step="",
                     stage=Stage.FINISHED, status=count_output_str))

    def execute(self, service_name):
        """
        This function kill a service by name and node ip
        :param service_name:
        :return:
        """
        if re.findall(r"openstack", service_name):
            service_name =\
                re.findall(r"openstack-(.+).service", service_name)[0]
        elif re.findall(r"service", service_name):
            service_name = re.findall(r"(.+).service", service_name)[0]

        service_pid = ""

        self.observable.notify_observer(
            HAResult(name=self.__class__.__name__, step=KillStep.Init,
                     stage=Stage.EXECUTED, status=Status.SUCCEEDED + ": " + service_name))

        # Kill strategy:
        # Find a process (ppid=1), a child of root process (pid=1)
        # ps -eo pid,ppid,command --sort ppid|grep nova-api
        try:
            self.observable.notify_observer(
                HAResult(name=service_name, step=KillStep.GetPid,
                         stage=Stage.EXECUTING, status=Status.SUCCEEDED))

            command_line = "ps -eo ppid,pid,command --sort ppid"
            args = shlex.split(command_line)
            output = subprocess.Popen(args, stdout=subprocess.PIPE)

            output1 = subprocess.Popen(["grep", service_name],
                                       stdin=output.stdout,
                                       stdout=subprocess.PIPE)
            ppid_pid_lists = subprocess.Popen(["awk", "{print $1,$2}"],
                                              stdin=output1.stdout,
                                              stdout=subprocess.PIPE)
            ppid_pid_lists_str = ppid_pid_lists.stdout.readlines()

            if len(ppid_pid_lists_str) < 1:
                self.observable.notify_observer(
                    HAResult(name=service_name, step=KillStep.GetPid,
                             stage=Stage.EXECUTED, status=Status.SUCCEEDED + ": no such service."))
                return [Status.SUCCEEDED, "no service to be killed"]

            ppid_pid_lists_strs = str(ppid_pid_lists_str).split(",")
            for ppid_pid in ppid_pid_lists_strs:
                ppid_pid = ppid_pid.strip()
                pid = re.findall(r"\d+", ppid_pid.split(" ")[1])[0]
                ppid = re.findall(r"\d+", ppid_pid.split(" ")[0])[0]

                if (ppid == "1") and (pid != "1"):
                    service_pid = pid
                    break

            if service_pid == "":
                self.observable.notify_observer(
                    HAResult(name=service_name, step=KillStep.GetPid,
                             stage=Stage.EXECUTED, status=Status.SUCCEEDED + ": no such service."))
                return [Status.SUCCEEDED, "no service to be killed"]
        except:
            self.observable.notify_observer(
                HAResult(name=service_name, step=KillStep.GetPid,
                         stage=Stage.EXECUTED, status=Status.FAILED))
            return [Status.FAILED, "none"]

        self.observable.notify_observer(
            HAResult(name=service_name, step=KillStep.GetPid,
                     stage=Stage.EXECUTED, status=Status.SUCCEEDED + ": pid-" + service_pid))

        # kill pid
        try:
            self.observable.notify_observer(
                HAResult(name=service_name, step=KillStep.KillPid,
                         stage=Stage.EXECUTING, status=Status.SUCCEEDED))

            kill_output = subprocess.Popen(["kill", "-9", service_pid],
                                           stdout=subprocess.PIPE)
        except:
            self.observable.notify_observer(
                HAResult(name=service_name, step=KillStep.KillPid,
                         stage=Stage.EXECUTED, status=Status.FAILED + ": pid-" + service_pid))
            return [Status.FAILED, "none"]

        self.observable.notify_observer(
            HAResult(name=service_name, step=KillStep.KillPid,
                     stage=Stage.EXECUTED, status=Status.SUCCEEDED + ": pid-" + service_pid))

        # wait for the killing process
        sleep(3)

        # check whether the process is killed
        try:
            self.observable.notify_observer(
                HAResult(name=service_name, step=KillStep.CheckPid,
                         stage=Stage.EXECUTING, status=Status.SUCCEEDED))
            check_output = subprocess.Popen(["ps", "-ef"], stdout=subprocess.PIPE)
            check_output1 = subprocess.Popen(["grep", service_name],
                                             stdin=check_output.stdout,
                                             stdout=subprocess.PIPE)
            check_pid_lists = subprocess.Popen(["awk", "{print $2}"],
                                               stdin=check_output1.stdout,
                                               stdout=subprocess.PIPE)
            check_pid = subprocess.Popen(["grep", service_pid],
                                         stdin=check_pid_lists.stdout,
                                         stdout=subprocess.PIPE)
            check_pid = check_pid.stdout.readlines()
        except:
            self.observable.notify_observer(
                HAResult(name=service_name, step=KillStep.CheckPid,
                         stage=Stage.EXECUTED, status=Status.FAILED))
            return [Status.FAILED, "none"]

        if len(check_pid) < 1:
            self.observable.notify_observer(
                HAResult(name=service_name, step=KillStep.CheckPid,
                         stage=Stage.EXECUTED, status=Status.SUCCEEDED))
            return [Status.SUCCEEDED, "none"]
        else:
            analysis = "cannot kill pid-" + service_pid
            self.observable.notify_observer(
                HAResult(name=service_name, step=KillStep.CheckPid,
                         stage=Stage.EXECUTED, status=Status.FAILED + ": " + analysis))
            return [Status.FAILED, analysis]


class ServiceCommand(object):
    """
    The class runs commands by "systemctl".
    The commands includes "start", "restart", "stop".
    """
    def __init__(self, observable=None):
        self.command = None
        if observable is None:
            self.observable = DefaultObservable(
                info_type=ObserverInfoType.HA).observable
        else:
            self.observable = observable

    def execute(self, service_name, s_command):
        """
        This function runs the systemctl command
        :param service_name: service name
        :param s_command: service command: systmctl start, restart or stop
        :return:
        """
        self.observable.notify_observer(
            HAResult(name=service_name, step=SystemdContralStep.Init,
                     stage=Stage.EXECUTING, status=Status.SUCCEEDED))

        self.command = None
        try:
            self.command = shlex.split(s_command)
            self.command.append(service_name)
        except:
            analysis = "cannot parse the command"
            self.observable.notify_observer(
                HAResult(name=service_name, step=SystemdContralStep.Init,
                         stage=Stage.EXECUTED, status=Status.FAILED + ": " + analysis))
            return [Status.FAILED, analysis]

        self.observable.notify_observer(
            HAResult(name=service_name, step=SystemdContralStep.Init,
                     stage=Stage.EXECUTED, status=Status.SUCCEEDED))

        self.observable.notify_observer(
            HAResult(name=service_name, step=SystemdContralStep.Run,
                     stage=Stage.EXECUTING, status=Status.SUCCEEDED))

        try:
            output = subprocess.Popen(self.command, stdout=subprocess.PIPE)
        except:
            self.observable.notify_observer(
                HAResult(name=service_name, step=SystemdContralStep.Run,
                         stage=Stage.EXECUTED, status=Status.FAILED))
            return [Status.FAILED, "none"]

        result = output.stdout.readlines()

        if len(result) != 0:
            analysis = ": " + str(result)
            self.observable.notify_observer(
                HAResult(name=service_name, step=SystemdContralStep.Run,
                         stage=Stage.EXECUTED, status=Status.FAILED + analysis))
            return [Status.FAILED, analysis]

        self.observable.notify_observer(
            HAResult(name=service_name, step=SystemdContralStep.Run,
                     stage=Stage.EXECUTED, status=Status.SUCCEEDED))
        return [Status.SUCCEEDED, "none"]


class HAScenarioTestStep(object):
    Init = "Initialize HA scenario"
    RunOnce = "Run HA scenario once"
    Finished = "Finished HA scenario"
    Stop = "Stop HA scenario"
    Start = "Start HA scenario"
    GetStatus = "Get HA scenario status"


class NodeHATest(object):
    """
    The tester for HA
    """

    def __init__(self, observable=None, step_observable=None):
        """
        is_ha_run: whether to continue the scenario test
        is_ha_executed: whether the scenario has been run >= one time
        """
        self.is_ha_run = True
        self.is_ha_executed = False
        self.times = None
        if observable is None:
            self.observable = Observable()
            self.observable.register_observer(WebSocketObserver(info_type=ObserverInfoType.HA))
            self.observable.register_observer(LoggerObserver(info_type=ObserverInfoType.HA))
        else:
            self.observable = observable

        if step_observable is None:
            self.step_observable = Observable()
            self.step_observable.register_observer(WebSocketObserver(info_type=ObserverInfoType.HA))
            self.step_observable.register_observer(LoggerObserver(info_type=ObserverInfoType.HA))
        else:
            self.step_observable = step_observable

        self.scenario_class_name = None

    def run_ha_scenario(self, scenario_class, times=None):
        """
        This function runs ha scenario by given parameters
        :param scenario_class: the class for the scenario
        :param times: the times to run the scenario (default infinite)
        :return: True - exit safely; False - exit with errors
        """
        # Init

        self.scenario_class_name = scenario_class

        if times is not None:
            self.times = int(times)
            self.observable.notify_observer(ScenarioResult(
                name=self.scenario_class_name, step=HAScenarioTestStep.Init,
                stage=Stage.EXECUTED, status=Status.SUCCEEDED + ": run " + str(times) + " times."
            ))

        while self.is_ha_run:
            self.observable.notify_observer(ScenarioResult(
                name=self.scenario_class_name, step=HAScenarioTestStep.RunOnce,
                stage=Stage.EXECUTING, status=Status.SUCCEEDED
            ))

            try:
                scenario = ScenarioChecker.get_scenario_class(
                    scenario_name=self.scenario_class_name, scenario_class_list=HA_SCENARIO_LIST)()
                self.observable.notify_observer(ScenarioResult(
                    name=self.scenario_class_name, step=HAScenarioTestStep.Init,
                    stage=Stage.EXECUTING, status=Status.SUCCEEDED
                ))
            except:
                self.observable.notify_observer(ScenarioResult(
                    name=self.scenario_class_name, step=HAScenarioTestStep.Init,
                    stage=Stage.EXECUTED, status=Status.FAILED + ": Cannot find scenario class."
                ))
                return False

            self.observable.notify_observer(ScenarioResult(
                name=self.scenario_class_name, step=HAScenarioTestStep.Init,
                stage=Stage.EXECUTED, status=Status.SUCCEEDED
            ))

            try:
                scenario_result = scenario.execute(
                    observable=self.observable,
                    step_observable=self.step_observable,
                    is_clean_up=False)
                self.is_ha_executed = True
                LOG.info("HATest: Scenario runs 1 time")

                if scenario_result != Status.SUCCEEDED:
                    self.observable.notify_observer(ScenarioResult(
                        name=self.scenario_class_name, step=HAScenarioTestStep.RunOnce,
                        stage=Stage.EXECUTED, status=Status.FAILED
                    ))
                    return False

                if self.times is not None:
                    if self.times > 0:
                        self.times -= 1
                    else:
                        self.observable.notify_observer(ScenarioResult(
                            name=self.scenario_class_name, step=HAScenarioTestStep.RunOnce,
                            stage=Stage.EXECUTED, status=Status.SUCCEEDED
                        ))
                        return True
            except:
                self.observable.notify_observer(ScenarioResult(
                    name=self.scenario_class_name, step=HAScenarioTestStep.RunOnce,
                    stage=Stage.EXECUTED, status=Status.FAILED
                ))
                return False

        self.observable.notify_observer(ScenarioResult(
            name=self.scenario_class_name, step=HAScenarioTestStep.RunOnce,
            stage=Stage.FINISHED, status=Status.SUCCEEDED
        ))
        return True

    def set_ha_scenario_stop(self):
        """
        Stop the scenario running loop
        :return:
        """
        self.observable.notify_observer(ScenarioResult(
            name=self.scenario_class_name, step=HAScenarioTestStep.Stop,
            stage=Stage.EXECUTING, status=Status.SUCCEEDED
        ))
        self.is_ha_run = False

    def set_ha_scenario_start(self):
        """
        Start the scenario running loop
        :return:
        """
        self.observable.notify_observer(ScenarioResult(
            name=self.scenario_class_name, step=HAScenarioTestStep.Start,
            stage=Stage.EXECUTING, status=Status.SUCCEEDED
        ))
        self.is_ha_run = True

    def get_executed_status(self):
        """
        Get the status of whether the scenario has been run at least one time
        :return:
        """
        self.observable.notify_observer(ScenarioResult(
            name=self.scenario_class_name, step=HAScenarioTestStep.GetStatus,
            stage=Stage.EXECUTING, status=str(self.is_ha_executed)
        ))
        return self.is_ha_executed

    def set_unexecuted_status(self):
        """
        Reset the status of scenario running times
        :return:
        """

        self.is_ha_executed = False

    def set_times(self, times):
        self.observable.notify_observer(ScenarioResult(
            name=self.scenario_class_name, step=HAScenarioTestStep.Init,
            stage=Stage.EXECUTING, status=Status.SUCCEEDED + ": run " + str(times) + " times."
        ))
        self.times = times

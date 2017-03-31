import re
import shlex
import subprocess
import logging.config
from time import sleep

from sedna.common import Service
from sedna.common import Result
from sedna.ha.ha import HAScenarioMap

from sedna.scenario.scenario import Status

LOG = logging.getLogger("")


class ServiceKiller(object):
    """
    Service Killer
    """
    def kill_services(self, services):
        """
        This class kills a group of services on a node
        :param services:
        :return:
        """
        service_results = []
        LOG.debug(
            "ServiceKiller: killer has been called by server for services.")

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
            LOG.info("service:%s   status:%s   analysis:%s" %
                     (result.service.name, result.status,
                      result.analysis))
            if result.status == "failed":
                failed_count += 1
            if result.status == "successful":
                passed_count += 1
        LOG.debug(
            "ServiceKiller: %s services was killed by the server. "
            "%s services failed to be killed",
            str(passed_count), str(failed_count))

    def execute(self, service_name):
        """
        This function kill a service by name and node ip
        :param service_name:
        :param node_ip:
        :return:
        """
        if re.findall(r"openstack", service_name):
            service_name =\
                re.findall(r"openstack-(.+).service", service_name)[0]
        elif re.findall(r"service", service_name):
            service_name = re.findall(r"(.+).service", service_name)[0]

        service_pid = ""

        # Kill strategy:
        # Find a process (ppid=1), a child of root process (pid=1)
        # ps -eo pid,ppid,command --sort ppid|grep nova-api
        try:
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
                status = "successful"
                analysis = "no process"
                return [status, analysis]

            ppid_pid_lists_strs = str(ppid_pid_lists_str).split(",")
            for ppid_pid in ppid_pid_lists_strs:
                ppid_pid = ppid_pid.strip()
                pid = re.findall(r"\d+", ppid_pid.split(" ")[1])[0]
                ppid = re.findall(r"\d+", ppid_pid.split(" ")[0])[0]

                if (ppid == "1") and (pid != "1"):
                    service_pid = pid
                    break

            if service_pid == "":
                LOG.debug("service: %s, status: %s" %
                          (service_name, "no process to be killed"))
                status = "successful"
                analysis = "no process to be killed"
                return [status, analysis]

            LOG.debug(
                "ServiceKiller: pid %s will be killed.", service_pid)
            kill_output = subprocess.Popen(["kill", "-9", service_pid],
                                           stdout=subprocess.PIPE)
        except:
            LOG.error("service: %s, status: %s" %
                      (service_name, "failed to be killed"))
            status = "failed"
            analysis = "none"
            return [status, analysis]

        # wait for the killing process
        sleep(3)

        # check whether the process is killed
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

        if len(check_pid) < 1:
            status = "successful"
            analysis = "none"
            return [status, analysis]
        else:
            status = "failed"
            analysis = "cannot kill the service"
            LOG.error("service: %s, status: %s" % (service_name, "inactive"))
            return [status, analysis]


class ServiceCommand(object):
    """
    The class runs commands by "systemctl".
    The commands includes "start", "restart", "stop".
    """
    def __init__(self):
        self.command = None

    def execute(self, service_name, s_command):
        """
        This function runs the systemctl command
        :param service_name: service name
        :param s_command: service command: systmctl start, restart or stop
        :return:
        """
        self.command = shlex.split(s_command)
        self.command.append(service_name)

        try:
            output = subprocess.Popen(self.command, stdout=subprocess.PIPE)
        except:
            LOG.error("service: %s, status: %s"
                      % (service_name, "systemctl command failed"))
            status = "systemctl command failed"
            analysis = "none"
            return [status, analysis]

        result = output.stdout.readlines()

        if len(result) != 0:
            status = "failed"
            analysis = "info:" + str(result)
            LOG.error("service: %s, status: %s" %
                      (service_name, "failed"))
            return [status, analysis]

        status = "successful"
        analysis = "none"
        return [status, analysis]


class NodeHATest(object):
    """
    The tester for HA
    """

    def __init__(self):
        """
        is_ha_run: whether to continue the scenario test
        is_ha_executed: whether the scenario has been run >= one time
        """
        self.is_ha_run = False
        self.is_ha_executed = False
        self.times = None

    def run_ha_scenario(self, scenario_class=None, times=None):
        """
        This function runs ha scenario by given parameters
        :param scenario_class: the class for the scenario
        :param times: the times to run the scenario (default infinite)
        :return: 0 - exit safely; -1 - exit with errors
        """
        # Instantiation
        try:
            # scenario = eval(scenario_class + "()")
            scenario = HAScenarioMap.HA_SCENARIO_MAP[scenario_class]
            LOG.info("HATest: Scenario class: %s", scenario)
        except:
            LOG.error("HATest: Cannot find scenario class: %s", scenario_class)
            return -1

        if times is not None:
            self.times = int(times)

        while self.is_ha_run:
            try:
                scenario_result = scenario.execute()
                self.is_ha_executed = True
                LOG.info("HATest: Scenario runs 1 time")

                if scenario_result != Status.SUCCEEDED:
                    return -1

                if self.times is not None:
                    if self.times > 0:
                        self.times -= 1
                    else:
                        return 0
            except:
                LOG.error("HATest: Scenario failed")
                return -1

        LOG.info("HATest: Scenario is stopped")
        return 0

    def set_ha_scenario_stop(self):
        """
        Stop the scenario running loop
        :return:
        """
        LOG.info("HATest: Stop Scenario")
        self.is_ha_run = False

    def set_ha_scenario_start(self):
        """
        Start the scenario running loop
        :return:
        """
        LOG.info("HATest: Start Scenario")
        self.is_ha_run = True

    def get_executed_status(self):
        """
        Get the status of whether the scenario has been run at least one time
        :return:
        """
        return self.is_ha_executed

    def set_unexecuted_status(self):
        """
        Reset the status of scenario running times
        :return:
        """
        self.is_ha_executed = False

    def set_times(self, times):
        self.times = times

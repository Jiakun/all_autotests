"""base class of service status checker"""
import re
import shlex
import string
import subprocess
import logging.config

from sedna.common import Result


LOG = logging.getLogger("")


class NodeSampler(object):
    """
    The sampler to check the running status of given services on the node where
    the sampler is running.
    """
    def __init__(self):
        self._sedna_service_map = {}

    def register_service(self, name, klass):
        self._sedna_service_map[name] = klass

        LOG.debug(
            "Register Checker: {Check method: %s , Checker registered: %s}"
            % (name, klass))

    def sample(self, services):
        """
        The entrance to start the logic to run sedna service including:
            check the status of the given services on the current node
            kill a service by name
            restart a service by name

        :param services: the list of services Object to run sedna service
        :return: the verification results which is a list of Result Object
        """
        results = []
        LOG.debug(
            "NodeSampler:sample has been called by sampler server.")

        for service in services:
            #
            sedna_service_class = self._sedna_service_map[service.methods]
            LOG.debug(
                "service.name:%s service.method: %s service.checker:%s" %
                (service.name, service.methods, sedna_service_class))
            if sedna_service_class:
                checker = sedna_service_class()
                service_result = checker.execute(service=service)
                service_result =\
                    Result(service=service,
                           status=service_result[0],
                           analysis=service_result[1])
                results.append(service_result)
            else:
                LOG.error("The '%s' checker used to check '%s' "
                          "cannot be find in sampler node." %
                          (service.methods, service.name))
                raise Exception(
                    "The '%s' checker used to check '%s' "
                    "cannot be find in sampler node." %
                    (service.methods, service.name))
        LOG.debug("NodeSampler return :%s" % results)

        self._formated_output(results)

        return results

    @staticmethod
    def _formated_output(results):
        for result in results:
            LOG.info("service:%s   status:%s   checker:%s  analysis:%s" %
                     (result.service.name, result.status,
                      result.service.methods, result.analysis))


class SystemdChecker(object):
    """
    The class to check the status of service charged by systemd
    using its name given by NodeSampler.
    The status sample including "active", "inactive", "unknown".
    """
    def execute(self, service):
        command = shlex.split("systemctl is-active ")
        command.append(service.name)
        try:
            output = subprocess.Popen(command, stdout=subprocess.PIPE)
        except:
            LOG.error("service: %s, status: %s" % (service.name, "no checker"))
            status = "no checker"
            analysis = "none"
            return [status, analysis]
        str_status = str(output.stdout.readlines())
        if "active" in str_status:
            status = "active"
            analysis = "none"
            if "inactive" in str_status:
                status = "inactive"
                analysis = "need to analyse"
                LOG.error("service: %s, status: %s" %
                          (service.name, "inactive"))
            return [status, analysis]
        elif 'unknown' in str_status:
            status = "unknown"
            analysis = "none"
            LOG.error("service: %s, status: %s" % (service.name, "unknown"))
            return [status, analysis]


class PacemakerChecker(object):
    """
    The class to check the status of service charged by pacemaker
    using its name given by NodeSampler and at the present, counting
    the number of its all relevent process is to check its status.
    "active" is the symbol of the number of its process > 1;
    "inactive" is the symbol of the number of its process <= 1;
    The status sample including "active", "inactive".
    """
    def execute(self, service):
        ip_receive = service.ip
        ip = ip_receive.split('.')
        try:
            output = subprocess.check_output(
                'crm_resource --list | grep Started', shell=True)
        except:
            LOG.error("service: %s, status: %s" % (service.name, "no checker"))
            status = "no checker"
            analysis = "none"
            return [status, analysis]
        result_started = re.findall(r"\[(.+)\]", output)
        result = result_started[0].strip().split(' ')
        ip_final = []
        for each_ip in result:
            ip_final.append(re.findall('\d+', each_ip)[0])

        if ip[3] in ip_final:
            status = "active"
            analysis = "none"
            return [status, analysis]
        else:
            status = "inactive"
            analysis = "need to analyse"
            LOG.error("service: %s, status: %s" % (service.name, "inactive"))
            return [status, analysis]


class InitdChecker(object):
    def execute(self, service):
        LOG.error("The 'init.d' checker of service named %s "
                  "doesn't have been Implemented"
                  % service.name)
        raise NotImplementedError(
            "The 'init.d' checker of service named %s "
            "doesn't have been Implemented"
            % service.name)

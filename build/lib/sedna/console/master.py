import logging.config
import os
import argparse
import textwrap

from sedna.config import SednaConfigParser
from sedna.master import Master

LOG = logging.getLogger("")


class FormatedResult(object):
    """
    Display error in the stdout and log file.
    Display info in the log file.
    """
    def format_output_log(self, node_results):
        print "+", "-".center(120, '-'), "+"
        print "", "node".center(20), "group".center(10),\
            "service".center(40), "status".center(10),\
            "analysis".center(31), "".rjust(5)
        for node_result in node_results:
            for result in node_result.result:
                if result.status == "inactive":
                    LOG.error(
                        "[ip:%s, group:%s][service[name:%s, ip:%s, method:%s],"
                        "status:%s, analysis:%s]]" %
                        (node_result.ip, node_result.group,
                         result.service.name, result.service.ip,
                         result.service.methods,
                         result.status, result.analysis))
                elif result.status == "active":
                    LOG.debug(
                        "[ip:%s, group:%s]"
                        "[service[name:%s, ip:%s, method:%s], "
                        "status:%s, analysis:%s]]" %
                        (node_result.ip, node_result.group,
                         result.service.name, result.service.ip,
                         result.service.methods,
                         result.status, result.analysis))
                else:
                    LOG.warning(
                        "[ip:%s, group:%s][service[name:%s, ip:%s, method:%s],"
                        " status:%s, analysis:%s]]" %
                        (node_result.ip, node_result.group,
                         result.service.name, result.service.ip,
                         result.service.methods,
                         result.status, result.analysis))

                print "", node_result.ip.center(20),\
                    node_result.group.center(10),\
                    result.service.name.center(30),\
                    result.status.center(20), \
                    result.analysis.center(30), "".rjust(5)
        print "+", "-".center(120, '-'), "+"


def main(config_paser_class=SednaConfigParser,
         master_class=Master,
         format_output_class=FormatedResult):
    parser = \
        argparse.ArgumentParser(
            prog='parser',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent('''
    **************************************************************
                        Sedna Master
                 -----------------------
    You can choose make sedna configuration as user-defined path.
    **************************************************************
                                     ''')
                                     )
    parser.add_argument('--config_path', type=str,
                        help='the path to description the'
                             ' path of sedna.config')
    parser.add_argument('--log_config_path', type=str,
                        help='the path to description the'
                             ' path of logging.config')

    args = parser.parse_args()

    log_config_path = args.log_config_path
    if log_config_path is None:
        log_config_path = os.environ["SEDNA_LOG_CONF"]

    if not log_config_path:
        raise Exception("No log config file path is given neither in "
                        "command line nor environment arguements")
    logging.config.fileConfig(log_config_path)

    config_path = args.config_path
    if config_path is None:
        config_path = os.environ["SEDNA_CONF"]

    if not config_path:
        raise Exception("No config file path is given neither in command"
                        " line nor environment arguements")
    conf = config_paser_class(config_path)

    sedna_config_value = conf.get_sedna_config()
    master = master_class()
    results = master.verify_nodes(sedna_config_value=sedna_config_value)
    formated_result = format_output_class()
    formated_result.format_output_log(results)


if __name__ == "__main__":
    main()

import logging.config
import argparse
import textwrap

from sedna.config import SednaConfigParser
from sedna.sampler import NodeSampler
from sedna.sampler import SystemdChecker
from sedna.sampler import PacemakerChecker
from sedna.sampler import InitdChecker
from sedna.server import NodeServer

from sedna.config import SEDNA_CONF
from sedna.config import SEDNA_LOG_CONF


LOG = logging.getLogger("")


def sampler_console():
    parser = \
        argparse.ArgumentParser(
            prog='parser',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent('''\
    **************************************************************
                         Sedna Sampler
                   ------------------------
    You can choose make sedna configuration as user-defined path.
    But default config path is /etc/sedna.
    **************************************************************
    ''')
        )
    parser.add_argument('--config_path', type=str,
                        help='the string of path to description'
                             'the path of sedna.config')
    parser.add_argument('--log_config_path', type=str,
                        help='the string of path to description'
                             'the path of logging.config')

    args = parser.parse_args()

    return args


def main(config_paser_class=SednaConfigParser,
         node_server=NodeServer):
    args = sampler_console()

    log_config_path = args.log_config_path
    if log_config_path is None:
        log_config_path = SEDNA_LOG_CONF

    if not log_config_path:
        raise Exception("No log config file path is given either in "
                        "command line or environment arguements")
    logging.config.fileConfig(log_config_path)

    config_path = args.config_path
    if config_path is None:
        config_path = SEDNA_CONF

    if not config_path:
        raise Exception("No config file path is given either in command"
                        " line or environment arguements")
    conf = config_paser_class(config_path)

    node_sampler = NodeSampler()
    node_sampler.register_service("systemd", SystemdChecker)
    node_sampler.register_service("pacemaker", PacemakerChecker)
    node_sampler.register_service("init.d", InitdChecker)
    server = node_server(port=int(conf.port), sampler=node_sampler)
    server.start()


if __name__ == "__main__":
    main()

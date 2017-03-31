import logging.config

from sedna.config import SednaConfigParser
from sedna.sampler import NodeSampler
from sedna.sampler import SystemdChecker
from sedna.sampler import PacemakerChecker
from sedna.sampler import InitdChecker
from sedna.server import NodeServer

from sedna.config import SEDNA_CONF
from sedna.config import SEDNA_LOG_CONF


LOG = logging.getLogger("")


def main(config_paser_class=SednaConfigParser,
         node_server=NodeServer):
    logging.config.fileConfig(SEDNA_LOG_CONF)

    conf = config_paser_class(SEDNA_CONF)

    node_sampler = NodeSampler()
    node_sampler.register_service("systemd", SystemdChecker)
    node_sampler.register_service("pacemaker", PacemakerChecker)
    node_sampler.register_service("init.d", InitdChecker)
    server = node_server(port=int(conf.port), sampler=node_sampler)
    server.start()

if __name__ == "__main__":
    main()

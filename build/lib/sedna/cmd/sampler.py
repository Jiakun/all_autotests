import logging.config
import os
import argparse
import textwrap

from sedna.config import SednaConfigParser
from sedna.sampler import NodeSampler
from sedna.sampler import SystemdChecker
from sedna.sampler import PacemakerChecker
from sedna.sampler import InitdChecker
from sedna.server import NodeServer


LOG = logging.getLogger("")

SEDNA_CONF = os.environ["SEDNA_CONF"] if \
    os.environ.get("SEDNA_CONF", None) else "/etc/sedna/sedna.conf"
SEDNA_LOG_CONF = os.environ["SEDNA_LOG_CONF"] if \
    os.environ.get("SEDNA_LOG_CONF", None) else "/etc/sedna/logging.conf"


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

"""Demo for Pyro4 rpc communication """
import Pyro4
from threading import Thread
from unittest2 import TestCase
import time

"""
change configuration to support dill serialization, which should support
complex object serialization and deserialization
"""
Pyro4.config.SERIALIZERS_ACCEPTED = ['dill']
Pyro4.config.SERIALIZER = 'dill'


class Pyro4DemoTest(TestCase):
    """Test case to demo rpc communication """

    def test(self):
        def start_server():
            # start Pyro4 server
            Pyro4.Daemon.serveSimple(
                {Team: "my.Team"}, host="localhost",
                ns=False, port=10086
            )

        server_thread = Thread(target=start_server)
        server_thread.setDaemon(True)
        server_thread.start()
        # waiting for the server be ready for serve
        time.sleep(5)

        proxy = Pyro4.Proxy("PYRO:my.Team@localhost:10086")
        member = Member()
        member.name = "sam"
        proxy.add_member(member)


class Member(object):
    """ common object as parameter for serialization """
    def __init__(self):
        self.name = None


@Pyro4.expose
class Team(object):
    """PRC server"""
    def __init__(self):
        self.members = []

    def add_member(self, member):
        print "add member : %s" % member
        self.members.append(member)

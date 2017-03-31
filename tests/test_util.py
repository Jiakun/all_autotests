"""Test cases for utilities """
from unittest2 import TestCase

from sedna import util


class GenerateUUIDTest(TestCase):
    """test case for uuid generating """

    def test(self):
        uuid = util.generate_uuid_str()
        self.assertRegexpMatches(
            uuid,
            "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{8}")

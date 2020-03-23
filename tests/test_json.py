from __future__ import absolute_import, division, unicode_literals
import datetime
import unittest

import jsonrpc

try:
    ustr = unicode
except NameError:  # Python3
    ustr = str


class TestJSON(unittest.TestCase):
    def test_datetime_objects(self):
        """Test that we serialize datetime objects without raising"""
        now = datetime.datetime.now()

        obj = {'time': now}
        value = jsonrpc.dumps(obj)
        self.assertTrue(value)

    def test_datetime_objects_roundtrip(self):
        """Test that we can serialize and un-serialize datetimes

        datetime objects are converted to strings when serializing,
        but we do not convert back to datetime.

        """
        now = datetime.datetime.now()

        obj = {'time': now}
        value = jsonrpc.dumps(obj)
        unserialized = jsonrpc.loads(value)

        self.assertTrue(isinstance(unserialized['time'], ustr))
        self.assertEqual(unserialized['time'], now.isoformat())

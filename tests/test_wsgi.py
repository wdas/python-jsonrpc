from __future__ import absolute_import, division, unicode_literals
from io import BytesIO
import string
import unittest

from jsonrpc.compat import encode
from jsonrpc.wsgi import WsgiContentReader


class MockFileObject(BytesIO):
    def __init__(self, string):
        BytesIO.__init__(self, string)
        self.read_call_args = []

    def read(self, size):
        self.read_call_args.append(size)
        return BytesIO.read(self, size)


class WsgiContentReaderTestCase(unittest.TestCase):
    def test_constructor(self):
        reader = WsgiContentReader('file', 'length')
        self.assertTrue(isinstance(reader, WsgiContentReader))

    def test_data_is_read_in_expected_chunk_sizes(self):
        content_length = len(string.ascii_lowercase)
        file_object = MockFileObject(encode(string.ascii_lowercase))
        reader = WsgiContentReader(file_object, content_length, chunk_size=4)
        got = reader.read_data()
        self.assertEqual(encode(string.ascii_lowercase), got)
        self.assertEqual([4, 4, 4, 4, 4, 4, 2], file_object.read_call_args)

    def test_chunk_size_reduced_if_content_length_smaller_than_chunk(self):
        content_length = len(string.ascii_lowercase)
        file_object = MockFileObject(encode(string.ascii_lowercase))
        reader = WsgiContentReader(file_object, content_length, chunk_size=50)
        got = reader.read_data()
        self.assertEqual(encode(string.ascii_lowercase), got)
        self.assertEqual([26], file_object.read_call_args)

    def test_get_empty_string_if_content_length_is_zero(self):
        file_object = MockFileObject(b'')
        reader = WsgiContentReader(file_object, 0, chunk_size=50)
        actual = reader.read_data()
        assert b'' == actual

#!/usr/bin/env python

import unittest
import os

from jsonrpc import _tests

if __name__ == '__main__':
    testdir = os.path.dirname(_tests.__file__)
    modules = []
    for filename in os.listdir(testdir):
        if filename[-3:] == '.py' and filename != '__init__.py':
            modules.append('jsonrpc._tests.%s' % filename[:-3])

    suite = unittest.TestLoader().loadTestsFromNames(modules)
    unittest.TextTestRunner(verbosity=5).run(suite)

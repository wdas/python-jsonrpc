#!/usr/bin/env python

import unittest
import os


from jsonrpc import _tests

if __name__ == "__main__":

    testPath = os.path.split(_tests.__file__)[0]
    testModules = []
    for fileName in os.listdir(testPath):
        if fileName[-3:] == '.py' and fileName != '__init__.py':
            testModules.append('jsonrpc._tests.%s' % fileName[:-3])

    suite = unittest.TestLoader().loadTestsFromNames(testModules)

    unittest.TextTestRunner(verbosity=5).run(suite)
    

#!/usr/bin/env python

import unittest
import os
from glob import glob

import tests

if __name__ == '__main__':
    testdir = os.path.dirname(tests.__file__)
    modules = []
    for filename in glob(os.path.join(testdir, '*.py')):
        modules.append('tests.%s' % os.path.basename(filename)[:-3])

    suite = unittest.TestLoader().loadTestsFromNames(modules)
    unittest.TextTestRunner(verbosity=5).run(suite)

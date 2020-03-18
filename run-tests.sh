#!/bin/sh
num_procs=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
tox --parallel "$num_procs" --develop --skip-missing-interpreters -e python,py27,py34,py35,py36,py37,py38 "$@"

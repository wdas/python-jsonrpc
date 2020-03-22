#!/bin/sh
num_procs=$(
	nproc 2>/dev/null ||
	sysctl -n hw.ncpu 2>/dev/null ||
	echo 4
)

tox \
	--parallel "$num_procs" \
	--skip-missing-interpreters \
	-e 'python,py{27,36,37,38}' "$@"

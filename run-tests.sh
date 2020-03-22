#!/bin/sh
num_procs=$(
	nproc 2>/dev/null ||
	sysctl -n hw.ncpu 2>/dev/null ||
	echo 4
)

tox \
	--parallel "$num_procs" \
	--skip-missing-interpreters \
	-e python,py27,py36,py37,py38 "$@"

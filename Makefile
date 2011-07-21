#!/usr/bin/env make

PYTHON ?= python

prefix ?= $(shell pf-makevar --absolute root)
ifeq ($(mac_pkg),1)
    mac_flags=--mac-pkg
endif
pfmakevar ?= pf-makevar --root=$(prefix) --absolute $(mac_flags)
pylibs ?= $(DESTDIR)$(shell $(pfmakevar) python-site)
rsync ?= rsync -r --delete --exclude=_tests --exclude='*.swp' --exclude='*~'
nose_args=--no-path-adjustment --with-doctest
test_flags=
release_flags=

-include config.mak
# test flags can be specified on the command line for passing
# extra arguments to nose.  You can also add a 'config.mak'
# in this same directory to redefine these variables as needed.

all: install

makevars:
	@(test -n "$(prefix)" && \
	  test -n "$(pylibs)") || \
	(echo "error: undefined build variables: is pathfinder installed?"; \
	 false)

libs: makevars
	mkdir -p $(pylibs)
	$(rsync) jsonrpc/ $(pylibs)/jsonrpc/
	find $(pylibs)/ -name '*.py' | xargs $(PYTHON) -m py_compile

install: libs

pkg:
	git make-pkg

rpm:
	git make-rpm

clean: makevars
	rm -rf $(pylibs)/jsonrpc
	rmdir -p $(DESTDIR)$(pylibs) 2>/dev/null || true
	find . -name '*.py[co]' -print0 | xargs -0 rm -f

test:
	@env PYTHONPATH="$(CURDIR)":"$(PYTHONPATH)" \
	./run-tests.py

.PHONY: test install clean makevars
.PHONY: rpm
.PHONY: pkg

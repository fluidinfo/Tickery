.PHONY: all, debug, check, clobber

all:
	$(MAKE) -C www $@
	$(MAKE) -C admin $@

debug:
	$(MAKE) -C www $@
	$(MAKE) -C admin $@

clobber:
	$(MAKE) -C www $@
	$(MAKE) -C admin $@

check:
	pyflakes *.py www/*.py admin/*.py

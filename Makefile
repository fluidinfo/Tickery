.PHONY: all, clobber, wc, dist

all:
	$(MAKE) -C tickery/www $@
	$(MAKE) -C tickery/admin $@

clobber:
	rm -fr tickery/test/_trial_temp MANIFEST dist
	find . -name '*~' -o -name '*.pyc' -print0 | xargs -0 -r rm
	$(MAKE) -C tickery/www $@
	$(MAKE) -C tickery/admin $@
	$(MAKE) -C doc $@

wc:
	find . -name '*.py' -print0 | xargs -0 wc -l

dist:
	rm -f MANIFEST
	python setup.py sdist

.PHONY: all debug install-pyjamas deploy run clean wc pep8 pyflakes lint

all:
	cd tickery/www && ../../pyjamas/bin/pyjsbuild index.py
	cd tickery/admin && ../../pyjamas/bin/pyjsbuild index.py

debug:
	cd tickery/www && ../../pyjamas/bin/pyjsbuild --strict --print-statements --debug --debug-wrap -o output index.py
	cd tickery/admin && ../../pyjamas/bin/pyjsbuild --strict --print-statements --debug --debug-wrap -o output index.py

install-pyjamas:
	curl -L http://sourceforge.net/projects/pyjamas/files/pyjamas/0.7/pyjamas-0.7.tgz > pyjamas.tgz
	tar xfv pyjamas.tgz
	rm -f pyjamas
	ln -s pyjamas-0.7 pyjamas
	cd pyjamas && python bootstrap.py
	rm pyjamas.tgz

deploy: all
	fab live deploy

run:
	cd tickery && twistd -n tickery

clean:
	rm -fr tickery/test/_trial_temp MANIFEST dist parsetab.py
	find . -name '*~' -o -name '*.pyc' -print0 | xargs -0 -r rm
	rm -fr tickery/www/output tickery/www/*.js
	rm -fr tickery/admin/output tickery/admin/*.js
	$(MAKE) -C doc $@

wc:
	find tickery -name '*.py' -print0 | xargs -0 wc -l

pep8:
	find tickery -name '*.py' -print0 | xargs -0 -n 1 pep8 --repeat

pyflakes:
	find tickery -name '*.py' -print0 | xargs -0 pyflakes

lint: pep8 pyflakes

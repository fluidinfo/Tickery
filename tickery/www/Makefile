.PHONY: all, debug, index, check, clobber

all: index

index:
	pyjsbuild -O index.py

debug:
	pyjsbuild -d --strict --print-statements index.py

check:
	pyflakes *.py

clobber:
	rm -fr output


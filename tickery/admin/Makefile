.PHONY: all, debug, index, check, clobber

all: index

debug: index-debug

index:
	pyjsbuild -O index.py

index-debug:
	pyjsbuild -d --strict --print-statements index.py

check:
	pyflakes *.py

clobber:
	rm -fr output

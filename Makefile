.PHONY: all install uninstall dist clean check refresh test setver

# Installation locations
PREFIX=/usr/local
MANDIR=$(PREFIX)/man
BINDIR=$(PREFIX)/bin

# Leave these two as they are.
SUBDIR=doc
VER=2.0.0
DISTFILES=README.rst

# Default target.
all: lamprop ${SUBDIR}

lamprop: src/__main__.py src/lamprop/*.py
	cd src; zip -q ../foo.zip __main__.py lamprop/*.py
	echo '#!/usr/bin/env python3' >lamprop
	cat foo.zip >>lamprop
	chmod a+x lamprop
	rm -f foo.zip

${SUBDIR}::
	cd ${.TARGET}; make ${.TARGETS}

# Install lamprop and its documentation.
install: lamprop
# Install the zipped script.
	install -d ${BINDIR}
	install lamprop ${BINDIR}
# Install the manual page.
	gzip -c doc/lamprop.1 >lamprop.1.gz
	gzip -c doc/lamprop.5 >lamprop.5.gz
	install -d $(MANDIR)/man1
	install -d $(MANDIR)/man5
	install -m 644 lamprop.1.gz $(MANDIR)/man1
	install -m 644 lamprop.5.gz $(MANDIR)/man5
	rm -f lamprop.1.gz lamprop.5.gz

# Remove an installed lamprop completely
uninstall::
	rm -f ${BINDIR}/lamprop $(MANDIR)/man1/lamprop.1* \
	$(MANDIR)/man5/lamprop.5*

clean: ${SUBDIR}
	rm -rf lamprop dist backup-*.tar*
	find . -type f -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete

# EOF.
# The specifications below are for the maintainer only.
CUTLINE!=grep -n '\#[^E]*EOF' Makefile | cut -d ':' -f 1

dist: ${SUBDIR} lamprop
	rm -rf dist
	mkdir -p dist/lamprop-${VER}/src/lamprop
	ln lamprop dist/lamprop-${VER}
	for f in ${DISTFILES}; do \
		ln $$f dist/lamprop-${VER}/$${f} ; \
	done
	head -n ${CUTLINE} Makefile >dist/lamprop-${VER}/Makefile
	for f in $$(find src/ -type f -name '*.py'); do \
		ln $$f dist/lamprop-${VER}/$${f} ; \
	done
	mkdir -p dist/lamprop-${VER}/doc
	for f in $$(ls doc/lamprop.*); do \
		ln $$f dist/lamprop-${VER}/$${f} ; \
	done
	mkdir -p dist/lamprop-${VER}/test
	ln test/hyer.lam dist/lamprop-${VER}/test/hyer.lam
	cd dist; zip -r lamprop-${VER}.zip lamprop-${VER}
	rm -rf dist/lamprop-${VER}

check:: .IGNORE
	pep8-3.4 src/__main__.py src/lamprop/*.py test/test*.py

refresh::
	.git/hooks/post-commit

tests::
	cd test; nosetests-3.4 -v

setver::
	sed -i '' -e "s/^__version__.*/__version__ = '${VER}'/" `find . -type f -name "*.py"`

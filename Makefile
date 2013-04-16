TEST_RUNNER=./tests.py
COVERAGE=coverage.py
SOURCE_FILES=html2markdown.py
DIRECTORY_NAME=html2markdown

all:	test

test:
	make -C tests
	$(TEST_RUNNER)

coverage:	.coverage
	$(COVERAGE) -r -m $(SOURCE_FILES)

annotate:	.coverage
	$(COVERAGE) -a $(SOURCE_FILES)

clean-coverage:
	$(COVERAGE) -e

clean:	clean-coverage
	make -C tests clean
	rm -f .coverage *,cover *.pyc *.tar.gz

.coverage:	$(SOURCE_FILES)
	make -C tests
	-$(COVERAGE) -x $(TEST_RUNNER)

DIST_DIRECTORY_NAME = $(DIRECTORY_NAME)-$(VERSION)
DIST_ARCHIVE = $(DIST_DIRECTORY_NAME).tar.gz
dist:	clean
	if [ "x$(VERSION)" = "x" ]; then \
		echo "Set VERSION!  make VERSION=99.9 dist" >&2; \
		exit 1; \
	fi
	mkdir $(DIST_DIRECTORY_NAME)
	mtn list known | cpio -pdm $(DIST_DIRECTORY_NAME)
	chmod -R a+rX $(DIST_DIRECTORY_NAME)
	chmod -R o-w $(DIST_DIRECTORY_NAME)
	tar -zcvf $(DIST_ARCHIVE) $(DIST_DIRECTORY_NAME)
	rm -rf $(DIST_DIRECTORY_NAME)
	chmod 644 $(DIST_ARCHIVE)
	ls -al $(DIST_ARCHIVE)

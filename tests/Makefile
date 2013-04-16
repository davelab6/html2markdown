GENTEST=../gentest.py

TEST_FILES = $(patsubst %.source,%.test,$(wildcard *.source))

all:	tests

tests:	$(TEST_FILES)

%.test:	%.source
	$(GENTEST) $<

clean:
	rm -f *.test

#!/usr/bin/python

from unittest import TestCase, main
from html2markdown import html2markdown, WRAP_AT_COLUMN
import html2markdown as h2m
import logging
import sys
import os
import os.path as path
import new
from StringIO import StringIO
import textwrap

TESTS_DIRECTORY = "tests"

log = logging.getLogger("HTML2MarkdownTests")

def assertRendering(test, box, expectedRendering):
    rendering = StringIO()
    box.render(rendering.write)
    test.assertEqual(rendering.getvalue(), expectedRendering)

class MockBox (h2m.Box):
    def render(self, writer, width=0):
        self.width = width

class TextBoxTests (TestCase):
    def setUp(self):
        self.__box = h2m.TextBox()

    def testRender(self):
        testString = "foo\n"
        self.__box.addText(testString)
        assertRendering(self, self.__box, testString)

    def testLineBreak(self):
        self.__box.addText("foo")
        self.__box.addLineBreak()
        self.__box.addText("bar\n")
        assertRendering(self, self.__box, "foo  \nbar\n")

    def testAlwaysEndsWithNewline(self):
        testString = "foo"
        self.__box.addText(testString)
        assertRendering(self, self.__box, testString + "\n")

class CompositeBoxTests (TestCase):
    __testStrings = "foo bar blee".split()
    __expectedBoxStrings = [ s + "\n" for s in __testStrings ]

    def __setUpTextBoxes(self, useDividers):
        self.__root = h2m.CompositeBox(useDividers)
        self.__textBoxes = []
        for string in self.__testStrings:
            self.__textBoxes.append(self.__root.makeChild(h2m.TextBox))
            self.__textBoxes[-1].addText(string)

    def testRenderWithDividers(self):
        self.__setUpTextBoxes(True)
        self.__assertRendering("\n".join(self.__expectedBoxStrings))

    def testRenderWithoutDividers(self):
        self.__setUpTextBoxes(False)
        self.__assertRendering("".join(self.__expectedBoxStrings))

    def testSelectedDivider(self):
        self.__setUpTextBoxes(False)
        self.__root.insertNewLineAfterChild(0)
        self.__assertRendering("".join([self.__expectedBoxStrings[0], "\n"]
                                       + self.__expectedBoxStrings[1:]))

    def __assertRendering(self, expectedValue):
        assertRendering(self, self.__root, expectedValue)

    def testEmptyBox(self):
        assertRendering(self, h2m.CompositeBox(), "")

class WrappedTextBoxTests (TestCase):
    __word = "foo"
    __width = 70
    __numberOfWords = (__width / len(__word)) * 2
    __text = " ".join([__word] * __numberOfWords)
    __expectedWrapping = textwrap.fill(__text, __width)

    def setUp(self):
        root = h2m.RootBox(self.__width)
        self.__box = root.makeChild(h2m.WrappedTextBox)

    def testWrapping(self):
        self.__box.addText(self.__text)
        assertRendering(self, self.__box, self.__expectedWrapping + "\n")

    def testWrappingWithLineBreak(self):
        self.__box.addText(self.__text)
        self.__box.addLineBreak()
        self.__box.addText(self.__text)
        assertRendering(self, self.__box,
                        "%(t)s  \n%(t)s\n" % {"t": self.__expectedWrapping})

class IndentedBoxTests (TestCase):
    def testBox(self):
        firstLine = "foo bar blee\n"
        subsequentLine = "eek eek eek\n"
        firstLineIndent = "* "
        subsequentLineIndent = "  "
        box = h2m.IndentedBox(firstLineIndent=firstLineIndent,
                              indent=subsequentLineIndent)
        box.makeChild(h2m.TextBox).addText(firstLine)
        box.makeChild(h2m.TextBox).addText(subsequentLine)
        expectedValue = "".join((firstLineIndent, firstLine,
                                 subsequentLineIndent, subsequentLine))
        assertRendering(self, box, expectedValue)

    # XXX factor this out, with BlockCompositeBoxTests.  Maybe into a
    # module-level function, since we might not feel it's right to
    # make a superclass for this (extending a utility class).  We
    # should probably do this test for every Box, too.
    #
    # XXX should we have setUp make an IndentingBox, a la
    # BlockCompositeBoxTests?
    def testEmptyBox(self):
        assertRendering(self, h2m.IndentedBox(indent="> "), "")

class HTML2MarkdownTests (TestCase):
    def setUp(self):
        log.debug("running %r" % (self.id(),))

    # This can't be named with __ because our generated tests would
    # then have to perform name mangling manually.  If I knew of a
    # function in the Python library that would do name mangling for
    # me, I'd probably like that.  I don't like to assume how Python
    # will be mangling the name.  Anyway, the underscore probably
    # makes it sufficiently obvious that this function is not to be
    # called by outsiders.
    def _testHTML2Markdown(self, html, expectedOutput):
        status, output = html2markdown(html)
        self.assertEqual(status, 0, "html2markdown returned non-zero status")
        self.assertEqual(output, expectedOutput)

# XXX This comment is no longer 100% accurate, perhaps.
#
# Dynamically build test cases by running some given Markdown markup
# through Markdown, then using that output as the input HTML for our
# code and the Markdown markup we read in as the expected output.
#
# Test cases are expected to be one per file in a directory called
# "tests" which is a subdirectory of the CWD.  Only files in that
# directory are examined.  Subdirectories are not recursed.

def __makeTestNameFromFileName(fileName):
    fileName, extension = path.splitext(fileName)
    testName = filter(lambda c: c.isalnum() or c == "_", fileName)
    while len(testName) > 0 \
          and not (testName[0].isalpha() or testName[0] == "_"):
        testName = testName[1:]
    assert len(testName) > 0, "can't get test name for file %r" % aFile
    return testName

# unittest will barf if the callable objects we install for test
# functions on the TestCase don't have a proper __name__ attribute.
# That's why we have to jump through some hoops to dynamically
# generate the test methods.
def __makeTest(testName, html, text):
    testName = "test%s" % (testName,)
    testLambda = lambda self: self._testHTML2Markdown(html, text)
    testFunction = new.function(testLambda.func_code, {}, testName,
                                closure=testLambda.func_closure)
    setattr(HTML2MarkdownTests, testName,
            new.instancemethod(testFunction, None, HTML2MarkdownTests))

def __readTestFile(pathToFile):
    test = open(pathToFile, "r")
    inputSize, outputSize = map(int, test.readline().split(" ", 1))
    input = test.read(inputSize)
    output = test.read(outputSize)
    return input, output

for aFile in os.listdir(TESTS_DIRECTORY):
    if aFile.endswith(".test"):
        pathToFile = path.join(TESTS_DIRECTORY, aFile)
        if path.isfile(pathToFile):
            testName = __makeTestNameFromFileName(aFile)
            input, output = __readTestFile(pathToFile)
            __makeTest(testName, input, output)

if __name__ == "__main__":
    logging.basicConfig()
    if len(sys.argv) >= 2 and sys.argv[1] == '-d':
        logging.getLogger().setLevel(logging.DEBUG)
        del sys.argv[1]
    main()

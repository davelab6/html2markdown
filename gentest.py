#!/usr/bin/python

import sys
import os
from os import path
from popen2 import Popen3
from StringIO import StringIO

MARKDOWN = os.environ.get("MARKDOWN", "Markdown.pl")

def runMarkdown(input):
    markdown = Popen3(MARKDOWN)
    markdown.tochild.write(input)
    markdown.tochild.close()
    output = markdown.fromchild.read()
    status = markdown.wait()
    assert normalExitStatus(status), "Markdown exited unusually"
    return output

def normalExitStatus(status):
    return os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0

def main():
    checkUsage()
    sourcePath, destinationPath = getSourceAndDestinationPaths()
    input, output = readTestSource(sourcePath)
    inputHTML = runMarkdown(input)
    writeTestFile(destinationPath, inputHTML, output)
    sys.exit(0)

def writeTestFile(destinationPath, inputHTML, output):
    destination = open(destinationPath, "w")
    destination.write("%d %d\n" % (len(inputHTML), len(output)))
    destination.write(inputHTML)
    destination.write(output)
    destination.close()

def getSourceAndDestinationPaths():
    sourcePath = sys.argv[1]
    destinationPath = getOutputPath(sourcePath)
    return sourcePath, destinationPath

def readTestSource(sourcePath):
    source = open(sourcePath, "r")

    separateInputOutput = readFirstLineOfTestSource(source)
    input = readTestInput(source, separateInputOutput)

    if separateInputOutput:
        output = source.read()
    else:
        output = input

    source.close()

    return input, output

def readTestOutput(separateInputOutput, source, input):
    return output

def readFirstLineOfTestSource(source):
    firstLine = source.readline()
    assert firstLine.startswith("#"), "Unknown first line in test"
    firstLine = firstLine[1:].strip().lower()
    if firstLine == "input":
        separateInputOutput = True
    else:
        separateInputOutput = False
    return separateInputOutput

def readTestInput(source, separateInputOutput):
    input = StringIO()
    while True:
        line = source.readline()
        if (not line) or (separateInputOutput
                          and line.lower().rstrip() == "#output"):
            break
        else:
            input.write(line)
    input = input.getvalue()

    if separateInputOutput:
        assert line, "Test source ended prematurely"
    else:
        assert not line, "Shouldn't get here"

    return input

def getOutputPath(sourcePath):
    directoryName, sourceFileNameAndExt = path.split(sourcePath)
    sourceFileName, sourceExt = path.splitext(sourceFileNameAndExt)
    assert sourceExt == ".source", "Unknown extension on input file"
    destinationPath = path.join(directoryName, sourceFileName + ".test")
    return destinationPath

def checkUsage():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s <test file>" % sys.argv[0])
        sys.exit(1)

if __name__ == "__main__":
    main()

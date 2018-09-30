import sys
from scorelib import Print


def load(filename):
    tempData = {}
    prints = []
    for line in open(filename, "r"):
        if line not in ['\n', '\r\n']:
            data = line.split(":")
            tempData[data[0].rstrip()] = data[1].rstrip().strip()
        else:
            prints.append(processBlock(tempData))
            tempData = {}
    prints.append(processBlock(tempData))
    return prints


def processBlock(data):
    return Print.fromData(data)


printclasses = load(sys.argv[1])

for printclass in printclasses:
    printclass.format()
    print("")
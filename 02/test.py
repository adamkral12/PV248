import sys
from scorelib import Print, Person, Composition, Voice, Edition


def load(filename):
    tempData = {}
    prints = []
    for line in open(filename, "r"):
        if line not in ['\n', '\r\n']:
            data = line.split(":")
            tempData[data[0].rstrip()] = data[1].rstrip().strip()
        else:
            if tempData:
                prints.append(Print.fromData(tempData))
                tempData = {}
    prints.append(Print.fromData(tempData))
    return prints


printclasses = load(sys.argv[1])

for printclass in printclasses:
        printclass.format()
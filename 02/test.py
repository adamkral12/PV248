import sys
import re
from scorelib import Print, Edition, Composition, Voice, Person


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


def processCompositionYear(data):
    regexp = re.compile('(.*)(\d\d\d\d)(.*)')
    match = regexp.match(data)
    return match.group(1) if match else None


def processPerson(data):
    if data:
        insideBrackets = re.search(r'(.*)\((.*?)\)', data)
        if insideBrackets:
            name = insideBrackets.group(1)
            years = insideBrackets.group(2)
            yearsSplit = re.search(r'(\d\d\d\d)(-|--)(\d\d\d\d)', years)
            if yearsSplit:
                return Person(name, yearsSplit.group(1), yearsSplit.group(3))
            else:
                yearBorn = re.search(r'(\d\d\d\d)(-|--)(.*)', years)
                if yearBorn:
                    return Person(name, yearBorn.group(1), None)
                else: # find * and +
                    yearBorn = None
                    yearDied = None
                    yearDiedReg = re.search(r'(\+)(\d\d\d\d)', years)
                    if yearDiedReg:
                        yearDied = yearDiedReg.group(2)
                    yearBornReg = re.search(r'(\*)(\d\d\d\d)', years)
                    if yearBornReg:
                        yearBorn = yearBornReg.group(2)
                    return Person(name, yearBorn, yearDied)
        else:
            return Person(data, None, None)


def processBlock(data):
    voices = []
    editors = []
    composers = []
    for key, val in data.items():
        if re.match(r"(.*)Voice(.*)", key):
            voices.append(processVoice(val))
    if "Editor" in data:
        if processPerson(data["Editor"]):
            editors.append(processPerson(data["Editor"]))
    if "Composer" in data:
        for composer in data["Composer"].split(";"):
            if processPerson(composer):
                composers.append(processPerson(composer))
    composition = Composition(
        data["Title"] if "Title" in data else None,
        data["Incipit"] if "Incipit" in data else None,
        data["Key"] if "Key" in data else None,
        data["Genre"] if "Genre" in data else None,
        processCompositionYear(data["Composition Year"]) if "Composition Year" in data else None,
        voices,
        composers
    )

    edition = Edition(
        composition,
        editors,
        data["Edition"] if "Ediiton" in data else None
    )

    return Print(
        edition,
        data["Print Number"] if "Print Number" in data else None,
        data["Partiture"] if "Partiture" in data else None
    )


def processVoice(voiceData):
    voiceRange = re.match(r"(.*)--([^,;]*)[,;](.*)", voiceData)
    if voiceRange:
        return Voice(voiceRange.group(3).strip(), voiceRange.group(1) + "--" + voiceRange.group(2))
    else:
        return Voice(voiceData, None)


printclasses = load(sys.argv[1])

for printclass in printclasses:
    printclass.format()
    print("")
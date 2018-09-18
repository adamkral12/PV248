import sys
import re
from collections import Counter

cntComposers = Counter()
cntYears = Counter()


def centuryFromYear(year):
    return str(int(year) // 100 + 1) + "th century"


def printCounter(counter):
    for key, value in counter.most_common():
        print(key + ": " + str(value))


for line in open(sys.argv[1], "r"):
    if line not in ['\n', '\r\n']:
        data = line.split(":")
        if data[0] == "Composer":
            if data[1].rstrip():
                cntComposers[data[1].rstrip()] += 1
        elif data[0] == "Composition Year":
            # find 4 digits next to each other, extract
            regexp = re.compile('(.*)(\d\d\d\d)(.*)')
            match = regexp.match(data[1])
            if match:
                cntYears[centuryFromYear(match.group(2))] += 1
            elif re.match(r"(.*)century(.*)", data[1]):  # case 17th century
                century = re.sub('[^0-9]', '', data[1])
                cntYears[century + "th century"] += 1

# print
if sys.argv[2] == 'composer':
    printCounter(cntComposers)
elif sys.argv[2] == 'year':
    printCounter(cntYears)
else:
    raise Exception("What do you want?")

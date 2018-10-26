import sys
import numpy as np
import re

input = sys.argv[1]

rightSides = []
resultVars = []
setOfVars = set()
minus = 1
for k, line in enumerate(open(sys.argv[1], "r")):
    thingies = re.split("(\+|\-|\=)", line)
    left = []
    vars = {}
    for thingy in thingies:
        koef = None
        var = None
        result = None
        thingy = thingy.strip()
        if thingy == '+' or thingy == '=':
            minus = 1
            continue
        elif thingy == '-':
            minus = -1
            continue
        match = re.match(r"(\d+)([A-z])|([A-z])|([\d+])", thingy)
        if not match:
            raise Exception("Error in matching vars or numbers")
        if match.group(1) and match.group(2): # coefficient and number
            koef = int(match.group(1))*minus
            var = match.group(2)
        elif match.group(3): # only variable - set koef to 1
            koef = minus
            var = match.group(3)
        elif match.group(4): # numbers (should be on right side)
            result = int(match.group(4))*minus
        else:
            raise Exception("Error in grouping match")

        if koef is not None and var is not None:
            vars[var] = koef
            setOfVars.add(var)
        elif result is not None:
            rightSides.append(result)
        else:
            raise Exception("Neither koef or result is set")
    resultVars.append(vars)


print("result vars ",resultVars)
print("set {}", setOfVars)
koefs = {}

for var in setOfVars:
    koefs[var] = []
    for result in resultVars:
        if var in result:
            koefs[var].append(result[var])
        else:
            koefs[var].append(0)

print("koefs {}", koefs)

finalKoefs = []
for k, finalKoef in koefs.items():
    finalKoefs.append(finalKoef)

print("final koefs {}", finalKoefs)
print("right sides", rightSides)
a = np.array(finalKoefs)
b = np.array(rightSides)
x = np.linalg.solve(a, b)
print(x)

matrix1 = np.column_stack((finalKoefs, rightSides))
koefRank = np.linalg.matrix_rank(finalKoefs)
augRank = np.linalg.matrix_rank(matrix1)
dim = len(setOfVars) - koefRank

setOfVars = list(setOfVars)
if augRank != koefRank:
    print("no solution")
else:
    if koefRank == len(setOfVars):
        printText = ""
        sol = np.linalg.solve(finalKoefs, rightSides)
        for i in range(len(setOfVars)):
            printText += " {} = {},".format(setOfVars[i], int(sol[i]) if sol[i].is_integer() else sol[i])
        print("solution:{}".format(printText[:-1]))   # remove ,
    else:
        print("solution space dimension: {}".format(dim))
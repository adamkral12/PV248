import sys
import numpy as np
import re

input = sys.argv[1]

rightSides = []
resultVars = []
setOfVars = list()
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
        if not thingy:
            continue
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
            if var not in setOfVars:
                setOfVars.append(var)
        elif result is not None:
            rightSides.append(result)
        else:
            raise Exception("Neither koef or result is set")
    resultVars.append(vars)


finalKoefs = []

for result in resultVars:
    finalKoef = []
    for var in setOfVars:
        if var in result:
            finalKoef.append(result[var])
        else:
            finalKoef.append(0)
    finalKoefs.append(finalKoef)

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
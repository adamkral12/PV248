#!/usr/bin/python3

import sys, re
import numpy as np

constants = []  # matrix of constants
coeficients = []  # matrix of int coeficients

lines = []  # list of dicts with variables and their coeficients e.g. [{"x":1,"y":1},{"y":2,"x":3}]
variables = set()  # set of all used variables

for line in open(sys.argv[1], "r"):
    left, right = line.strip().split("=")  # left side coeficients and variables, right side constants
    constants.append(int(right.strip()))
    left.strip()
    positive = True  # if the number should be positive or negative, first number is always positive
    number = ""
    line_variables = {}  # variables and their coeficients e. g. {"x":12,"y":3}
    for char in left:
        if char == "+":
            positive = True
        elif char == "-":
            positive = False
        elif ord(char) >= 97 and ord(char) <= 122:  # its variable
            variables.add(char)
            if number == "":  # coeficient is 1 if there is none near variable
                number = "1"
            if not positive:  # create negative number
                number = "-" + number

            line_variables[char] = int(number)
            number = ""
        elif ord(char) >= 48 and ord(char) <= 57:
            number += char  # crate number by concatinating chars
        else:  # spaces, other garbage
            continue
    lines.append(line_variables)

variables = list(variables)  # convert to list so i can sort
variables.sort()

# create coeficients matrix
for line in lines:
    coeficient_line = []
    for var in variables:
        if var in line:
            coeficient_line.append(line[var])
        else:
            coeficient_line.append(0)
    coeficients.append(coeficient_line)

# math stuff
augmented_matrix = np.column_stack((coeficients, constants))
coeficients_rank = np.linalg.matrix_rank(coeficients)
augmented_rank = np.linalg.matrix_rank(augmented_matrix)
dimension = len(variables) - coeficients_rank

# helper prints for debuging
debug = False
if debug:
    print("Variables set sorted: {}".format(variables))
    print("Parsed equations: {}".format(lines))
    print("Coef_rank: {}, Aug_rank: {}".format(coeficients_rank, augmented_rank))
    print("Coeficients: {}".format(coeficients))
    print("Augmented matrix: {}".format(augmented_matrix))

if coeficients_rank != augmented_rank:
    print("no solution")
else:
    if coeficients_rank == len(variables):
        answer = ""
        solution = np.linalg.solve(coeficients, constants)  # returns list of floats
        for i in range(len(variables)):
            # if solution is integer, convert ot integer, otherwise stays float
            answer += " {} = {},".format(variables[i], int(solution[i]) if solution[i].is_integer() else solution[i])
        print("solution:{}".format(answer[:-1]))  # [:-1], there is "," at the end
    else:
        print("solution space dimension: {}".format(dimension))
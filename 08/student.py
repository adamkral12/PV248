import sys
import pandas
import numpy
import json
from datetime import datetime
from datetime import timedelta


def normalizeColName(col: str):
    col = col.strip()
    if col == 'student':
        return col
    return col.split('/')[1]


def normalizeColNameDate(col: str):
    col = col.strip()
    if col == 'student':
        return col
    return col.split('/')[0]


def regression(groupedDates):
    # print(groupedDates[8])
    # print(groupedDates.values)
    # print(groupedDates.values)
    # for key, date in groupedDates.iteritems():
    #     print(key)
    #     print(date)
    startDate = datetime.strptime('2018-09-17', "%Y-%m-%d").date()
    x = [(datetime.strptime(key, "%Y-%m-%d").date() - startDate).days for key, val in groupedDates.iteritems()]

    y = []
    totalSum = 0
    for item in groupedDates.values:
        totalSum += item
        y.append(totalSum)

    x = numpy.array(x)
    y = numpy.array(y)
    xi = x[:, numpy.newaxis]
    regSlope, _, _, _ = numpy.linalg.lstsq(xi, y, rcond=None)
    regSlope = regSlope[0]
    if regSlope != 0:
        sixteen = str(startDate + timedelta(16 / regSlope))
        twenty = str(startDate + timedelta(20 / regSlope))
    else:
        sixteen = None
        twenty = None
    return regSlope, sixteen, twenty


fileName = sys.argv[1]
studentId = sys.argv[2]
df1 = pandas.read_csv(fileName)

# df2 = df1.set_index("student", drop=True)
if studentId == 'average':
    df1 = df1.drop(columns='student')

    studentDateValues = df1.rename(columns=lambda x: normalizeColNameDate(x), inplace=False)
    studentDateValues = studentDateValues.groupby(axis=1, level=0).sum()
    studentDateValues = studentDateValues.describe().loc['mean']

    df1.rename(columns=lambda x: normalizeColName(x), inplace=True)
    studentValues = df1.groupby(axis=1, level=0).sum()
    studentValues = studentValues.describe().loc['mean', :]
else:
    studentValues = df1.loc[df1['student'] == int(studentId)]
    studentValues = studentValues.drop(columns='student')

    studentDateValues = studentValues.rename(columns=lambda x: normalizeColNameDate(x), inplace=False)
    studentDateValues = studentDateValues.groupby(axis=1, level=0).sum()
    studentDateValues = studentDateValues.T
    studentDateValues = studentDateValues[studentDateValues.keys()[0]]
    # print(studentDateValues[studentDateValues.keys()[0]])

    studentValues = studentValues.rename(columns=lambda x: normalizeColName(x), inplace=False)

    studentValues = studentValues.groupby(axis=1, level=0).sum()
    studentValues = studentValues.T

slope, sixteen_points_date, twenty_points_date = regression(studentDateValues)
values = studentValues.values

data = {
    'mean': numpy.mean(values),
    'median': numpy.percentile(values, 50),
    'total': numpy.sum(values),
    'passed': len([i for i in values if i > 0]),
    'regression slope': slope,
    'date 16': sixteen_points_date,
    'date 20': twenty_points_date,
}

print(json.dumps(data, indent=4, ensure_ascii=False))
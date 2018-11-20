import sys
import pandas
import numpy
import json


def normalizeColName(col: str, usedMode: str):
    col = col.strip()
    if col == 'student':
        return col

    if usedMode == 'dates':
        return col.split('/')[0]
    elif usedMode == 'exercises':
        return col.split('/')[1]
    elif usedMode == 'deadlines':
        return col
    else:
        raise Exception("unknown mode {}".format(usedMode))


fileName = sys.argv[1]
mode = sys.argv[2]
data = {}
df1 = pandas.read_csv(fileName)
df2 = df1.set_index("student", drop=False)
df2.rename(columns=lambda x: normalizeColName(x, mode), inplace=True)
df2 = df2.groupby(axis=1, level=0).sum()

for colName in list(df2.columns.values):
    if colName == "student":
        pass
    else:
        pointInCol = df2.loc[:, colName]

        passed = len([i for i in pointInCol.values if i > 0])
        dataInCol = {
            'mean': numpy.mean(pointInCol.values),
            'passed': passed,
            'median': numpy.median(pointInCol.values),
            'first': numpy.percentile(pointInCol.values, 25),
            'last': numpy.percentile(pointInCol.values, 75),
        }
        data[colName] = dataInCol

# print(data)
print(json.dumps(data, indent=4, ensure_ascii=False))

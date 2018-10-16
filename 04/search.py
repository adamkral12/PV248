import sqlite3
import sys
import json

# puts author_name as key
# removes none
def dict_factory(cursor, row):
    d = {}
    data = {}
    name = ""

    for idx, col in enumerate(cursor.description):
        if col[0] == 'author_name':
            name = row[idx]
        else:
            data[col[0]] = row[idx]
    d[name] = data
    return d

conn = sqlite3.connect("../03/scorelib.dat")
conn.row_factory = dict_factory
cur = conn.cursor()

query = "Select p.name as author_name, p.id as 'Print Number', " \
        "p.name as 'Composer', s.name as 'Title', " \
        "s.genre as 'Genre', s.key as 'Key', s.year as 'Composition Year', " \
        "e.name as 'Edition', print.partiture as 'Partiture' " \
        "from print " \
        "join edition e on print.edition = e.id " \
        "join score s on e.score = s.id " \
        "join score_author a on s.id = a.score " \
        "join person p on a.composer = p.id " \
        "where p.name like ?;"

cur.execute(query, ["%"+sys.argv[1]+"%"])
composers = cur.fetchall()
# print(composers)
jsonData = {}
for k in composers.__iter__():
    # print(k)
    for i in k:
        if i in jsonData:
            jsonData[i].append(k[i])
        else:
            jsonData[i] = [k[i]]

print(json.dumps(jsonData, ensure_ascii=False, indent=4, separators=(',', ': ')))

conn.close()
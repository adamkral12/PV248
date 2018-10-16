import sqlite3
import sys
import json

# puts property names
# removes none
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        if row[idx]:
                d[col[0]] = row[idx]
    return d


conn = sqlite3.connect("../03/scorelib.dat")
conn.row_factory = dict_factory
cur = conn.cursor()

query = "Select p.name, p.born, p.died from print " \
        "join edition e on print.edition = e.id " \
        "join score s on e.score = s.id " \
        "join score_author a on s.id = a.score " \
        "join person p on a.composer = p.id " \
        "where print.id = ?;"


cur.execute(query, [sys.argv[1]])
composers = cur.fetchall()

print(json.dumps(composers, ensure_ascii=False, indent=4, separators=(',', ': ')))
conn.close()
import sys
import sqlite3


conn = sqlite3.connect(sys.argv[1])
cur = conn.cursor()
query = "SELECT name, born, died from person order by name;"
cur.execute(query)
people1 = cur.fetchall()

query = "SELECT p.partiture, e.name, s.name, s.genre, s.key, s.incipit, s.year" \
        " from print p" \
        " join edition e on p.edition = e.id" \
        " join score s on e.score = s.id" \
        " order by p.id"
cur.execute(query)
prints1 = cur.fetchall()

conn.close()

conn = sqlite3.connect(sys.argv[2])
cur = conn.cursor()
query = "SELECT name, born, died from person order by name;"
cur.execute(query)
people2 = cur.fetchall()

query = "SELECT p.partiture, e.name, s.name, s.genre, s.key, s.incipit, s.year" \
        " from print p " \
        "join edition e on p.edition = e.id" \
        " join score s on e.score = s.id" \
        " order by p.id"
cur.execute(query)
prints2 = cur.fetchall()

conn.close()

i = 0
for person in people1:
    # assert person[0] == people2[i][0], "People names dont match 1: " + person[0] + ", 2: " + people2[i][0] + ", row " + str(i+1)
    # assert person[1] == people2[i][1], "People born dont match 1: " + (str(person[1]) if person[1] else "null") + ", 2: " + (str(people2[i][1]) if people2[i][1] else "null") + ", row " + str(i+1)
    # assert person[2] == people2[i][2], "People died dont match 1: " + (str(person[2]) if person[2] else "null") + ", 2: " + (str(people2[i][2]) if people2[i][2] else "null") + ", row " + str(i+1)
    i += 1

i = 0
for printClass in prints1:
    assert printClass[0] == prints2[i][0], "Print partiture dont match 1: " + (printClass[0] if printClass[0] else "null") + ", 2: " + prints2[i][0] + ", row " + str(i+1)
    assert printClass[1] == prints2[i][1], "Edition name dont match 1: " + (printClass[1] if printClass[1] else "null") + ", 2: " + prints2[i][1] + ", row " + str(i+1)
    i += 1

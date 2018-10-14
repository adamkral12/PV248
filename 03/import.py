import sqlite3
import sys
from classes import PrintDB, PersonDB


def insertPrint(printClass: PrintDB, cur):

    # compositions/composers
    composition = printClass.edition.composition
    composerIds = []
    for composer in composition.authors:
        query = "SELECT id, name from person where name = ?;"
        cur.execute(query, [composer.name])
        people = cur.fetchone()
        if people:
            print(people)
            composerIds.append(people[0])
        else:
            query = "insert into person (born, died, `name`) values (?,?,?);"
            cur.execute(query, (composer.born, composer.died, composer.name))
            composerIds.append(cur.lastrowid)
            conn.commit()

    query = "INSERT INTO score (name, genre, key, incipit, year) values (?,?,?,?,?);"
    cur.execute(query, (composition.name, composition.genre, composition.key, composition.incipit, composition.year))
    compositionId = cur.lastrowid
    conn.commit()

    for composerId in composerIds:
        query = "INSERT INTO score_author(score, composer) VALUES (?,?);"
        cur.execute(query, (compositionId, composerId))
        conn.commit()

    # edition/editors
    editorIds = []
    for editor in printClass.editors():
        query = "SELECT id, name from person where name = ?;"
        cur.execute(query, [editor.name])
        people2 = cur.fetchone()
        if people2:
            print(people2)
            editorIds.append(people2[0])
        else:
            query = "insert into person (born, died, `name`) values (?,?,?);"
            cur.execute(query, (editor.born, editor.died, editor.name))
            editorIds.append(cur.lastrowid)
            conn.commit()

    edition = printClass.edition
    query = "INSERT INTO edition (score, `name`) values (?,?);"
    cur.execute(query, (compositionId, edition.name))
    editionId = cur.lastrowid
    conn.commit()

    for editorId in editorIds:
        query = "INSERT INTO edition_author (edition, editor) VALUES (?,?);"
        cur.execute(query, (editionId, editorId))
        conn.commit()
    # voices
    for voice in composition.voices:
        query = "INSERT INTO voice (number, score, range, name) VALUES (?,?,?,?);"
        cur.execute(query, (voice.number, compositionId, voice.range, voice.name))
        conn.commit()

    query = "INSERT INTO print (id, edition, partiture) values (?,?,?);"
    if printClass.partiture:
        part = "Y"
    else:
        part = "N"
    cur.execute(query, (printClass.print_id, editionId, part))
    conn.commit()


def load(filename):
    tempData = {}
    prints = []
    for line in open(filename, "r"):
        if line not in ['\n', '\r\n']:
            data = line.split(":")
            tempData[data[0].rstrip()] = data[1].rstrip().strip()
        else:
            if tempData:
                prints.append(PrintDB.fromData(tempData))
                tempData = {}
    if tempData:
        prints.append(PrintDB.fromData(tempData))
    return prints


printclasses = load(sys.argv[1])

conn = sqlite3.connect("scorelib.dat")
cur = conn.cursor()

with open('scorelib.sql') as fp:
    cur.executescript(fp.read())  # or con.executescript

for printclass in printclasses:
    insertPrint(printclass, cur)

conn.close()
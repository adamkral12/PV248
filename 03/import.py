import sqlite3
import sys
from classes import PrintDB, PersonDB


def insertPrint(printClass: PrintDB, cur):

    # compositions/composers
    composition = printClass.edition.composition
    composerIds = []
    for composer in composition.authors:
        query = "insert into person (born, died, `name`) values (?,?,?);"
        cur.execute(query, (composer.born, composer.died, composer.name))
        composerIds.append(cur.lastrowid)

    query = "INSERT INTO score (name, genre, key, incipit, year) values (?,?,?,?,?);"
    cur.execute(query, (composition.name, composition.genre, composition.key, composition.incipit, composition.year))
    compositionId = cur.lastrowid

    for composerId in composerIds:
        query = "INSERT INTO score_author(score, composer) VALUES (?,?);"
        cur.execute(query, (compositionId, composerId))


    # edition/editors
    editorIds = []
    for editor in printClass.editors():
        query = "insert into person (born, died, `name`) values (?,?,?);"
        cur.execute(query, (editor.born, editor.died, editor.name))
        editorIds.append(cur.lastrowid)

    edition = printClass.edition
    query = "INSERT INTO edition (score, `name`) values (?,?);"
    cur.execute(query, (compositionId, edition.name))
    editionId = cur.lastrowid

    for editorId in editorIds:
        query = "INSERT INTO edition_author (edition, editor) VALUES (?,?);"
        cur.execute(query, (editionId, editorId))
    # voices
    for voice in composition.voices:
        query = "INSERT INTO voice (number, score, range, name) VALUES (?,?,?,?);"
        cur.execute(query, (1, compositionId, voice.range, voice.name))

    query = "INSERT INTO print (id, edition, partiture) values (?,?,?);"
    cur.execute(query, (printClass.print_id, editionId, printClass.partiture))
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
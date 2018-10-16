import sqlite3
import sys
from classes import PrintDB, PersonDB


def insertPrint(printClass: PrintDB, cur):

    # compositions/composers
    composition = printClass.edition.composition
    composerIds = []
    for composer in composition.authors:
        query = "SELECT id, name, born, died from person where name = ?;"
        cur.execute(query, [composer.name])
        people = cur.fetchone()
        if people:
            if not people[2]:
                query = "update person set born = (?) where id = ?;"
                cur.execute(query, (composer.born, people[0]))
                conn.commit()
            if not people[3]:
                query = "update person set died = (?) where id = ?;"
                cur.execute(query, (composer.died, people[0]))
                conn.commit()
            composerIds.append(people[0])
        else:
            query = "insert into person (born, died, `name`) values (?,?,?);"
            cur.execute(query, (composer.born, composer.died, composer.name))
            composerIds.append(cur.lastrowid)
            conn.commit()

    query = "SELECT id, name, genre, key, incipit, year " \
            "FROM score " \
            "WHERE name is ? " \
            "and genre is ? " \
            "AND key is ? " \
            "AND incipit is ?" \
            "AND year is ?;"
    cur.execute(query, (composition.name, composition.genre, composition.key, composition.incipit, composition.year))
    foundCompositions = cur.fetchall()
    new_composition = False
    if foundCompositions:
        for foundComposition in foundCompositions:
            query = "SELECT name, range FROM voice where score is ?"
            cur.execute(query, [foundComposition[0]])
            foundVoices = cur.fetchall()
            sameVoices = set((voice.name, voice.range) for voice in composition.voices) == set(foundVoices)
            if sameVoices:
                query = "SELECT name FROM score_author join person on score_author.composer = person.id where score is ?"
                cur.execute(query, [foundComposition[0]])
                foundComposers = cur.fetchall()
                sameComposers = set(author.name for author in composition.authors) == (set([author[0] for author in foundComposers]))
                if sameComposers:
                    compositionId = foundComposition[0]
                else:
                    new_composition = True
                    query = "INSERT INTO score (name, genre, key, incipit, year) values (?,?,?,?,?);"
                    cur.execute(query, (composition.name, composition.genre, composition.key, composition.incipit, composition.year))
                    compositionId = cur.lastrowid
                    conn.commit()
                    break
            else:
                # insert
                new_composition = True
                query = "INSERT INTO score (name, genre, key, incipit, year) values (?,?,?,?,?);"
                cur.execute(query,(composition.name, composition.genre, composition.key, composition.incipit, composition.year))
                compositionId = cur.lastrowid
                conn.commit()
                break
    else:
        new_composition = True
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
        query = "SELECT id, name, born, died from person where name = ?;"
        cur.execute(query, [editor.name])
        people2 = cur.fetchone()
        if people2:
            if not people2[2]:
                query = "update person set born = ? where id = ?;"
                cur.execute(query, (editor.born, people2[0]))
                conn.commit()
            if not people2[3]:
                query = "update person set died = ? where id = ?;"
                cur.execute(query, (editor.died, people2[0]))
                conn.commit()
            editorIds.append(people2[0])
        else:
            query = "insert into person (born, died, `name`) values (?,?,?);"
            cur.execute(query, (editor.born, editor.died, editor.name))
            editorIds.append(cur.lastrowid)
            conn.commit()

    edition = printClass.edition
    query = "SELECT score, name, year from edition " \
            "where score is ? " \
            "and name is ?;"
    cur.execute(query, (compositionId, edition.name))
    foundEditions = cur.fetchone()
    if foundEditions:
        query = "SELECT name FROM edition_author join person on edition_author.editor = person.id where edition_author.edition is ?"
        cur.execute(query, [foundEditions[0]])
        foundEditors = cur.fetchall()
        sameEditors = set(author.name for author in edition.authors) == (set([author[0] for author in foundEditors]))
        if sameEditors:
            editionId = foundEditions[0]
        else:
            query = "INSERT INTO edition (score, `name`) values (?,?);"
            cur.execute(query, (compositionId, edition.name))
            editionId = cur.lastrowid
            conn.commit()
    else:
        query = "INSERT INTO edition (score, `name`) values (?,?);"
        cur.execute(query, (compositionId, edition.name))
        editionId = cur.lastrowid
        conn.commit()

    for editorId in editorIds:
        query = "INSERT INTO edition_author (edition, editor) VALUES (?,?);"
        cur.execute(query, (editionId, editorId))
        conn.commit()
    # voices
    if new_composition:
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
            data = line.split(":", 1)
            tempData[data[0].rstrip()] = data[1].rstrip().strip()
        else:
            if tempData:
                prints.append(PrintDB.fromData(tempData))
                tempData = {}
    if tempData:
        prints.append(PrintDB.fromData(tempData))
    return prints


printclasses = load(sys.argv[1])

conn = sqlite3.connect(sys.argv[2])
cur = conn.cursor()

with open('scorelib.sql') as fp:
    cur.executescript(fp.read())

for printclass in printclasses:
    insertPrint(printclass, cur)

conn.close()
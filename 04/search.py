import sqlite3
import sys
import json

# default doc
def default_dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

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
            if col[0] == 'Partiture':
                if row[idx] == 'Y':
                    data[col[0]] = True
                else:
                    data[col[0]] = False
            else:
                data[col[0]] = row[idx]
    d[name] = data
    return d

conn = sqlite3.connect("../03/scorelib.dat")
conn.row_factory = dict_factory
cur = conn.cursor()

# "v.number as 'voice_number', v.name as 'voice_name', v.number as 'voice_number' "
# "join voice v on s.id = v.score " \

query = "Select p.name as author_name, p.id as 'Print Number', " \
    "p.name as 'Composer', s.name as 'Title', s.id as 's_id', e.id as 'e_id', " \
    "s.genre as 'Genre', s.key as 'Key', s.year as 'Composition Year', " \
        "s.incipit as 'Incipit', " \
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

# add voices
conn.close()
conn = sqlite3.connect("../03/scorelib.dat")
cur = conn.cursor()

for k, v in jsonData.items():
    for k2, v2 in enumerate(v):
        voices = {}
        query = "Select number, range, name from voice where score = ?;"
        cur.execute(query, [v2['s_id']])
        foundVoices = cur.fetchall()
        for voice in foundVoices:
            voices[voice[0]] = {"name": voice[1], "range": voice[2]}
        jsonData[k][k2]['Voices'] = voices
        # jsonData[k][k2].pop('s_id', None)

# add editors
for k, v in jsonData.items():
    for k2, v2 in enumerate(v):
        editors = []
        query = "Select p.name, born, died from edition " \
                "join edition_author a on edition.id = a.edition " \
                "join person p on a.editor = p.id " \
                "where score = ?;"
        cur.execute(query, [v2['e_id']])
        foundEditors = cur.fetchall()
        for editor in foundEditors:
            editors.append({"name": editor[0], "born": editor[1], "died": editor[2]})
        jsonData[k][k2]['Editor'] = editors
        jsonData[k][k2].pop('e_id', None)

# add composers
for k, v in jsonData.items():
    for k2, v2 in enumerate(v):
        composers = []
        query = "Select p.name, born, died from score s " \
                "join score_author sa on s.id = sa.score " \
                "join person p on sa.composer = p.id " \
                "where score = ?;"
        cur.execute(query, [v2['s_id']])
        foundComposers = cur.fetchall()
        for composer in foundComposers:
            composers.append({"name": composer[0], "born": composer[1], "died": composer[2]})
        jsonData[k][k2]['Composer'] = composers
        jsonData[k][k2].pop('s_id', None)



print(json.dumps(jsonData, ensure_ascii=False, indent=4, separators=(',', ': ')))

conn.close()


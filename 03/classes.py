import sys
sys.path.insert(0, './../02')
import re
from scorelib import Print, Person, Composition, Voice, Edition


class PersonDB(Person):
    def toArray(self):
        return self.born, self.died, self.name


class VoiceDB:
    def __init__(self, number: int, name: str=None, range: str=None):
        self.name = name
        self.range = range
        self.number = number

    @staticmethod
    def fromData(number, data) -> 'VoiceDB':
        voiceRange = re.match(r"(.*)--([^,;]*)[,;](.*)", data)
        if voiceRange:
            return VoiceDB(number, voiceRange.group(3).strip(), voiceRange.group(1) + "--" + voiceRange.group(2))
        else:
            return VoiceDB(number, data)


class CompositionDB(Composition):
    @staticmethod
    def fromData(data) -> 'CompositionDB':
        voices = []
        for key, val in data.items():
            voiceMatch = re.match(r"(.*)Voice(.*)", key)
            if voiceMatch:
                voices.append(VoiceDB.fromData(voiceMatch.group(2), val))

        composers = []
        if "Composer" in data:
            for composer in data["Composer"].split(";"):
                if Person.fromData(composer.strip()):
                    composers.append(Person.fromData(composer.strip()))

        title = data["Title"].rstrip().strip() if "Title" in data else None
        incipit = data["Incipit"].rstrip().strip() if "Incipit" in data else None
        key = data["Key"].rstrip().strip() if "Key" in data else None
        genre = data["Genre"].rstrip().strip() if "Genre" in data else None
        return Composition(
            title if title else None,
            incipit if incipit else None,
            key if key else None,
            genre if genre else None,
            Composition.processCompositionYear(data["Composition Year"]) if "Composition Year" in data else None,
            voices,
            composers
        )


class PrintDB(Print):
    def editors(self):
        return self.edition.authors


    def compositors(self):
        return self.edition.composition.authors

    @staticmethod
    def fromData(data) -> 'PrintDB':
        if "Partiture" in data:
            if re.search("yes", data["Partiture"].lower()):
                partiture = True
            else:
                partiture = False
        else:
            partiture = False

        return PrintDB(
            Edition.fromData(data, CompositionDB.fromData(data)),
            data["Print Number"] if "Print Number" in data else None,
            partiture
        )

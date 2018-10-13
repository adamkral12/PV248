import sys
sys.path.insert(0, './../02')
import re
from scorelib import Print, Person, Composition, Voice, Edition


class PrintDB(Print):
    def editors(self):
        return self.edition.authors


    def compositors(self):
        return self.edition.composition.authors


    def toArray(self):
        pass

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
            Edition.fromData(data, Composition.fromData(data)),
            data["Print Number"] if "Print Number" in data else None,
            partiture
        )


class PersonDB(Person):
    def toArray(self):
        return self.born, self.died, self.name

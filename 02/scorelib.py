import re


class Voice:
    def __init__(self, name: str=None, range: str=None):
        self.name = name
        self.range = range

    def format(self, i):
        string = ""
        if self.name or self.range:
            string += "Voice " + i + ": "
            if self.range and self.name:
                string += self.range + ", " + self.name
            elif self.name:
                string += self.name
            elif self.range:
                string += self.range
            string += "\n"
        return string

    @staticmethod
    def fromData(data) -> 'Voice':
        voiceRange = re.match(r"(.*)--([^,;]*)[,;](.*)", data)
        if voiceRange:
            return Voice(voiceRange.group(3).strip(), voiceRange.group(1) + "--" + voiceRange.group(2))
        else:
            return Voice(data)


class Person:
    def __init__(self, name: str, born: int = None, died: int = None):
        self.name = name
        self.born = born
        self.died = died

    def format(self):
        string = ""
        if self.name:
            string += self.name
        if self.born or self.died:
            lifeString = "--"
            if self.born:
                lifeString = str(self.born) + lifeString
            if self.died:
                lifeString += str(self.died)
            string += "(" + lifeString + ")"
        return string

    @staticmethod
    def fromData(data) -> 'Person' or None:
        if data:
            insideBrackets = re.search(r'(.*)\((.*?)\)', data)
            if insideBrackets:
                name = insideBrackets.group(1).strip()
                years = insideBrackets.group(2)
                yearsSplit = re.search(r'(\d\d\d\d)(-|--)(\d\d\d\d)', years)
                if yearsSplit:
                    return Person(name, int(yearsSplit.group(1)), int(yearsSplit.group(3)))
                else:
                    yearBorn = re.search(r'(\d\d\d\d)(-|--)(.*)', years)
                    yearDied = re.search(r'(.*)(-|--)(\d\d\d\d)', years)
                    if yearBorn:
                        return Person(name, int(yearBorn.group(1)))
                    elif yearDied:
                        return Person(name, None, int(yearDied.group(3)))
                    else:  # find * and +
                        yearBorn = None
                        yearDied = None
                        yearDiedReg = re.search(r'(\+)(\d\d\d\d)', years)
                        if yearDiedReg:
                            yearDied = int(yearDiedReg.group(2))
                        yearBornReg = re.search(r'(\*)(\d\d\d\d)', years)
                        if yearBornReg:
                            yearBorn = int(yearBornReg.group(2))
                        return Person(name, yearBorn, yearDied)
            else:
                return Person(data)


    @staticmethod
    def fromDataEditor(data) -> 'Person' or None:
        if data:
            return Person(data)


class Composition:
    def __init__(
            self,
            name: str=None,
            incipit: str=None,
            key: str=None,
            genre: str=None,
            year: int=None,
            voices: [Voice] = (),
            authors: [Person] = ()
    ):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors

    def format(self, edition, printClass):
        string = ""
        if self.authors:
            string += "Composer: "
        for author in self.authors:
            string += author.format().strip() + "; "
        if self.authors:
            string = string[:-2]
            string += "\n"
        if self.name:
            string += "Title: " + self.name + '\n'
        if self.genre:
            string += "Genre: " + self.genre + '\n'
        if self.key:
            string += "Key: " + self.key + '\n'
        if self.year:
            string += "Composition Year: " + str(self.year) + '\n'

        if edition.name:
            string += "Edition: " + edition.name + '\n'
        if edition.authors:
            string += "Editor: "
        for author in edition.authors:
            string += author.format() + ","
        if edition.authors:
            string = string[:-1]
            string += "\n"

        i = 0
        for voice in self.voices:
            i += 1
            string += voice.format(str(i))

        if printClass.partiture:
            string += "Partiture: yes\n"
        else:
            string += "Partiture: no\n"

        if self.incipit:
            string += "Incipit: " + self.incipit + '\n'
        return string


    @staticmethod
    def fromData(data) -> 'Composition':
        voices = []
        for key, val in data.items():
            if re.match(r"(.*)Voice(.*)", key):
                voices.append(Voice.fromData(val))

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


    @staticmethod
    def processCompositionYear(data):
        regexp = re.compile('(.*)(\d\d\d\d)(.*)')
        match = regexp.match(data)
        return match.group(2) if match else None


class Edition:
    def __init__(
            self,
            composition: Composition,
            authors: [Person] = (),
            name: str = None
    ):
        self.composition = composition
        self.authors = authors
        self.name = name

    def format(self, printClass):
        string = self.composition.format(self, printClass)
        return string


    @staticmethod
    def fromData(data, composition: Composition) -> 'Edition':
        editors = []
        if "Editor" in data:
            splitEditors = []
            for item in data["Editor"].split(","):
                splitEditors.append(item.rstrip().strip())
            i = 0
            for editor in splitEditors:
                if i >= len(splitEditors):
                    break
                if " " in editor:
                    if Person.fromDataEditor(splitEditors[i]):
                        editors.append(Person.fromDataEditor(splitEditors[i]))
                else:
                    try:
                        current = splitEditors[i]
                        nextEditor = splitEditors[i + 1]
                        if Person.fromData(current + nextEditor):
                            editors.append(Person.fromData(current + " " + nextEditor))
                        i += 1
                    except IndexError:
                        if Person.fromData(splitEditors[i]):
                            editors.append(Person.fromData(splitEditors[i]))
                i += 1
        name = data["Edition"].strip() if "Edition" in data else None
        return Edition(
            composition,
            editors,
            name if name else None
        )


class Print:
    def __init__(self, edition: Edition, print_id: int, partiture: bool):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def format(self):
        if self.print_id:
            print("Print Number: " + str(self.print_id))
        print(self.edition.format(self))

    def composition(self):
        return self.edition.composition

    @staticmethod
    def fromData(data) -> 'Print':
        if "Partiture" in data:
            if re.search("yes", data["Partiture"].lower()):
                partiture = True
            else:
                partiture = False
        else:
            partiture = False

        return Print(
            Edition.fromData(data, Composition.fromData(data)),
            int(data["Print Number"]) if "Print Number" in data else None,
            partiture
        )

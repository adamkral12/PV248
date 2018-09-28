class Print:
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def format(self):
        if self.print_id:
            print("Print Number: " + self.print_id)
        print(self.edition.format())
        if self.partiture:
            print("Partiture: " + self.partiture)
    def composition(self):
        return self.edition.composition


class Edition:
    def __init__(self, composition, authors, name):
        self.composition = composition
        self.authors = authors
        self.name = name

    def format(self):
        string = self.composition.format()
        if self.authors:
            for author in self.authors:
                string += "Editor: " + author.format() + "\n"
        if self.name:
            string += "Edition: " + self.name + "\n"

        return string


class Composition:
    def __init__(self, name, incipit, key, genre, year, voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors

    def format(self):
        string = ""
        if self.name:
            string += "Composition: " + self.name + '\n'
        if self.incipit:
            string += "Incipit: " + self.incipit + '\n'
        if self.key:
            string += "Key: " + self.key + '\n'
        if self.genre:
            string += "Genre: " + self.genre + '\n'
        if self.year:
            string += "Composition Year: " + self.year + '\n'
        for voice in self.voices:
            string += voice.format()
        for author in self.authors:
            string += author.format()
        return string


class Voice:
    def __init__(self, name, range):
        self.name = name
        self.range = range

    def format(self):
        string = ""
        if self.name:
            string += "Voice: " + self.name + '\n'
        if self.range:
            string += "Range: " + self.range + '\n'

        return string


class Person:
    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died

    def format(self):
        string = ""
        if self.name:
            string += self.name
        if self.born or self.died:
            lifeString = " - "
            if self.born:
                lifeString = self.born + lifeString
            if self.died:
                lifeString += self.died
            string += lifeString + "\n"
        else:
            string += '\n'

        return string
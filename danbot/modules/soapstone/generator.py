import random
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent


class RandomSoapstoneGenerator:
    def __init__(self, data_folder="original"):
        with open(BASE_PATH / data_folder / "templates.txt") as f:
            self.templates = f.read().splitlines()
        with open(BASE_PATH / data_folder / "words.txt") as f:
            self.words = f.read().splitlines()
        with open(BASE_PATH / data_folder / "supertemplates.txt") as f:
            self.supertemplates = list(map(lambda s: s.replace(r"\n", "\n"), f.read().splitlines()))

    def get_template(self):
        return random.choice(self.templates)

    def get_word(self):
        return random.choice(self.words)

    def get_supertemplate(self):
        return random.choice(self.supertemplates)

    def get_simple_soapstone(self):
        word = self.get_word()
        template = self.get_template()

        return template.format(word)

    def get_complex_soapstone(self):
        sentence1 = self.get_simple_soapstone()
        sentence2 = self.get_simple_soapstone()
        supertemplate = self.get_supertemplate()

        return supertemplate.format(sentence1, sentence2)

    def get_soapstone(self):
        if random.random() < 0.5:
            return self.get_simple_soapstone()
        else:
            return self.get_complex_soapstone()


if __name__ == "__main__":
    soapstone_generator = RandomSoapstoneGenerator()
    for _ in range(10):
        print(soapstone_generator.get_soapstone())
        print()

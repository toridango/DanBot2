import random


class SoapstoneGenerator:
    def __init__(self):
        with open("templates.txt") as f:
            self.templates = f.read().splitlines()
        with open("words.txt") as f:
            self.words = f.read().splitlines()
        with open("conjunctions.txt") as f:
            self.conjunctions = f.read().splitlines()

    def get_random_template(self):
        return random.choice(self.templates)

    def get_random_word(self):
        return random.choice(self.words)

    def get_random_conjunction(self):
        return random.choice(self.conjunctions)

    def get_simple_random_soapstone(self):
        word = self.get_random_word()
        template = self.get_random_template()

        return template.format(word)

    def get_complex_random_soapstone(self):
        sentence1 = self.get_simple_random_soapstone()
        sentence2 = self.get_simple_random_soapstone()
        conjunction = self.get_random_conjunction()

        return f"{sentence1}\n{conjunction} {sentence2}"

    def get_random_soapstone(self):
        if random.random() < 0.5:
            return self.get_simple_random_soapstone()
        else:
            return self.get_complex_random_soapstone()


if __name__ == "__main__":
    soapstone_generator = SoapstoneGenerator()
    for _ in range(10):
        print(soapstone_generator.get_random_soapstone())
        print()

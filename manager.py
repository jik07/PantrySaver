from difflib import SequenceMatcher
import os

from text_extraction import TextExtractor

class Manager():
    def __init__(self):
        self.all_ingredients = set()
        self.ingredients = set()

        self.itc = dict() # ingredient to category
        self.cti = dict() # category to ingredients

        self._populate_ingredients("ingredients")
        self.te = TextExtractor(False)

    def _populate_ingredients(self, path):
        for txt in os.listdir(path):
            cat = os.path.splitext(os.path.basename(txt))[0]
            self.cti[cat] = set()
            with open(path + "/" + txt, "r") as f:
                for line in f:
                    l = line.strip()
                    self.all_ingredients.add(l)
                    self.itc[l] = cat
                    self.cti[cat].add(l)


    def remove_ingredient(self, removed):
        self.ingredients.remove(removed)

    def add_ingredient(self, added):
        self.ingredients.add(added)

    def get_ingredients(self):
        return self.ingredients

    def guess_ingredients(self, img):
        progress = 0
        yield progress

        raw_text = self.te.get_raw_text(img)
        progress += 50

        yield progress

        result = []
        gen = self.process_text(raw_text)
        while True:
            new_line, percent = next(gen, [None, None])

            if new_line == None:
                progress = 100
                yield progress
                break

            progress += percent
            result.append(new_line)
            yield progress

        yield result

    def filter_text(self, line):
        return ''.join(x.lower() for x in line if x.isalpha() or x == " ").replace(" ", "_")

    def process_text(self, raw_text):
        for i, line in enumerate(raw_text):
            new_line = [line, None]
            line = self.filter_text(line)

            closest = self.closest_ingredients(line, 3)

            if closest[0][0] > 0.55:
                new_line[1] = closest

            yield new_line, i/len(raw_text) * 50


    def closest_ingredients(self, ingredient, num_results):
        sim = [[0, ing] for ing in self.all_ingredients]
        for i in range(len(sim)):
            sim[i][0] = SequenceMatcher(None, ingredient, sim[i][1]).ratio()

        sim.sort(reverse=True)
        return sim[:num_results]

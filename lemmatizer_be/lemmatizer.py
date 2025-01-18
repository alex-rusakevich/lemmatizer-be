import json
from pathlib import Path

from lemmatizer_be._util import timer

DATA_DIR = Path(Path(__file__).parent.parent, "data")
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Lemmatizer:
    @timer
    def __init__(self):
        lemma_data = json.load(open(DATA_DIR / "lemma_data.json", "r", encoding="utf8"))
        self._changeable = lemma_data["change"]
        self._unchangeable = lemma_data["leave"]

    @timer
    def lemmatize(self, word):
        if word in self._unchangeable:
            return [word]

        lemma = self._changeable.get(word, None)

        if not lemma:
            lemma = [word]

        return lemma

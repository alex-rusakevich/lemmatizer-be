"""The lemmatizer main file."""

# ruff: noqa: T201

from __future__ import annotations

import csv
from pathlib import Path

from lemmatizer_be._utils import _fetch_unzip

DATA_DIR = Path(Path(__file__).parent.parent.parent, "data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

LEMMA_DATA_URL = "https://github.com/alex-rusakevich/lemmatizer-be/releases/latest/download/lemma_data.zip"


class BnkorpusLemmatizer:
    """Belarusian language lemmatizer based on bnkorpus."""

    def __init__(self):
        """Load the lemma dictionaries into memory."""
        if (
            not (DATA_DIR / "change.json").is_file()
            or not (DATA_DIR / "leave.txt").is_file()
        ):
            print("The lemmatizer's data is missing, downloading...")
            _fetch_unzip(LEMMA_DATA_URL, DATA_DIR)
            print("The lemmatizer's data has been downloaded successfully.")

        self._changeable = {}

        with open(DATA_DIR / "change.tsv", "r", encoding="utf8") as f:
            tsv_file = csv.reader(f, delimiter="\t")

            for line in tsv_file:
                self._changeable[line[0]] = line[1].split(";")

        self._unchangeable = (DATA_DIR / "leave.txt").read_text(encoding="utf8").split()

    def lemmas(self, word: str) -> list[str]:
        """Return list of all the lemmas for the word.

        Parameters
        ----------
        word : str
            the word lemmatizer finds lemmas for

        Returns
        -------
        list[str]
            list of lemmas if any

        """
        if word in self._unchangeable:
            return [word]

        lemma = self._changeable.get(word, None)

        return lemma

    def lemmatize(self, word: str) -> str:
        """Lemmatize ``word`` by picking the shortest of the possible lemmas.

        Uses ``self.lemmas()`` internally.
        Returns the input word unchanged if it cannot be found in WordNet.

        Parameters
        ----------
        word : str
            the word lemmatizer finds lemma for

        Returns
        -------
        str
            the lemma found by lemmatizer

        """
        lemmas = self.lemmas(word)
        return min(lemmas, key=len) if lemmas else word

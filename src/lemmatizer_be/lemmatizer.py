"""The lemmatizer main file."""

# ruff: noqa: T201

from __future__ import annotations

import csv
from pathlib import Path

from tqdm import tqdm

from lemmatizer_be._utils import _fetch_unzip, dir_empty

DATA_DIR = Path(Path(__file__).parent.parent.parent, "data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

LEMMA_DATA_URL = "https://github.com/alex-rusakevich/lemmatizer-be/releases/latest/download/lemma_data.zip"


class BnkorpusLemmatizer:
    """Belarusian language lemmatizer based on bnkorpus."""

    def __init__(self, no_progress_bar: bool = False):
        """Load the lemma dictionaries into memory."""
        if dir_empty(DATA_DIR):
            print("The lemmatizer's data is missing, downloading...")
            _fetch_unzip(LEMMA_DATA_URL, DATA_DIR)
            print("The lemmatizer's data has been downloaded successfully.")

        self._changeable = {}

        with open(DATA_DIR / "lemma_data.tsv", encoding="utf8") as f:
            tsv_file = csv.reader(f, delimiter="\t")

            for line in tqdm(
                tsv_file,
                disable=no_progress_bar,
                desc="Loading the dictionary...",
                total=int(Path(DATA_DIR / "lemma_data_info.txt").read_text()),
            ):
                self._changeable[line[0]] = line[1].split(";")

    def lemmas(self, word: str, pos: str | None = None) -> list[str]:
        """Return list of all the lemmas for the word.

        Parameters
        ----------
        word : str
            the word lemmatizer finds lemmas for

        pos : Optional[str]
            part of speech letter, see https://bnkorpus.info/grammar.be.html.
            ``None`` means "select all".

        Returns
        -------
        list[str]
            list of lemmas if any

        """
        lemmas = self._changeable.get(word, [])

        searched_pos = pos

        if isinstance(pos, str):
            searched_pos = pos.upper()

        filtered_lemmas = []

        for lemma in lemmas:
            lemma_text, lemma_pos = lemma.split("|")

            if searched_pos is not None and lemma_pos != searched_pos:
                continue

            if not lemma_text:
                lemma_text = word

            filtered_lemmas.append(lemma_text)

        return list(set(filtered_lemmas))

    def lemmatize(self, word: str, pos: str | None = None) -> str:
        """Lemmatize ``word`` by picking the shortest of the possible lemmas.

        Uses ``self.lemmas()`` internally.
        Returns the input word unchanged if it cannot be found in WordNet.

        Parameters
        ----------
        word : str
            the word lemmatizer finds lemma for

        pos : Optional[str]
            part of speech letter, see https://bnkorpus.info/grammar.be.html.
            ``None`` means "select all".

        Returns
        -------
        str
            the lemma found by lemmatizer

        """
        lemmas = self.lemmas(word, pos=pos)
        return min(lemmas, key=len) if lemmas else word

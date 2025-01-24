"""The lemmatizer main file."""

# ruff: noqa: T201

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from lemmatizer_be._utils import _fetch_unzip, dir_empty

DATA_DIR = Path(
    os.environ.get(
        "LEMMATIZER_BE_DATA_DIR",
        Path(
            "~",
            ".alerus",
            "shared",
        ),
    ),
    "lemma_data",
).expanduser()
DATA_DIR.mkdir(parents=True, exist_ok=True)

LEMMA_DATA_URL = "https://github.com/alex-rusakevich/lemmatizer-be/releases/latest/download/lemma_data.zip"


class BnkorpusLemmatizer:
    """Belarusian language lemmatizer based on bnkorpus."""

    def __init__(self):
        """Connect to the lemma data sqlite3 db."""
        if dir_empty(DATA_DIR):
            print("The lemmatizer's data is missing, downloading...")
            _fetch_unzip(LEMMA_DATA_URL, DATA_DIR)
            print("The lemmatizer's data has been downloaded successfully.")

        self._conn = sqlite3.connect(str(DATA_DIR / "lemma_data.sqlite3"), check_same_thread=False)
        # check_same_thread=False because we only read, but not change anything
        self._cursor = self._conn.cursor()

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
        self._cursor.execute("SELECT * FROM lemma_data WHERE form = ?", (word,))
        result = self._cursor.fetchone()

        lemmas = result[1].split(";")

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

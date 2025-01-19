"""The lemmatizer main file."""

# ruff: noqa: T201

from __future__ import annotations

import json
from pathlib import Path

from lemmatizer_be._utils import _fetch_unzip

DATA_DIR = Path(Path(__file__).parent.parent.parent, "data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

LEMMA_DATA_URL = "https://github.com/alex-rusakevich/lemmatizer-be/releases/latest/download/lemma_data.zip"


class BnkorpusLemmatizer:
    """Belarusian language lemmatizer based on bnkorpus."""

    def __init__(self):
        """Load the lemma dictionaries into memory."""
        if (not (DATA_DIR / "change.json").is_file() or not (DATA_DIR / "leave.txt").is_file()) and not (
            DATA_DIR / "lemma_data.tar.gz"
        ).is_file():
            _fetch_unzip(LEMMA_DATA_URL, DATA_DIR)
            print("The lemmatizer's data has been downloaded successfully.")

        self._changeable = json.loads((DATA_DIR / "change.json").read_text(encoding="utf8"))
        self._unchangeable = (DATA_DIR / "leave.txt").read_text(encoding="utf8").split()

    def lemmatize(self, word: str) -> list[str]:
        """Return list of lemmas for the word.

        Parameters
        ----------
        word : str
            the word lemmatizer makes lemmas for

        Returns
        -------
        list[str]
            list of lemmas

        """
        if word in self._unchangeable:
            return [word]

        lemma = self._changeable.get(word, None)

        if not lemma:
            lemma = [word]

        return lemma

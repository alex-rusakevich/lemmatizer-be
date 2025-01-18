"""The lemmatizer main file."""

from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(Path(__file__).parent.parent.parent, "data")
DATA_DIR.mkdir(parents=True, exist_ok=True)


class BnkorpusLemmatizer:
    """Belarusian language lemmatizer based on bnkorpus."""

    def __init__(self):
        """Load the lemma dictionaries into memory."""
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

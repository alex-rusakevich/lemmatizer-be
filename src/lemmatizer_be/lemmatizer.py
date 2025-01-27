"""The lemmatizer main file."""

from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path
from typing import Literal

from lemmatizer_be._utils import _fetch_unzip, dir_empty, singleton
from lemmatizer_be.exceptions import LemmatizerBeError

logger = logging.getLogger(__name__)


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

DB_PATH = DATA_DIR / "lemma_data.sqlite3"


@singleton
class BnkorpusLemmatizer:
    """Belarusian language lemmatizer based on bnkorpus."""

    def __init__(self, db_storage: Literal["memory", "disk"] = "memory"):
        """Connect to the lemma data sqlite3 db.

        Parameters
        ----------
        db_storage : Literal[&quot;memory&quot;, &quot;disk&quot;], optional
            Where to store the lemmas database, by default "disk"
            * "memory" is much faster than "disk", but takes some time to load and a lot of RAM.
            * "disk" starts immediately, takes little RAM, but lemma functions
            are slower than while using "memory" mode.

        """
        if dir_empty(DATA_DIR):
            logger.warning("The lemmatizer's data is missing, downloading...")
            _fetch_unzip(LEMMA_DATA_URL, DATA_DIR)
            logger.warning("The lemmatizer's data has been downloaded successfully.")

        if db_storage == "disk":
            self._conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        elif db_storage == "memory":
            source_conn = sqlite3.connect(str(DB_PATH))
            self._conn = sqlite3.connect(":memory:")

            source_conn.backup(self._conn)
            source_conn.close()
        else:
            msg = f"Wrong db_storage value: {db_storage}"
            raise LemmatizerBeError(msg)

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
        with self._conn:
            cursor = self._conn.cursor()

        cursor.execute("SELECT * FROM lemma_data WHERE form = ?", (word,))
        result = cursor.fetchone()
        lemmas = []

        if result:
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

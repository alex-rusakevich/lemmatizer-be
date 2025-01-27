"""Build lemma dictionary from bnkorpus."""

import locale
import logging
import os
import sqlite3
import sys
import zipfile
from pathlib import Path

from lxml import etree
from tqdm import tqdm

from lemmatizer_be._utils import _fetch_unzip, dir_empty

logger = logging.getLogger(__name__)

locale.setlocale(locale.LC_ALL, "be_BY.UTF-8")

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

BNKORPUS_DIR = Path("~", ".alerus", "shared", "bnkorpus").expanduser()
BNKORPUS_DIR.mkdir(parents=True, exist_ok=True)

BNKORPUS_URL = "https://github.com/Belarus/GrammarDB/releases/download/RELEASE-202309/RELEASE-20230920.zip"


INFO_TEXT = """
База дадзеных лематызатара lemmatizer-be (https://github.com/alex-rusakevich/lemmatizer-be).

БД змяшчае {} адпаведнасцяў "форма → лемы".

Лемы запісаны праз кропку з коскай. Пасля кожнай лемы ідзе інфармацыя пра частку мовы ў фармаце |X, дзе X — гэта частка мовы (гл. https://bnkorpus.info/grammar.be.html).

БД заснавана на граматычным корпусе праекту "Беларускі N-корпус", за што асаблівы дзякуй яго стваральнікам.
""".strip()


def strip_plus(word):  # noqa: D103
    return word.replace("+", "")


def main():  # noqa: D103
    if dir_empty(BNKORPUS_DIR):
        logger.warning("BNK is missing. Downloading...")
        _fetch_unzip(BNKORPUS_URL, BNKORPUS_DIR)

    # region Creating database
    db_path = str(DATA_DIR / "lemma_data.sqlite3")
    if Path(db_path).is_file():
        os.remove(db_path)

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lemma_data (
            form TEXT NOT NULL PRIMARY KEY,
            lemmas TEXT NOT NULL
        );
    """)

    # cursor.execute("""
    #     CREATE INDEX IF NOT EXISTS index_forms ON lemma_data (form);
    #                """)

    logger.debug("Initialized empty db '%s'", Path(db_path).resolve())

    connection.commit()
    # endregion

    data_dict = {}

    for xml_path in BNKORPUS_DIR.glob("*.xml"):
        tree = etree.fromstring(xml_path.read_bytes())  # noqa: S320
        logger.info("Loaded '%s'. Analyzing...", xml_path)
        sys.stdout.flush()

        for paradigm in tree.findall("Paradigm"):
            paradigm_lemma = strip_plus(paradigm.get("lemma"))

            for variant in paradigm.findall("Variant"):
                pos = paradigm.get("tag", variant.get("tag", "0"))[0]

                for form in variant.findall("Form"):
                    form_text = strip_plus(form.text)

                    if form_text not in data_dict:
                        data_dict[form_text] = set()

                    data_dict[form_text].add(paradigm_lemma + "|" + pos)

    changeable = {}

    for k, v in data_dict.items():
        list_v = list(v)

        for i, val in enumerate(list_v):
            if val.split("|")[0] == k:  # If form == lemma then write |A, not word|A
                list_v[i] = "|" + list_v[0].split("|")[1]

        changeable[k] = sorted(set(list_v), key=len)

    logger.info("Found %d words", len(changeable))

    # Sort by forms ascending
    changeable = sorted(changeable.items(), key=lambda i: i[0])

    # region Writing data
    for word, lemmas in tqdm(changeable, desc="Writing the data into sqlite3 db..."):
        lemmas_val = ";".join(lemmas)

        sqlite_insert_with_param = """INSERT INTO lemma_data
                              (form, lemmas)
                              VALUES (?, ?);"""

        data_tuple = (word, lemmas_val)
        cursor.execute(sqlite_insert_with_param, data_tuple)

    connection.commit()

    logger.info("The changeable db size is %d MB", (Path(db_path).stat().st_size / 1024 / 1024))

    cursor.execute("""VACUUM;""")

    connection.close()
    # endregion

    # region Compressing
    arc_path = DATA_DIR / "lemma_data.zip"

    with zipfile.ZipFile(
        str(arc_path.resolve()),
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
    ) as zip_file:
        zip_file.write(DATA_DIR / "lemma_data.sqlite3", "lemma_data.sqlite3")
        zip_file.writestr(
            "README.txt",
            INFO_TEXT.format(locale.format_string("%d", len(changeable), grouping=True)) + "\n",
        )

    logger.info("The arc file size is %d MB", (arc_path.stat().st_size / 1024 / 1024))
    # endregion


if __name__ == "__main__":
    main()

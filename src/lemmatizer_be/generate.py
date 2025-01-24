"""Build lemma dictionary from bnkorpus."""

# ruff: noqa: T201

import os
import sqlite3
import sys
import zipfile
from pathlib import Path

from lxml import etree
from tqdm import tqdm

from lemmatizer_be._utils import _fetch_unzip, dir_empty

DATA_DIR = Path(
    os.environ.get(
        "LEMMATIZER_BE_DATA_DIR",
        Path(
            "~",
            ".alerus",
            "shared",
        ),
    )
).expanduser()
DATA_DIR.mkdir(parents=True, exist_ok=True)

BNKORPUS_DIR = Path("~", ".alerus", "shared", "bnkorpus").expanduser()
BNKORPUS_DIR.mkdir(parents=True, exist_ok=True)

BNKORPUS_URL = "https://github.com/Belarus/GrammarDB/releases/download/RELEASE-202309/RELEASE-20230920.zip"


def strip_plus(word):  # noqa: D103
    return word.replace("+", "")


def main():  # noqa: D103
    print("bnkorpus status:", end=" ")

    if dir_empty(BNKORPUS_DIR):
        print("missing. Downloading...")
        _fetch_unzip(BNKORPUS_URL, BNKORPUS_DIR)
    else:
        print("OK")

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

    print(f"Initialized empty db '{Path(db_path).resolve()}'")

    connection.commit()
    # endregion

    data_dict = {}

    for xml_path in BNKORPUS_DIR.glob("*.xml"):
        tree = etree.fromstring(xml_path.read_bytes())  # noqa: S320
        print(f"Loaded '{xml_path}'. Analyzing...", end=" ")
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

        print("OK")

    changeable = {}

    for k, v in data_dict.items():
        list_v = list(v)

        for i, val in enumerate(list_v):
            if val.split("|")[0] == k:  # If form == lemma then write |A, not word|A
                list_v[i] = "|" + list_v[0].split("|")[1]

        changeable[k] = sorted(list_v, key=len)

    print(f"Found {len(changeable):_} words")

    # Sort by forms ascending
    changeable = sorted(changeable.items(), key=lambda i: i[0])

    # region Writing data
    for word, lemmas in tqdm(changeable, desc="Writing the data into sqlte3 db..."):
        lemmas_val = ";".join(lemmas)

        sqlite_insert_with_param = """INSERT INTO lemma_data
                              (form, lemmas)
                              VALUES (?, ?);"""

        data_tuple = (word, lemmas_val)
        cursor.execute(sqlite_insert_with_param, data_tuple)

    connection.commit()

    print(f"The changeable db size is {(Path(db_path).stat().st_size / 1024 / 1024):.2f} MB")

    cursor.execute("""VACUUM;""")

    connection.close()
    # endregion

    Path(DATA_DIR / "lemma_data_info.txt").write_text(str(len(changeable)))

    # region Compressing
    arc_path = DATA_DIR / "lemma_data.zip"

    with zipfile.ZipFile(
        str(arc_path.resolve()),
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
    ) as zip_file:
        zip_file.write(DATA_DIR / "lemma_data.sqlite3", "lemma_data.sqlite3")

    print(f"The arc file size is {(arc_path.stat().st_size / 1024 / 1024):.2f} MB")
    # endregion


if __name__ == "__main__":
    main()

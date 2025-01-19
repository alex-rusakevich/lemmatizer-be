"""Build lemma dictionary from bnkorpus."""

# ruff: noqa: T201

import json
import sys
import zipfile
from pathlib import Path

from lxml import etree

from lemmatizer_be._utils import _fetch_unzip, dir_empty

DATA_DIR = Path(Path(__file__).parent.parent.parent, "data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

BNKORPUS_DIR = Path(Path(__file__).parent.parent.parent, "bnkorpus")
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

    data_dict = {}

    for xml_path in BNKORPUS_DIR.glob("*.xml"):
        tree = etree.fromstring(xml_path.read_bytes())  # noqa: S320
        print(f"Loaded '{xml_path}'. Analyzing...", end=" ")
        sys.stdout.flush()

        for paradigm in tree.findall("Paradigm"):
            paradigm_lemma = strip_plus(paradigm.get("lemma"))

            for variant in paradigm.findall("Variant"):
                for form in variant.findall("Form"):
                    form_text = strip_plus(form.text)

                    if form_text not in data_dict:
                        data_dict[form_text] = set()

                    data_dict[form_text].add(paradigm_lemma)

        print("OK")

    changeable = {}
    leaveable = []

    for k, v in data_dict.items():
        list_v = list(v)

        if len(list_v) == 1 and k == list_v[0]:
            leaveable.append(k)
        else:
            changeable[k] = list_v

    print(f"Found {len(leaveable):_} words to be left unchanged and {len(changeable):_} changeable words")

    # region Writing data
    changeable_file_path = DATA_DIR / "change.json"

    json.dump(
        changeable,
        open(changeable_file_path, "w", encoding="utf8"),
        ensure_ascii=False,
        separators=(",", ":"),
    )

    print(f"The changeable file size is {changeable_file_path.stat().st_size / 1024 / 1024:2f} MB")

    leaveable_file_path = DATA_DIR / "leave.txt"

    with open(leaveable_file_path, "w", encoding="utf8") as f:
        for word in leaveable:
            f.write(word)
            f.write("\n")

    print(f"The leaveable file size is {leaveable_file_path.stat().st_size / 1024 / 1024:2f} MB")
    # endregion

    # region Compressing
    arc_path = DATA_DIR / "lemma_data.zip"

    with zipfile.ZipFile(
        str(arc_path.resolve()),
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
    ) as zip_file:
        zip_file.write(str(changeable_file_path.resolve()), "change.json")
        zip_file.write(str(leaveable_file_path.resolve()), "leave.txt")

    print(f"The arc file size is {arc_path.stat().st_size / 1024 / 1024:2f} MB")
    # endregion


if __name__ == "__main__":
    main()

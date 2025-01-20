"""Build lemma dictionary from bnkorpus."""

# ruff: noqa: T201

import sys
import zipfile
from pathlib import Path

from lxml import etree

from lemmatizer_be._utils import _fetch_unzip, dir_empty

DATA_DIR = Path(Path(__file__).parent.parent.parent, "data")
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

        if len(list_v) == 1 and k == list_v[0].split("|")[0]:
            changeable[k] = "|" + list_v[0].split("|")[1]
        else:
            changeable[k] = sorted(list_v)

    print(f"Found {len(changeable):_} words")

    # region Writing data
    changeable_file_path = DATA_DIR / "lemma_data.tsv"

    with open(changeable_file_path, "w", encoding="utf8") as f:
        for word, lemmas in changeable.items():
            if isinstance(lemmas, list):
                f.write("{}\t{}\n".format(word, ";".join(lemmas)))
            else:
                f.write(f"{word}\t{lemmas}\n")

    print(
        f"The changeable file size is {(changeable_file_path.stat().st_size / 1024 / 1024):.2f} MB"
    )
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
        zip_file.write(str(changeable_file_path.resolve()), "lemma_data.tsv")
        zip_file.write(DATA_DIR / "lemma_data_info.txt", "lemma_data_info.txt")

    print(f"The arc file size is {(arc_path.stat().st_size / 1024 / 1024):.2f} MB")
    # endregion


if __name__ == "__main__":
    main()

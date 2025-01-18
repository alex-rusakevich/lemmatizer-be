import io
import json
import os
import zipfile
from pathlib import Path

import requests
from lxml import etree
from tqdm import tqdm

from lemmatizer_be._util import timer

DATA_DIR = Path(Path(__file__).parent.parent, "data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

BNKORPUS_DIR = Path(Path(__file__).parent.parent, "bnkorpus")
BNKORPUS_DIR.mkdir(parents=True, exist_ok=True)

BNKORPUS_URL = "https://github.com/Belarus/GrammarDB/releases/download/RELEASE-202309/RELEASE-20230920.zip"


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def dir_empty(dir_path):
    return not any((True for _ in os.scandir(dir_path)))


def strip_plus(word):
    return word.replace("+", "")


def _fetch_unzip(zip_file_url: str, destination_dir: Path | str) -> Path:
    Path(destination_dir).mkdir(exist_ok=True, parents=True)
    bio = io.BytesIO()

    response = requests.get(zip_file_url, stream=True, timeout=10)
    with tqdm.wrapattr(
        bio,
        "write",
        miniters=1,
        desc=zip_file_url.split("/")[-1],
        total=int(response.headers.get("content-length", 0)),
    ) as fout:
        for chunk in response.iter_content(chunk_size=4096):
            fout.write(chunk)

    z = zipfile.ZipFile(bio)
    z.extractall(destination_dir)

    return Path(destination_dir)


@timer
def main():
    print("bnkorpus status:", end=" ")

    if dir_empty(BNKORPUS_DIR):
        print("missing. Downloading...")
        _fetch_unzip(BNKORPUS_URL, BNKORPUS_DIR)
    else:
        print("OK")

    data_dict = {}

    for xml_path in BNKORPUS_DIR.glob("*.xml"):
        tree = etree.fromstring(xml_path.read_bytes())
        print(f"Loaded '{xml_path}'. Analyzing...", end=" ")

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
        v = list(v)

        if len(v) == 1 and k == v[0]:
            leaveable.append(k)
        else:
            changeable[k] = v

    print(
        f"Found {len(leaveable):_} words to be left unchanged and {len(changeable):_} changeable words"
    )

    data_dict = {"change": changeable, "leave": leaveable}
    output_file_path = DATA_DIR / "lemma_data.json"

    json.dump(
        data_dict,
        open(output_file_path, "w", encoding="utf8"),
        ensure_ascii=False,
        separators=(",", ":"),
    )

    print(
        "The file size is {:2f} MB".format(
            output_file_path.stat().st_size / 1024 / 1024
        )
    )


if __name__ == "__main__":
    main()

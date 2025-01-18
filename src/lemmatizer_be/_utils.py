from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm


def dir_empty(dir_path: str | Path) -> bool:
    return not any(True for _ in os.scandir(dir_path))


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

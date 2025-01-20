"""FastAPI server."""

import os

import uvicorn
from fastapi import FastAPI, Response

from lemmatizer_be import BnkorpusLemmatizer

lm = BnkorpusLemmatizer()
app = FastAPI()


@app.get("/lemmas")
def get_lemmas(word: str) -> Response:
    """Get lemmas for a word.

    Parameters
    ----------
    word : str
        query

    Returns
    -------
    Response
        response

    """
    return {"result": lm.lemmas(word)}


@app.get("/lemma")
def get_lemma(word: str) -> Response:
    """Get one (the shortest) lemma for a word.

    Parameters
    ----------
    word : str
        query

    Returns
    -------
    Response
        response

    """
    return {"result": lm.lemmatize(word)}


def main():  # noqa: D103
    uvicorn.run(
        app,
        host="localhost",
        port=int(os.environ.get("PORT", "8093")),
        log_level="info",
    )


if __name__ == "__main__":
    main()

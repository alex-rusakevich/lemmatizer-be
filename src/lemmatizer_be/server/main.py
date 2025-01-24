"""FastAPI server."""

import os

import fastapi
import uvicorn
from fastapi import FastAPI, Response
from starlette import status

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


@app.get("/")
def redirect_to_docs() -> Response:
    """Redirect to docs when accessing /.

    Returns
    -------
    Response
        _description_

    """
    return fastapi.responses.RedirectResponse("/docs", status_code=status.HTTP_302_FOUND)


def main():  # noqa: D103
    uvicorn.run(
        app,
        host="localhost",
        port=int(os.environ.get("PORT", "8093")),
        log_level="info",
    )


if __name__ == "__main__":
    main()

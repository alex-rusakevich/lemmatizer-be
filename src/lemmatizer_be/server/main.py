"""FastAPI server."""

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

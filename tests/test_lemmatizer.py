import pytest

from lemmatizer_be.lemmatizer import BnkorpusLemmatizer

lemmatizer = BnkorpusLemmatizer()

words_lemmas = (
    ("амлету", ["амлет"]),
    ("в", ["в"]),
    ("робіш", ["рабіць"]),
    (
        "касы",
        ["каса", "касы"],
    ),  # Каса - валасы або каса з грашыма, касы - гэта чалавек з дадатковымі патрэбамі
    ("мех", ["мех"]),
)


@pytest.mark.parametrize(("word", "lemma"), words_lemmas)
def test_word_lemma(word, lemma):
    assert set(lemmatizer.lemmatize(word)) == set(lemma)

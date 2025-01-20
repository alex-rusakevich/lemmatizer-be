import pytest

from lemmatizer_be.lemmatizer import BnkorpusLemmatizer

lemmatizer = BnkorpusLemmatizer()

word_lemma_list = (
    ("амлету", ["амлет"]),
    ("в", ["в"]),
    ("робіш", ["рабіць"]),
    (
        "касы",
        ["каса", "касы"],
    ),  # Каса - валасы або каса з грашыма, касы - гэта чалавек з дадатковымі патрэбамі
    ("мех", ["мех"]),
)


@pytest.mark.parametrize(("word", "lemmas"), word_lemma_list)
def test_word_lemmas(word, lemmas):
    assert set(lemmatizer.lemmas(word)) == set(lemmas)


word_lemma = (
    ("перапісваеш", "перапісваць"),
    ("бівака", "бівак"),
    ("абкружанаму", "акружаны"),
    ("Ляхавічаў", "Ляхавічы"),
    ("хрумшчу", "хрумсцець"),
)


@pytest.mark.parametrize(("word", "lemma"), word_lemma)
def test_word_lemma(word, lemma):
    assert lemmatizer.lemmatize(word) == lemma

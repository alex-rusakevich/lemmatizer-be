# ruff: noqa: T201

import timeit

from lemmatizer_be import BnkorpusLemmatizer

if __name__ == "__main__":
    lm = BnkorpusLemmatizer(db_storage="memory")
    execution_time = timeit.timeit(
        "lm.lemmas('перавырашаць')", globals=globals(), number=100_000
    )
    print(f"Execution time: {execution_time:.9f} seconds")

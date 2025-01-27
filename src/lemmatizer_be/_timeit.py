import logging
import timeit

from lemmatizer_be import BnkorpusLemmatizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    lm = BnkorpusLemmatizer(db_storage="memory")
    execution_time = timeit.timeit("lm.lemmas('перавырашаць')", globals=globals(), number=100_000)
    logger.info("Execution time: %d seconds", execution_time)

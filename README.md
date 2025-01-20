Леммацізатар на аснове Беларускага N-корпуса
===

## Як з ім працаваць?

Каманда ўстаноўкі:

`pip install lemmatizer_be`

Прыклад кода:

```python
from lemmatizer_be import BnkorpusLemmatizer

lm = BnkorpusLemmatizer()
print(lm.lemmatize("Мінску"))
print(lm.lemmatize("алоўка", pos="N"))
```

## Падзякі

Дзякуй праекту "Беларускі N-корпус" і асабліва Алесю Булойчыку, без іх гэты праект быў бы немагчымы.

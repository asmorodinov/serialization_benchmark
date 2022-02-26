# serialization_benchmark

Небольшое приложение на Python, которое тестирует различные библиотеки сериализации/десериализации данных.

## Запуск
```
pip install -r requirements.txt
python benchmark.py
```
Или через докер:
```
docker run asmorodinov/serialization_benchmark
```

## Результаты
(на моей машине)

```
Encoding Test (500 loops)
Package                          Seconds    Size
-----------------------------  ---------  ------
Pickle (native serialization)  0.0070204    2529
MessagePack                    0.0077969    1753
JSON                           0.0247803    2697
Google Protocol Buffers        0.0324707    1999
XML                            0.567505     5936
Apache Avro                    0.852428     1640
YAML                           6.10425      2706

Decoding Test (500 loops)
Package                           Seconds
-----------------------------  ----------
Pickle (native serialization)   0.0123167
MessagePack                     0.0167849
JSON                            0.0290008
Google Protocol Buffers         0.030378
Apache Avro                     0.578425
XML                             0.799554
YAML                           11.545
```

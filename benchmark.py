"""
Dependencies:

    pip install tabulate simplejson xmltodict pyyaml msgpack protobuf avro

"""

from timeit import timeit
from tabulate import tabulate
import sys

import test_message_pb2

message = '''d = {
    'PackageID' : 1539,
    'PersonID' : 33,
    'Name' : """MEGA_GAMER_2222""",
    'Experience' : 42.69,
    'Achievements' : [i ** 2 for i in range(100)],
    'Inventory': dict(('item' + str(i),i) for i in iter(range(100))),
    'CurrentLocation': """
		Pentos is a large port city, more populous than Astapor on Slaver Bay,
		and may be one of the most populous of the Free Cities.
		It lies on the bay of Pentos off the narrow sea, with the Flatlands
		plains and Velvet Hills to the east.
		The city has many square brick towers, controlled by the spice traders.
		Most of the roofing is done in tiles. There is a large red temple in
		Pentos, along with the manse of Illyrio Mopatis and the Sunrise Gate
		allows the traveler to exit the city to the east,
		in the direction of the Rhoyne.
		"""
}'''


setup_pickle    = f'import pickle ; {message} ; src = pickle.dumps(d, 2)'
setup_json      = f'import json ; {message} ; src = json.dumps(d)'

xml_message     = '''d = {'root' : d}'''
setup_xml       = f'import xmltodict ; {message} ; {xml_message} ; src = xmltodict.unparse(d)'

setup_yaml      = f'import yaml ; {message} ; src = yaml.dump(d)'

setup_msgpack   = f'import msgpack ; {message} ; src = msgpack.packb(d)'

setup_protobuf = '''
import test_message_pb2
d = test_message_pb2.TestMessage()
d.PackageID = 1539
d.PersonID = 33
d.Name = "MEGA_GAMER_2222"
d.Experience = 42.69
d.Achievements.extend([i ** 2 for i in range(100)])
d.Inventory.update(dict(('item' + str(i),i) for i in iter(range(100))))
d.CurrentLocation = """
        Pentos is a large port city, more populous than Astapor on Slaver Bay,
		and may be one of the most populous of the Free Cities.
		It lies on the bay of Pentos off the narrow sea, with the Flatlands
		plains and Velvet Hills to the east.
		The city has many square brick towers, controlled by the spice traders.
		Most of the roofing is done in tiles. There is a large red temple in
		Pentos, along with the manse of Illyrio Mopatis and the Sunrise Gate
		allows the traveler to exit the city to the east,
		in the direction of the Rhoyne.
		"""
src = d.SerializeToString()
'''

serialize_avro = '''
byte_stream = BytesIO()
writer = DatumWriter(schema)
encoder = avro.io.BinaryEncoder(byte_stream)
writer.write(d, encoder)
src = byte_stream.getvalue()
'''

setup_avro = '''
import avro
from io import BytesIO
from avro.io import DatumWriter, DatumReader
from avro.datafile import DataFileWriter, DataFileReader

schema = avro.schema.parse(open("avro_test_scheme.avsc", "rb").read())
'''

deserialize_avro = '''
byte_stream = BytesIO(src)
decoder = avro.io.BinaryDecoder(byte_stream)
reader = DatumReader(schema)
d2 = reader.read(decoder)
'''

tests = [
    # (title, setup, enc_test, dec_test)
    ('Pickle (native serialization)', setup_pickle, 'pickle.dumps(d, 2)', 'pickle.loads(src)'),
    ('JSON', setup_json, 'json.dumps(d)', 'json.loads(src)'),
    ('XML', setup_xml, 'xmltodict.unparse(d)', 'xmltodict.parse(src)'),
    ('YAML', setup_yaml, 'yaml.dump(d)', 'yaml.safe_load(src)'),
    ('MessagePack', setup_msgpack, 'msgpack.packb(d)', 'msgpack.unpackb(src)'),
    ('Google Protocol Buffers', setup_protobuf, 'd.SerializeToString()', 'test_message_pb2.TestMessage().ParseFromString(src)'),
    ('Apache Avro', f'{message}\n{setup_avro}\n{serialize_avro}', serialize_avro, deserialize_avro)
]

loops = 500
enc_table = []
dec_table = []

print ("Running tests (%d loops each)" % loops)

for title, setup, enc, dec in tests:
    print(title)

    print("  [Encode]", enc)
    result = timeit(enc, setup, number=loops)

    exec(setup)
    enc_table.append([title, result, sys.getsizeof(src)])

    print("  [Decode]", dec)
    result = timeit(dec, setup, number=loops)
    dec_table.append([title, result])

    # Проверяем, что после десериализации мы получили исходную структуру.
    # Для XML равенство не выполняется, так как в XML все данные сохраняются как строки.
    if title == 'Google Protocol Buffers':
        exec(f'd2 = test_message_pb2.TestMessage() ; d2.ParseFromString(src)')
    elif title == 'Apache Avro':
        exec(dec)
    else:
        exec(f'd2 = {dec}')

    if d != d2:
        print(f'  [Warning] dec(enc(d)) != d')


enc_table.sort(key=lambda x: x[1])
enc_table.insert(0, ['Package', 'Seconds', 'Size'])

dec_table.sort(key=lambda x: x[1])
dec_table.insert(0, ['Package', 'Seconds'])

print ("\nEncoding Test (%d loops)" % loops)
print (tabulate(enc_table, headers="firstrow"))

print ("\nDecoding Test (%d loops)" % loops)
print (tabulate(dec_table, headers="firstrow"))
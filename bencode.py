# -*- coding: utf-8 -*-
"""JSON-like bencode serialization"""
from io import BufferedReader, BytesIO


def dumps(obj):
    buf = BytesIO()
    dump(obj, buf)
    return buf.getvalue()


def dump(obj, stream):
    if isinstance(obj, int):
        stream.write(b'i')
        dump_int(obj, b'e', stream)
    elif isinstance(obj, list):
        stream.write(b'l')
        for v in obj:
            dump(v, stream)
        stream.write(b'e')
    elif isinstance(obj, dict):
        stream.write(b'd')
        for k in sorted(obj.keys()):
            dump(want_bytes(k), stream)
            dump(obj[k], stream)
        stream.write(b'e')
    elif isinstance(obj, bytes):
        dump_int(len(obj), b':', stream)
        stream.write(obj)
    else:
        raise ValueError('Type %s not supported' % type(obj).__name__)


def dump_int(value, term, stream):
    stream.write(str(value).encode())
    stream.write(term)


def want_bytes(value):
    if isinstance(value, bytes):
        return value
    return value.encode('utf-8')


def loads(data):
    if not isinstance(data, bytes):
        raise ValueError('loads expects bytes')
    return load(BufferedReader(BytesIO(data)))


def load(stream):
    obj = decode(stream)
    if stream.read(1):
        raise ValueError('Unexpected data')
    return obj


def decode(stream):
    """Expects a binary stream."""
    token = stream.peek(1)[:1]
    if not token:
        raise ValueError('Unexpected end of stream')
    if token == b'i':
        stream.read(1)
        return read_int(stream, b'e')
    elif token == b'l':
        stream.read(1)
        return read_list(stream)
    elif token == b'd':
        stream.read(1)
        return read_dict(stream)
    else:
        str_length = read_int(stream, b':')
        data = stream.read(str_length)
        if len(data) != str_length:
            raise ValueError('Unexpected end of stream')
        return data


def read_list(stream):
    l = []
    while True:
        if read_terminator(stream, b'e'):
            break
        val = decode(stream)
        l.append(val)
    return l


def read_dict(stream):
    d = {}
    while True:
        if read_terminator(stream, b'e'):
            break
        key = decode(stream)
        if not isinstance(key, bytes):
            raise ValueError('Expected string key')
        val = decode(stream)
        d[key] = val
    return d


def read_terminator(stream, term):
    ch = stream.peek(1)[:1]
    if not ch:
        raise ValueError('Expected terminator')
    if ch == term:
        stream.read(1)
        return True
    return False


def read_int(stream, term):
    buf = BytesIO()
    while True:
        ch = stream.read(1)
        if not ch:
            raise ValueError('Unexpected end of stream')
        elif ch == term:
            break
        elif ch.isdigit():
            buf.write(ch)
        else:
            raise ValueError('Unexpected token: ' + repr(ch))
    data = buf.getvalue()
    if data.startswith(b'0') and data != b'0':
        raise ValueError('Leading zeros are not allowed')
    return int(data)

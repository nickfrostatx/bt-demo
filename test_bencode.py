# -*- coding: utf-8 -*-
from bencode import loads, dumps
import pytest


def test_dump_good_data():
    assert dumps(0) == b'i0e'
    assert dumps(123) == b'i123e'
    assert dumps(b'') == b'0:'
    assert dumps(b'abcdef') == b'6:abcdef'
    assert dumps([]) == b'le'
    assert dumps([[[]]]) == b'llleee'
    assert dumps([1, 2, b'abc']) == b'li1ei2e3:abce'
    assert dumps({}) == b'de'
    assert dumps({b'key': b'value', b'abc': [1, 2, 3]}) == \
        b'd3:abcli1ei2ei3ee3:key5:valuee'
    assert dumps({u'key': b'value', u'abc': [1, 2, 3]}) == \
        b'd3:abcli1ei2ei3ee3:key5:valuee'
    assert dumps({u'日本語': b'abc'}) == \
        b'd9:\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e3:abce'


def test_dump_bad_data():
    for data in (u'abc', set([1]), {u'key': u'text value'}):
        with pytest.raises(ValueError) as exc:
            dumps(data)
        assert 'not supported' in str(exc)


def test_load_good():
    assert loads(b'i0e') == 0
    assert loads(b'i123e') == 123
    assert loads(b'0:') == b''
    assert loads(b'6:abcdef') == b'abcdef'
    assert loads(b'10:abcdefghij') == b'abcdefghij'
    assert loads(b'le') == []
    assert loads(b'llleee') == [[[]]]
    assert loads(b'li1ei2e3:abce') == [1, 2, b'abc']
    assert loads(b'de') == {}
    assert loads(b'd3:abcli1ei2ei3ee3:key5:valuee') == \
        {b'key': b'value', b'abc': [1, 2, 3]}


def test_load_bad():
    exceptions = {
        'loads expects bytes': [u'abc'],
        'Unexpected data': [b'i10eX', b'3:abcX', b'leX', b'deX'],
        'Unexpected end of stream': [b'', b'0', b'1:', b'4:abc', b'd3:abc',
                                     b'i', b'i123', b'123'],
        'Expected terminator': [b'l', b'lllee', b'll0:d', b'dd', b'dl'],
        'Expected string key': [b'di123e', b'dde'],
        'Unexpected token': [b'X', b'lX', b'12X', b'iXXXe', b'i-1e', b'i0Xe'],
        'Leading zeros are not allowed': [b'i00e', b'i01e'],
    }

    for msg in exceptions:
        for data in exceptions[msg]:
            with pytest.raises(ValueError) as exc:
                loads(data)
            assert msg in exc.value.args[0]

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


def test_dump_bad_data():
    for data in (u'abc', set([1]), ):
        with pytest.raises(ValueError) as exc:
            dumps(data)
        assert 'Type %s not supported' % type(data).__name__ in str(exc)

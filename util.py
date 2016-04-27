import binascii
import json


def pretty_format(data):
    return json.dumps(decode_deep(data), sort_keys=True, indent=4,
                      separators=(',', ': '))


def decode_deep(data):
    if isinstance(data, bytes):
        try:
            return data.decode('ascii')
        except ValueError:
            return binascii.hexlify(data).decode('utf-8')
    elif isinstance(data, int):
        return data
    elif isinstance(data, list):
        return [decode_deep(v) for v in list]
    elif isinstance(data, dict):
        obj = {}
        for k in data:
            obj[decode_deep(k)] = decode_deep(data[k])
        return obj

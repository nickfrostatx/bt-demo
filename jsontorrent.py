import bencode
import json
import sys
import util


def pretty_format(data):
    return json.dumps(decode_deep(data), sort_keys=True, indent=4,
                      separators=(',', ': '))


def decode_deep(data):
    if isinstance(data, bytes):
        try:
            return data.decode('ascii')
        except ValueError:
            return '<%d bytes of raw binary>' % len(data)
    elif isinstance(data, int):
        return data
    elif isinstance(data, list):
        return [decode_deep(v) for v in list]
    elif isinstance(data, dict):
        obj = {}
        for k in data:
            obj[decode_deep(k)] = decode_deep(data[k])
        return obj


def main(argv):
    data = bencode.load(open(sys.argv[1], 'rb'))
    print(pretty_format(data))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[0]))

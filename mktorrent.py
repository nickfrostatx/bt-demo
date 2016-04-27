import bencode
import hashlib
import math
import os
import sys


def main(argv):
    announce = argv[1]
    filename = argv[2]
    piece_length = 2 ** int(argv[3])
    length = os.path.getsize(filename)

    data = {
        'announce': announce.encode('ascii'),
        'info': {
            'length': length,
            'name': filename.encode('ascii'),
            'piece length': piece_length,
            'pieces': b'',
        },
    }

    with open(filename, 'rb') as f:
        piece = f.read(piece_length)
        while len(piece) > 0:
            data['info']['pieces'] += hashlib.sha1(piece).digest()
            piece = f.read(piece_length)

    bencode.dump(data, open(filename + '.torrent', 'wb'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

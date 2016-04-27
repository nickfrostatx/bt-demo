import bencode
import sys
import util


def main(argv):
    data = bencode.load(open(sys.argv[1], 'rb'))
    print(util.pretty_format(data))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[0]))

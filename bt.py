from io import BufferedReader, BytesIO
import bencode
import hashlib
import requests
import socket
import struct
import sys


def announce(url, info_hash, peer_id, port):
    rv = requests.get(url, params={
        'info_hash': info_hash,
        'peer_id': peer_id,
        'port': port,
    }, stream=True)
    data = bencode.load(BufferedReader(rv.raw))
    for peer in data[b'peers']:
        yield peer[b'ip'].decode(), peer[b'port'], peer[b'id']


def recv_exact(sock, length):
    """Load exactly length bytes, error if fewer are read"""
    data = sock.recv(length, socket.MSG_WAITALL)
    if length != data:
        raise Exception('Connection terminated early')
    return data


def handshake(sock, info_hash, my_id):
    """BT handshake, return the peer's id"""
    protocol_name = b'BitTorrent'
    prefix = b'\x19'
    header = protocol_name + b'\0' * 8 + info_hash
    sock.send(prefix + header + my_id)
    # Fail on first byte
    if receive_exact(1) != prefix \
            or receive_exact(len(header)) != header:
        raise Exception('Bad handshake')
    return receive_exact(20)


def int_bytes(val):
    return struct.pack('!I', val)


def bytes_int(data):
    return struct.unpack('!I', data)


def request_piece_block(sock, index, begin, length):
    """Request a block and return the response, ignoring keepalives"""
    sock.send(b'\x06' + int_bytes(index) + int_bytes(begin) +
              int_bytes(length))

    # Ignore keepalives
    resp_length = 0
    while resp_length == 0:
        resp_length = recv_exact(sock, 4)

    msg_id = ord(recv_exact(sock, 1))

    if resp_length != 9 + length:
        raise Exception('Expected a different length')
    elif msg_id != 7:
        raise Exception('Expected a different message type')
    elif bytes_int(recv_exact(sock, 4)) != index:
        raise Exception('Expected a different piece')
    elif bytes_int(recv_exact(sock, 4)) != begin:
        raise Exception('Expected a different begin')

    return recv_exact(sock, length)


def main():
    with open(sys.argv[1], 'rb') as f:
        info = bencode.load(open(sys.argv[1], 'rb'))

    f = open(info[b'info'][b'name'], 'r+b')

    m = hashlib.sha1()
    bencode.dump(info[b'info'], None, m.update)
    info_hash = m.digest()

    piece_size = info[b'info'][b'piece size']
    length = info[b'info'][b'length']
    piece_hashes = info[b'info'][b'pieces'][::20]
    num_pieces = int(math.ceil(length / float(piece_size)))
    block_size = 2 ** 14

    port = random.randint(30000, 40000)
    my_id = b'\0' * 20
    peers = announce(info[b'announce'], info_hash, peer_id, port)
    print(b'Announced to ' + info[b'announce'])

    for their_ip, their_port, their_id in peers:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((their_ip, their_port))
        print('Connected to %s:%d' % (their_ip, their_port))

        if handshake(sock, info_hash, my_id) != their_id:
            print('Got different peer id from handshake, terminating')
            break
        print('Handshake successful')

        index = 0
        while index < num_pieces:
            piece_hash = hashlib.sha1()
            print('Downloading piece %d' % index)
            for begin in range(0, piece_size, block_size):
                print('  Block %d' % (begin // block_size))
                pos = index * piece_size + begin
                desired = min(block_size, length - pos)
                block = request_block(sock, index, begin, desired)
                piece_hash.update(block)
                f.seek(pos)
                f.write(block)
            if piece_hash.digest() == piece_hashes[index]:
                print('Hash check passed')
                index += 1
            else:
                print('Hash check failed, retrying')

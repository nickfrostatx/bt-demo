from flask import Flask, Response, request, abort
from werkzeug import url_decode
import bencode

app = Flask(__name__)
peer_map = {}


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle(exc):
    data = {'failure reason': exc.name.encode('utf-8')}
    return Response(bencode.dumps(data), mimetype='text/plain')


@app.route('/announce')
def announce():
    args = url_decode(request.query_string, None)
    ip = request.remote_addr
    info_hash = args[b'info_hash']
    peer_id = args[b'peer_id']
    try:
        port = int(args[b'port'])
        numwant = int(args.get(b'numwant', b'50'))
    except ValueError:
        abort(400)

    if len(info_hash) != 20 or len(peer_id) != 20:
        abort(400)

    if info_hash not in peer_map:
        peer_map[info_hash] = {
            'complete': set(),
            'incomplete': set(),
            'peers': {},
        }

    peers = []
    for pid in peer_map[info_hash]['peers']:
        if peer != peer_id:
            peer_ip, peer_port = peer_map[info_hash]['peers'][pid]
            peers.append({
                'peer_id': pid,
                'ip': peer_ip.encode('utf-8'),
                'port': peer_port,
            })
        if len(peers) >= numwant:
            break

    if peer_id not in peer_map[info_hash]:
        peer_map[info_hash]['peers'][peer_id] = (ip, port)
        if args[b'left'] == b'0':
            peer_map[info_hash]['complete'].add(peer_id)
            peer_map[info_hash]['incomplete'].discard(peer_id)
        else:
            peer_map[info_hash]['complete'].discard(peer_id)
            peer_map[info_hash]['incomplete'].add(peer_id)

    print('Peers:', peers)

    data = {
        'interval': 1800,
        'peers': peers,
    }

    return Response(bencode.dumps(data), mimetype='text/plain')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

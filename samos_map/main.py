'''
Entry point for a minimal flas application from here.
'''
import os
import sys
# import data
from base64 import b64encode
from flask import Flask, render_template, request, jsonify, session
import kd

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = os.urandom(32)

# handle = data.handler()
# handle.loadkd()
data = kd.Container()


def convlon360(l_360):
    old = l_360
    print(l_360)
    l_360 %= 360
    res = (l_360 - 360) if (l_360 > 180) else l_360

    print('TESTING CONVLON360: {} -> {}'.format(old, res))

    return res

def convlon180(l_180):
    return (l_180 + 360) if (l_180 <= 0) else l_180

@app.route('/data', methods=['GET'])
def dat():
    '''
    stuff
    '''
    if 'id' in session:
        print('GOT SESSION ID: {}'.format(session['id']))

    def pins(bounds):
        lats = (bounds['S'], bounds['N'])
        lons = tuple(map(convlon360, (bounds['W'], bounds['E'])))
        idx = data.bbox(lats, lons, k=10)
        return jsonify(points=[{'lon': d[0], 'lat': d[1], 'idx': str(i)}
            for d, i in zip(data.tree.data[idx], idx)])

    def ancillary(idx):
        return jsonify({key : str(data.data[key][idx])
            for key in ('meta', 'time')})

    if 'idx' in request.args:
        return ancillary(int(request.args['idx']))
    else:
        return pins({card : float(request.args[card])
            for card in ('S', 'N', 'W', 'E')})

@app.route('/', methods=['GET'])
def index():
    '''
    The base web page for the map. We grab the bbox from the user
    using flasks request library (handles the web stuff).
    We execute the data query, and use it to render a response.
    '''
    print('TESTING /:')
    if 'id' in session:
        print('GOT SESSION ID: {}'.format(session['id']))
    else:
        session['id'] = os.urandom(8)
        print('Set a new session ID to {}'.format(session['id']))

    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


# simple unit test for the index
def unittest():
    with app.test_request_context('/', method='POST'):
        assert request.path == '/'
        assert request.method == 'POST'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    conn.close()

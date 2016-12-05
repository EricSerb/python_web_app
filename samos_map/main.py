'''
Entry point for a minimal flas application from here.
'''
import os
import sys
from base64 import b64encode
from flask import Flask, render_template, request, jsonify, session
import kd
import logging

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = os.urandom(32)

data = kd.Container()
log = logging.getLogger('server.log')
log.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
log.setFormatter(fmt)



def convlon360(l_360):
    l_360 %= 360
    return (l_360 - 360) if (l_360 > 180) else l_360

@app.route('/data', methods=['GET'])
def dat():
    '''
    stuff
    '''
    if 'id' in session:
        log.info('user {} active.'.format(session['id']))

    def pins(bounds):
        lats = (bounds['S'], bounds['N'])
        lons = tuple(map(convlon360, (bounds['W'], bounds['E'])))
        idx = data.bbox(lats, lons, k=1000)
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
    if 'id' in session:
        log.info('user {} opended map.'.format(session['id']))
    else:
        session['id'] = os.urandom(8)
        log.info('New session ID {}.'.format(session['id']))
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

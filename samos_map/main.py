'''
Entry point for a minimal flas application from here.
'''
# import sqlite3 as sql
import os
import sys
if __name__ == '__main__':
    import data
else:
    from . import data
from flask import Flask, render_template, request, jsonify, session
from base64 import b64encode
from os import urandom

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = os.urandom(32)

# conn = sql.connect('example.db')
# cur = conn.cursor()
# try:
#     cur.execute('''CREATE TABLE Users
#          (id)''')
#     conn.commit()
# except sql.OperationalError as e:
#     pass


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
    global conn
    print('TESTING /data:')
    if 'id' in session:
        print('GOT SESSION ID: {}'.format(session['id']))


    def request_call():
        handle = data.handler()
        lats, lons = ((request.args['S'], request.args['N']),
                      (request.args['W'], request.args['E']))
        print('request.args[W]: ' + str(request.args['W']))

        print('LATS: {}\nLONS: {}'.format(lats, lons))
        lons = tuple(convlon360(float(l)) for l in lons)

        print('LATS: {}\nLONS: {}'.format(lats, lons))

        data_pnts = handle.spatial(lats, lons, limit=100)
        packed_pnts = handle.extract(data_pnts)
        pnts = []
        for p in packed_pnts:
            lat, lon = handle.loadpoint(p.point)
            pnts.append({'lat': lat, 'lon': lon})
        return pnts

    pnts = request_call()
    return jsonify(points=pnts)

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
'''
Entry point for a minimal flas application from here.
'''
# import sqlite3 as sql
import sys
if __name__ == '__main__':
    import data
else:
    from . import data
from flask import Flask, render_template, request, jsonify
from base64 import b64encode
from os import urandom

app = Flask(__name__)
# conn = sql.connect('example.db')
# cur = conn.cursor()
# try:
#     cur.execute('''CREATE TABLE Users
#          (id)''')
#     conn.commit()
# except sql.OperationalError as e:
#     pass


def convlon360(l_360):
    print(l_360)
    l_360 %= 360
    return (l_360 - 360) if (l_360 > 180) else l_360

def convlon180(l_180):

    return (l_180 + 360) if (l_180 <= 0) else l_180

def gencookie():
    random_bytes = urandom(64)
    return b64encode(random_bytes)


@app.route('/data', methods=['GET'])
def dat():
    '''
    stuff
    '''
    global conn
    print('HI')

    def lookup(user):
        response = cur.execute('''
        SELECT * FROM Users
        WHERE Users.id == {}
        '''.format(user))
        print('~~~~~~~~~~~~~response:', response)
        sys.stdin.readline()
        # conn.commit()
        return True

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

    user_id = request.cookies.get('YourSessionCookie')
    print('user_id:', user_id)
    if user_id:
        # user = lookup(user_id)
        user = False
        if user:
            print('User {} found'.format(user))
            pass
    #
    # else:
    #     try:
    #         request.set_cookie

            # if time
    # print(pnts)
    # pnts = [{'lat':lat, 'lon':lon} for lat, lon in zip(
    #     (10.0, 10.0,  -20.0, 0.0,   0.0,    0.0,    0.0,    0.0,   0.0),
    #     (50.0, -15.0, -15.0, -89.0, -90.0, -179.0, -180.0, -181.0, 178.0))]
    pnts = request_call()
    return jsonify(points=pnts)

@app.route('/', methods=['GET'])
def index():
    '''
    The base web page for the map. We grab the bbox from the user
    using flasks request library (handles the web stuff).
    We execute the data query, and use it to render a response.
    '''
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
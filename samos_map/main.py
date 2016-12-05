"""
Entry point for a minimal flask application from here.
"""
import os
from flask import Flask, render_template, request, jsonify, session
import kd
import logging

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = os.urandom(32)

# Creating the kd tree from all of number of points that we request from solr
data = kd.Container()

"""
Creating a logger in order to log all of out print statements to a file.
"""
log = logging.getLogger('server.log')
log.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
fh = logging.FileHandler('server.log')
fh.setFormatter(fmt)
log.addHandler(fh)
log.info(data.stats())


def convlon360(l_360):
    """
    This function is used to convert the longitude range that solr uses,
    which is 0-360, to the range that open street maps uses, which is -180-180.
    :param l_360: Longitude value
    :return: Longitude value after being converted
    """
    l_360 %= 360
    return (l_360 - 360) if (l_360 > 180) else l_360


@app.route('/data', methods=['GET'])
def dat():
    """
    This method is used to get the points inside of a bounding box.
    This method also returns information about the points if a singular point
    is clicked on the map.
    :return: Points for the map or information about a pin
    """
    if 'id' in session:
        log.info('user {} active.'.format(session['id']))

    def pins(bounds):
        lats = (bounds['S'], bounds['N'])
        lons = tuple(map(convlon360, (bounds['W'], bounds['E'])))
        idx = data.bbox(lats, lons, k=1000)
        return jsonify(points=[{'lon': d[0], 'lat': d[1], 'idx': str(i)
                                }for d, i in zip(data.tree.data[idx], idx)])

    def ancillary(idx):
        return jsonify({key: str(data.data[key][idx])
                        for key in ('meta', 'time')})

    if 'idx' in request.args:
        return ancillary(int(request.args['idx']))
    else:
        return pins({card: float(request.args[card])
                    for card in ('S', 'N', 'W', 'E')})


@app.route('/', methods=['GET'])
def index():
    """
    The base web page for the map. We grab the bbox from the user
    using flasks request library (handles the web stuff).
    We execute the data query, and use it to render a response.
    """
    if 'id' in session:
        log.info('user {} opened map.'.format(session['id']))
    else:
        session['id'] = os.urandom(8)
        log.info('New session ID {}.'.format(session['id']))
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(error):
    """
    This is an error handler incase the user tries to access a page that we
    do not have.
    :param error: the url of the web page trying to be accessed
    :return: 404 page to be displayed
    """
    log.error("Some user tried to access {}".format(error))
    return render_template('page_not_found.html'), 404


# simple unit test for the index
def unittest():
    """
    Tests that the root path that is requested is '/' and the method for it
    is a 'GET' method
    """
    with app.test_request_context('/', method='GET'):
        assert request.path == '/'
        assert request.method == 'GET'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    conn.close()

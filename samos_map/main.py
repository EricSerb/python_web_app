'''
Entry point for a minimal flas application from here.
'''
import sys
from flask import Flask, render_template, request
app = Flask(__name__)

try:
    import data
except ImportError:
    pass # for now

@app.route('/', methods=['GET', 'POST'])
def index():
    '''
    The base web page for the map. We grab the bbox from the user 
    using flasks request library (handles the web stuff).
    We execute the data query, and use it to render a response.
    '''
    #data.test_spatial()
    
    handle = data.handler()
    #Request the bbox returned via ajax and then get data we need for this
    N, S, E, W = 'latitude1', 'latitude2', 'longitude1', 'longitude2'
    data_pts = handle.spatial_query([request.form(i) for i in (N, S, E, W)])
    
    # need to figure out how to confiugre html here
    
    # also, should we limit the number of "transactions" from the user?
    # Like if they scroll in and out really fast... were going to break edge.
    #  maybe not, but we should at least have some sort of breaker / limiter.
    
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


# simple unit test for the index
def unittest():
    with app.test_request_context('/', method='POST'):
        assert request.path == '/'
        assert request.method == 'POST'

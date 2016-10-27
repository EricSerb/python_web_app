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
    #data.test_spatial()
    
    handle = data.handler()
    #Request the bbox returned via ajax and then get data we need for this
    N, S, E, W = 'latitude1', 'latitude2', 'longitude1', 'longitude2'
    data_pts = handle.spatial_query([request.form(i) for i in (N, S, E, W)])
    
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


# simple unit test for the index
def unittest():
    with app.test_request_context('/', method='POST'):
        assert request.path == '/'
        assert request.method == 'POST'

'''
Entry point for a minimal flas application from here.
'''

from flask import Flask, render_template, request
app = Flask(__name__)

#import sys, data

@app.route('/', methods=['GET', 'POST'])
def index():
    #data.test_spatial()
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


# simple unit test for the index
def unittest():
    with app.test_request_context('/', method='POST'):
        assert request.path == '/'
        assert request.method == 'POST'

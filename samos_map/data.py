'''
This module will handle data.
It will be the top level module that uses a database,
kd-tree, clustering, and compression.

These are all the steps necessary before sending the 
client a response containing the necesary information
to populate a web map on their end.
'''

import os
import sys
import time
from urllib import request
import json
import codecs

try:
    scilibs_available = True
    import numpy as np
    from scipy.spatial import cKDTree
    import shapely.wkt as wkt
except ImportError:
    scilibs_available = False
    sys.stderr.write('Warning: Missing scientific libraries.\n' \
        'Please make sure scipy and shapely are installed.\n')
    pass

## DEPRACTAED LIBS .. FOR NOW
# import requests
# import solr

# SOLR_PORT = 8983
# SOLR_ENDPOINT = 'http://localhost:{}/solr/samos'.format(SOLR_PORT)

EDGE_ENDPOINT = 'http://doms.coaps.fsu.edu/ws/search/samos'


class handler(object):
    '''
    Simple handler for now. This will likely be broken down 
    into individual components as more code is added.
    '''
    # global SOLR_ENDPOINT
    # def __init__(self, endpoint=SOLR_ENDPOINT):
    def __init__(self, edge=EDGE_ENDPOINT):
        '''
        Loading 2 endpoints for now, because were not sure which one
        will be used.
        '''
        # trying out multiple data sources
        # solr is localhost only 
        # edge is accessible anywhere
        # self.endpoint = endpoint
        self.edge = edge
        self.edge_params = { 'itemsPerPage' : None, \
            'startIndex' : None, \
            'bbox' : None
        }
        # self.edge_tail = '?itemsPerPage={items}&startIndex={start}&bbox={box}'
        
        
        # try:
            # self.solr = solr.Solr(self.endpoint)
        # except (KeyboardInterrupt, SystemExit) as e:
            # raise e
        # except Exception as e:
            # sys.stderr.write('Error with Solr connection')
            # raise e
    
    
    # def _exec(self, qry):
        # sys.stderr.write('qry: {}'.format(qry))
        # self.solr.SearchHandler(self.solr, '/select')(qry)
    
    
    def load_query(self, items=None, start=None, box=None):
        '''
        Loads parameters from dictionary with query values
        and returns a url string that will be used to retrieve data.
        '''
        self.edge_params['itemsPerPage'] = items
        self.edge_params['startIndex'] = start
        self.edge_params['bbox'] = box
        
        tail = '&'.join('{}={}'.format(k, self.edge_params[k]) \
            for k in self.edge_params if self.edge_params[k] is not None)
        
        if tail:
            qry_str = '?'.join((self.edge, tail))
        else:
            qry_str = self.edge
        
        return qry_str
    
    def spatial_query(self, lats, lons):
        '''
        Handles the execution of querying the solr endpoint with a 
        bounding box representing lat/lon ranges.
        '''
        box = '{},{},{},{}'.format(lons[0], lats[0], lons[1], lats[1])
        start = 0
        items = 100
        
        qry_url = self.load_query(items=items, start=start, box=box)
        response = request.urlopen(qry_url)
        reader = codecs.getreader("utf-8")
        data = json.load(reader(response))
        return data
        ## BELOW IS DEPRACATED RIGHT NOW BUT LEFT FOR FUTURE REFERENCE
        # for x, y in zip(lats, lons):
            # assert -180 < x <= 180 and -90 < y <= 90, "Spatial parameters out of bounds:" \
                # " -180 < x <= 180 and -90 < y <= 90"
        # bbox = [lats, lons].flatten()
        # qry = '{}/select?q=*:*&fq=bounding_box:[{},{} TO {},{}]'
        # return self._exec(qry.format(self.endpoint,
            # lats[0], lats[1], lons[0], lons[1]))
    
    def get_kd(self, response):
        '''
        Given an EDGE response, this will construct a KD tree 
        with that data.
        '''
        global scilibs_available
        if not scilibs_available:
            sys.stderr.write('Warning: data.handler.load_kd() ' \
            'could not be ran because of missing dependency.\n')
            return
        # coords = np.
        n = response['itemsPerPage']
        arr = np.empty((n, 2), dtype=np.float32)
        for i, doc in enumerate(response['results']):
            p = wkt.loads(doc['point'])
            arr[i,:] = p.x, p.y
        return cKDTree(arr)



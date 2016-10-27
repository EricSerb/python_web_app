'''
This module will handle data.
It will be the top level module that uses a database,
kd-tree, clustering, and compression.

These are all the steps necessary before sending the 
client a response containing the necesary information
to populate a web map on their end.
'''

import os
import re
import sys
import time
import json
import codecs
from math import ceil
from collections import Iterable, namedtuple as ntuple

if sys.version_info[0] > 2:
    import urllib.request as urllib
elif sys.version_info[0] < 3:
    import urllib

try:
    scilibs_available = True
    import numpy as np
    from scipy.spatial import cKDTree
except ImportError:
    scilibs_available = False
    sys.stderr.write('Warning: Missing scientific libraries.\n' \
        'Please make sure scipy and shapely are installed.\n')
    pass


EDGE_ENDPOINT = 'http://doms.coaps.fsu.edu/ws/search/samos'


class handler(object):
    '''
    Simple handler for now. This will likely be broken down 
    into individual components as more code is added.
    '''
    def __init__(self, edge=EDGE_ENDPOINT, keys=None):
        '''
        Loading 2 endpoints for now, because were not sure which one
        will be used.
        '''
        self.edge = edge
        self.edge_params = { 'itemsPerPage' : None, \
                             'startIndex' : None, \
                             'bbox' : None
                             }
        self.wktreg = re.compile(r'(\d+(?:\.\d*)?)')
        
        self.datakeys = keys or ('point', 'time')
        assert isinstance(self.datakeys, Iterable)
        
        self.pack = ntuple('pack', ' '.join(self.datakeys))


    def config(self, items=None, start=None, box=None):
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


    def query(self, url):
        if sys.version_info[0] < 3:
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            return data
        elif sys.version_info[0] > 2:
            reader = codecs.getreader('utf-8')
            response = urllib.urlopen(url)
            data = json.load(reader(response))
            return data


    def loadpoint(self, s):
        '''
        My own simple version of shaoply.wkt.loads() so we don't require
        shapely libraries.
        '''
        assert isinstance(s, (str, unicode, bytearray))
        assert s.lower().startswith('point(')
        
        nums = map(float, re.findall(self.wktreg, s))
        return tuple(iter(nums))


    def spatial(self, lats, lons, limit=5000, chunk=1000):
        '''
        Handles the execution of querying the solr endpoint with a
        bounding box representing lat/lon ranges.
        '''
        assert isinstance(limit, int)
        assert isinstance(chunk, int)
        
        box = '{},{},{},{}'.format(lons[0], lats[0], lons[1], lats[1])
        start = 0
        cnt = self.count(box)
        
        n = ceil(cnt / chunk)
        loops = int(min(n, ceil(limit / chunk)) if limit else n)
        
        for _ in range(loops):
            url = self.config(items=chunk, start=start, box=box)
            start += chunk
            yield self.query(url)


    def count(self, box):
        url = self.config(items=0, start=0, box=box)
        page = self.query(url)
        return page['totalResults']


    def extract(self, responses):
        '''
        Given an EDGE response, this will construct a KD tree 
        with that data.
        '''
        global scilibs_available
        assert scilibs_available, 'Warning: data.handler.load_kd() ' \
                             'could not be ran because of missing dependency.'
        
        for chunk in responses:
            for res in chunk['results']:
                yield self.pack(**{k : res[k] for k in self.datakeys})

    def kd(self, packs):
        points, times = zip(*[(self.loadpoint(d.point), d.time) \
            for d in packs])
        n = len(points)
        arr = np.empty((n, 2), dtype=np.float32)
        for i, p in enumerate(points):
            arr[i,:] = p[0], p[1]
        return cKDTree(arr)

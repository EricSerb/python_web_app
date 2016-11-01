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
from sys import stderr as err
import time
import json
import codecs
from datetime import datetime
from math import ceil
from collections import Iterable, namedtuple as ntuple
if sys.version_info[0] > 2:
    import urllib.request as urllib
elif sys.version_info[0] < 3:
    from urllib.error import HTTPError as Httperr
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
                             'bbox' : None, \
                             'startTime' : '2016-01-01T00:00:00Z', \
                             'endTime' : datetime.now().isoformat() + 'Z', \
                             }
        # using this as replacement for shapely.wkt (an annoying dependency)
        self.wktreg = re.compile(r'(\d+(?:\.\d*)?)')

        self.datakeys = keys or ('point', 'time')
        assert isinstance(self.datakeys, Iterable)

        # simple way to structure a datum obj
        self.pack = ntuple('pack', ' '.join(self.datakeys))
        self.last = None
        self.last_cnt = None

    def config(self, items=None, start=None, box=None):
        '''
        Loads parameters from dictionary with query values
        and returns a url string that will be used to retrieve data.
        '''
        # get params
        self.edge_params['itemsPerPage'] = items
        self.edge_params['startIndex'] = start
        self.edge_params['bbox'] = box

        # build restuful url qry string
        tail = '&'.join('{}={}'.format(k, self.edge_params[k]) \
                        for k in self.edge_params if self.edge_params[k] is not None)

        # if no params return base, otherwise the built qry string
        return '?'.join((self.edge, tail)) if tail else self.edge


    def query(self, url):
        '''
        Uses web libraries (urllib, requests, codecs) to run qry url
        and return json data.
        '''
        self.last = url
        try:
            if sys.version_info[0] < 3:
                response = urllib.urlopen(url)
                data = json.loads(response.read())
                return data
            elif sys.version_info[0] > 2:
                reader = codecs.getreader('utf-8')
                response = urllib.urlopen(url)
                data = json.load(reader(response))
                return data
        except Httperr as e:
            err.write('Bad response.')
            print(str(e))

    def loadpoint(self, s):
        '''
        Simple version of shaoply.wkt.loads() so we don't require
        shapely libraries.
        '''
        # assert isinstance(s, (str, bytearray))
        # assert s.lower().startswith('point(')

        nums = map(float, re.findall(self.wktreg, s))
        return reversed(tuple(iter(nums)))


    def spatial(self, lats, lons, limit=5000, chunk=1000):
        '''
        Handles the execution of querying the solr endpoint with a
        bounding box representing lat/lon ranges.
        '''
        assert isinstance(limit, int)
        assert isinstance(chunk, int)

        chunk = min(int(limit / 4), chunk)

        box = '{},{},{},{}'.format(lons[0], lats[0], lons[1], lats[1])
        start = 0
        cnt = self.count(box)
        if cnt < 0:
            err.write('Warning: Count -1\n')
            cnt = 0
        n = ceil(cnt / chunk)
        loops = int(min(n, ceil(limit / chunk)) if limit else n)

        for _ in range(loops + 1):
            url = self.config(items=chunk, start=start, box=box)
            start += chunk
            yield self.query(url)
            if start > limit:
                break


    def count(self, box):
        '''
        We can get a total count from edge without extracting any data.
        Simply set items=0, make the request, and look for 'totalResults'
        in the JSON response.
        '''
        url = self.config(items=0, start=0, box=box)
        print(url)
        page = self.query(url)
        if not page:
            err.write('Page did not load. : {}'.format(os.path.basename(url)))
            self.last_cnt = -1
        else:
            self.last_cnt = page['totalResults']
        return self.last_cnt


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
        '''
        Given an iterable of Pack (namedtuple) items, walk over them
        and pull out data. (For now were just concerned with points)
        '''
        points, times = zip(*[(self.loadpoint(d.point), d.time) \
            for d in packs])
        n = len(points)
        arr = np.empty((n, 2), dtype=np.float32)
        for i, p in enumerate(points):
            arr[i,:] = p[0], p[1]
        return cKDTree(arr)

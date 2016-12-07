import solr
import re
from functools import reduce
from operator import or_
from time import time
import numpy as np
from scipy.spatial import cKDTree
from itertools import product
from math import sqrt
import threading

# This module uses a singleton style object for the KD tree.
# The flask app will check the container until it is ready
# before sending a client the webpage.
lock = threading.Lock()
container = None
ready = False

# this is a monkey patch I used from solrpy/issues/27
# it stops next_batch() from overwriting fields
# and returning all fields after the first call
old_call = solr.core.SearchHandler.__call__


def new_call(self, q=None, fields=None, *args, **params):
    """
    This call is intended to replace solr.core.SearchHandler.__call__.
    The reason for this is that a query resonse object will overwrite
    the fields attribute when calling next_batch(). This degrades
    performance because Solr begins to send all document elements
    after the first batch when we only need the few. Thus we fix the
    function so that we limit the data transfer over the local network
    to speed up initialization.
    """
    fields = params.pop('fl', fields)
    return old_call(self, q, fields, *args, **params)
solr.core.SearchHandler.__call__ = new_call


class Container(object):
    """
    This class contains the methods to get all of the data from solr and
    populate the kd tree and contain that in memory so that main can quickly
    access the data to return to the client.
    """
    def __init__(self, limit=100000):
        global lock, ready
        t = time()
        self.limit = limit
        print('Container using {} limit {}'.format(type(limit), limit))
        self.api = solr.Solr('http://localhost:8983/solr/samos')
        self.wktreg = re.compile(r'[-+]?\d*\.\d+|\d+')
        self.data = None
        self.size, self.total = self._load()
        # python3 version of cKDTree does periodic quick sort
        #  which severely hurts performance on sorted data
        #  -- solr returns semi sorted data usually
        # compact_nodes barely affects performance
        # , compact_nodes=False)
        self.tree = cKDTree(self.data['loc'][:self.total], balanced_tree=False)
        self.loadtime = time() - t
        with lock:
            ready = True

    def _add(self, doc, idx):
        """
        Adding the data to the arrays in memory
        :param doc: The document returned from solr
        :param idx: The index into the array where the information belongs
        """
        self.data['meta'][idx] = str(doc['meta'])
        self.data['time'][idx] = doc['time']
        self.data['loc'][idx][:] = self._convpoint(doc['loc'])

    def _load(self):
        """
        Creates the in memory arrays to store data from solr. Then queries
        solr to obtain all the data we will need for the map.
        :return: number of points returned from all queries
        """
        fields = ['time', 'loc', 'meta']
        query = 'time:[2016-01-01T00:00:00.00Z TO 2017-01-01T00:00:00.00Z]'
        res = self.api.select(q=query, fields=fields, rows=min(1000, self.limit))
        curr, size = 0, res.numFound
        self.data = {key: np.zeros(shape=(size,), dtype=object)
                     for key in ('time', 'meta')}
        self.data['loc'] = np.zeros(shape=(size, 2), dtype=np.float32)

        while res:
            if self.limit and (curr > self.limit):
                break
            i = curr
            for i, doc in enumerate(res, curr):
                if self.limit and i >= self.limit:
                    break
                self._add(doc, i)
            res, curr = res.next_batch(), i + 1
        return size, curr - 1

    def _convpoint(self, pntstr):
        """
        Converting the location string from solr to the lat and lon that will
        be used as a point on the map
        :param pntstr: point string from solr
        :return: (lon, lat)
        """
        nums = map(float, re.findall(self.wktreg, pntstr))
        return tuple(reversed(tuple(iter(nums))))

    def stats(self):
        """
        Creates a string about the data load time
        :return: string
        """
        return 'Loaded {} of {} records in {} s.\n{}'.format(
            self.total, self.size, self.loadtime,
            '\n'.join('\t{}: {} - {}'.format(
                k, type(self.data[k]), self.data[k].shape)
                    for k in self.data))

    def bbox(self, lats, lons, k=5000):
        """
        query n*m points in gridded fashion of the current map view
        to get a better sampling of data points when k is small
        x---x--x---x
        |          |
        x   x  x   x  <--- LIKE THIS
        |          |
        x---x--x---x
        p.s. numpy is awesome
        :param lats: tuple of latitiudes for bounding box
        :param lons: tuple of longitudes for the bounding box
        :param k: the number of points to be returned
        :return: a list of points to be layered onto the map
        """
        X = np.linspace(*lons, num=4, endpoint=True, dtype=np.float32)
        Y = np.linspace(*lats, num=3, endpoint=True, dtype=np.float32)
        r = sqrt(sum((i-j)**2 for i, j in [X[0:2], Y[0:2]])) / 2
        
        qpnts = list(product(X, Y))
        res = self.tree.query(qpnts, k=k, distance_upper_bound=r, n_jobs=-1)[1]
        return list(reduce(or_, map(set, res)) - set([self.total]))

    def nearest(self, lat, lon):
        """
        query the tree with 1 point and get the closest point. Return the meta
        string using the returned index. (Remember, we use parallel arrays)
        :param lat: single latitude
        :param lon: single longitude
        :return: the meta string for the closest point in the tree
        """
        return self.data['meta'][self.tree.query((lon, lat), k=1)[1]]

    def ancillary(self, meta):
        """
        Gets
        :param lat: a meta string representing a SAMOS record
        :return: dictionry of fields and values correlated with the doc
        """
        query = 'meta:{}'.format(meta)
        res = self.api.select(q=query, rows=1)
        doc = None
        for r in res:
            doc = r
        return doc

def init(limit=5000000):
    global container
    print('Initing container in kd module')
    container = Container(limit=limit)

if __name__ == '__main__':
    print(Container().stats())

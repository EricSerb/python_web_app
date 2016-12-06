import solr
import re
from functools import reduce
from operator import or_
from time import time
import numpy as np
from scipy.spatial import cKDTree
from itertools import permutations
from math import sqrt

# this is a monkey patch I used from solrpy/issues/27
# it stops next_batch() from overwriting fields
# and returning all fields after the first call
old_call = solr.core.SearchHandler.__call__


def new_call(self, q=None, fields=None, *args, **params):
    fields = params.pop('fl', fields)
    return old_call(self, q, fields, *args, **params)
solr.core.SearchHandler.__call__ = new_call


class Container(object):
    """
    This class contains the methods to get all of the data from solr and
    populate the kd tree and contain that in memory so that main can quickly
    access the data to return to the client.
    """
    def __init__(self):
        t = time()
        self.api = solr.Solr('http://localhost:8983/solr/samos')
        self.wktreg = re.compile(r'[-+]?\d*\.\d+|\d+')
        self.data = None
        self.size = self._load()
        # python3 version of cKDTree does periodic quick sort
        #  which severely hurts performance on sorted data
        #  -- solr returns semi sorted data usually
        # compact_nodes barely affects performance
        # , compact_nodes=False)
        self.tree = cKDTree(self.data['loc'], balanced_tree=False)
        self.loadtime = time() - t

    def _add(self, doc, idx):
        """
        Adding the data to the arrays in memory
        :param doc: The document returned from solr
        :param idx: The index into the array where the information belongs
        """
        self.data['meta'][idx] = doc['meta']
        self.data['time'][idx] = doc['time']
        self.data['loc'][idx][:] = self._convpoint(doc['loc'])

    def _load(self):
        """
        Creates the in memory arrays to store data from solr. Then queries
        solr to obtain all the data we will need for the map.
        :return: number of points returned from all queries
        """
        fields = ['time', 'loc', 'meta']
        res = self.api.select(q='*:*', fields=fields, rows=1000)
        curr, size = 0, res.numFound
        self.data = {key: np.zeros(shape=(size,), dtype=object)
                     for key in ('time', 'meta')}
        self.data['loc'] = np.zeros(shape=(size, 2), dtype=np.float32)

        while res:
            if curr > 10000:
                break
            i = curr
            for i, doc in enumerate(res, curr):
                self._add(doc, i)
            res, curr = res.next_batch(), i + 1
        return size

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
        return 'Loaded {} records in {} s.\n{}'.format(
            self.size, self.loadtime,
            '\n'.join('\t{}: {} - {}'.format(
                k, type(self.data[k]), self.data[k].shape)
                    for k in self.data))

    def bbox(self, lats, lons, k=100):
        """
        query 2 points in roughly l/r centers of map view
        to get a better sampling of data points when k is small
        ------------
        |          |
        |  x    x  |  <--- LIKE THIS
        |          |
        ------------
        p.s. numpy is awesome
        :param lats: tuple of latitiudes for bounding box
        :param lons: tuple of longitudes for the bounding box
        :param k: the number of points to be returned
        :return: a list of points to be layered onto the map
        """
        X = np.linspace(*lons, num=4, endpoint=False, dtype=np.float32)
        Y = np.linspace(*lats, num=3, endpoint=False, dtype=np.float32)
        max_d = sqrt(sum((i-j)**2 for i, j in zip(X[0:2], Y[0:2]))) / 2
        
        # return list(reduce(or_, [set(self.tree.query(p, k=k)[1])
        #                          for p in ((X[0], Y), (X[1], Y))]))

        def flatten(iterable, lowest_inst=tuple):
            for i in iterable:
                if isinstance(i, lowest_inst):
                    yield i
                else:
                    yield from flatten(i)
        
        qpnts = list(flatten([zip(_x, Y) for _x in permutations(X, len(Y))]))
        res = list(set(flatten(self.tree.query(qpnts, k=k, distance_upper_bound=max_d, n_jobs=-1)[1], lowest_inst=np.int64)))
        
        # res = 
        
        print(res.shape)
        print(res)
        # print(list(flatten([zip(_x, Y)
        #                     for _x in permutations(X, len(Y))])))
        return res
        # return list(reduce(or_, )


if __name__ == '__main__':
    X = np.linspace(*(0.0, 100.0), num=4, endpoint=False)
    Y = np.linspace(*(-100.0, 0.0), num=3, endpoint=False)
    # return list(reduce(or_, [set(self.tree.query(p, k=k)[1])
    #                          for p in ((X[0], Y), (X[1], Y))]))

    def flatten(iterable):
        for i in iterable:
            if isinstance(i, tuple):
                yield i
            else:
                yield from flatten(i)
    
    print(list(flatten([zip(_x, Y)
                        for _x in permutations(X, len(Y))])))

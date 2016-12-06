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
        self.size, self.total = self._load()
        # python3 version of cKDTree does periodic quick sort
        #  which severely hurts performance on sorted data
        #  -- solr returns semi sorted data usually
        # compact_nodes barely affects performance
        # , compact_nodes=False)
        self.tree = cKDTree(self.data['loc'][:self.total], balanced_tree=False)
        self.loadtime = time() - t

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
        res = self.api.select(q=query, fields=fields, rows=1000)
        curr, size = 0, res.numFound
        self.data = {key: np.zeros(shape=(size,), dtype=object)
                     for key in ('time', 'meta')}
        self.data['loc'] = np.zeros(shape=(size, 2), dtype=np.float32)

        while res:
            if curr > 100000:
                break
            i = curr
            for i, doc in enumerate(res, curr):
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
        X = np.linspace(*lons, num=4, endpoint=True, dtype=np.float32)
        Y = np.linspace(*lats, num=3, endpoint=True, dtype=np.float32)
        max_d = sqrt(sum((i-j)**2 for i, j in zip(X[0:2], Y[0:2]))) / 2
        
        # the permutation function returns things in separated groups
        # so this function simply flattens the nested lists down to tuples
        def flatten(iterable):
            for i in iterable:
                if isinstance(i, tuple):
                    yield i
                else:
                    yield from flatten(i)
        
        qpnts = list(flatten([zip(_x, Y) for _x in permutations(X, len(Y))]))
        res = self.tree.query(qpnts, k=k, distance_upper_bound=max_d, n_jobs=-1)[1]
        return list(reduce(or_, map(set, res)) - set([self.total]))


if __name__ == '__main__':
    c = Container()
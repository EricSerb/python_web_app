import solr
import re
import sys
from functools import reduce
from operator import or_
from time import time
import numpy as np
from scipy.spatial import cKDTree

# this is a monkey patch I used from solrpy/issues/27
#  it stops next_batch() from overwriting fields 
#  and returning all fields after the first call
old_call = solr.core.SearchHandler.__call__
def new_call(self, q=None, fields=None, *args, **params):
    fields = params.pop('fl', fields)
    return old_call(self, q, fields, *args, **params)
solr.core.SearchHandler.__call__ = new_call


class Container(object):
    
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
        self.tree = cKDTree(self.data['loc'], balanced_tree=False)#, compact_nodes=False)
        self.loadtime = time() - t

    def _add(self, doc, idx):
        # aw yeh loop unrolling coz im a human compiler
        self.data['meta'][idx] = doc['meta']
        self.data['time'][idx] = doc['time']
        self.data['loc'][idx][:] = self._convpoint(doc['loc'])

    def _load(self):
        fields = ['time', 'loc', 'meta']
        res = self.api.select(q='*:*', fields=fields, rows=1000)
        curr, size = 0, res.numFound
        self.data = { key : np.zeros(shape=(size,), dtype=object)
            for key in ('time', 'meta') }
        self.data['loc'] = np.zeros(shape=(size, 2), dtype=np.float32)

        while res:
            if curr > 1000000: break
            for i, doc in enumerate(res, curr):
                self._add(doc, i)
            res, curr = res.next_batch(), i + 1
        return size

    def _convpoint(self, pntstr):
        nums = map(float, re.findall(self.wktreg, pntstr))
        return tuple(reversed(tuple(iter(nums))))

    def stats(self):
        return 'Loaded {} records in {} s.\n{}'.format(
            self.size, self.loadtime, 
            '\n'.join('\t{}: {} - {}'.format(
                k, type(self.data[k]), self.data[k].shape)
                    for k in self.data))

    def bbox(self, lats, lons, k=100):
        S = set()
        # query 2 points in roughly l/r centers of map view
        # to get a better sampling of data points when k is small
        # ------------
        # |          |
        # |  x    x  |  <--- LIKE THIS
        # |          |
        # ------------
        # p.s. numpy is awesome
        X = np.linspace(*lons, num=4, endpoint=True)[1:3]
        Y = np.linspace(*lats, num=3, endpoint=True)[1]
        return list(reduce(or_, [set(self.tree.query(p, k=k)[1])
            for p in ((X[0], Y), (X[1], Y))]))
        

if __name__ == '__main__':
    KD = Container()
    print(KD.stats(), flush=True)
    if 1:
        print(KD.bbox((40.0, 60.0), (-135.0, -115.0)))



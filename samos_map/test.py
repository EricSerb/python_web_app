'''
Testing suite for the samos map project.
Currenlty contains tests for the data module to ensure
data traffic is handled appropriatly.

All libvraries here are std libs. If any functions require
3rd party libs in the other modules, they are checked 
in that module that the libraries exist. If they do not, 
a warning msg will print, but no error will be thrown. 

Instead it will turn the function into a no-op.
'''

import argparse
import data
import sys
import pprint


def test_qry_loader(show=False):
    '''
    Tests query construction.
    '''
    
    handle = data.handler()
    
    # TEST 1
    qs = handle.config(items=None, start=None, box=None)
    assert qs == data.EDGE_ENDPOINT, 'Query construction failure: {}' \
            '\nExpected: {}'.format(qs, data.EDGE_ENDPOINT)

    if show:
        pprint.pprint(qs)
    
    # TEST 2
    qs = handle.config(items=10, start=10, box='-45,15,-30,30')
    try:
        for sub in \
            'itemsPerPage=10&startIndex=10&bbox=-45,15,-30,30'.split('&'):
            assert sub in qs
    except AssertionError as e:
        sys.stderr.write('\nQuery construction 2 failure: ' + qs \
            + '\nExpected: {}?itemsPerPage=10&startIndex=10' \
            '&bbox=-45,15,-30,30\n\n'.format(data.EDGE_ENDPOINT))
        raise e
    if show:
        pprint.pprint(qs)


def test_qry_executor(show=False):
    handle = data.handler()
    lats = [15, 30]
    lons = [-45, -30]
    res = handle.spatial(lats, lons)
    assert res is not None # Consider beefing this test assertion up
    if show:
        pprint.pprint(res)
    return res # for use below


def test_extraction(show=False):
    handle = data.handler()
    res = test_qry_executor(show)
    kd = handle.kd(handle.extract(res))
    if show and kd is not None:
        print(kd.data)


if __name__ == '__main__':
    '''
    Pass in the following args / flags:
    -v  --verbose   :  show test results
    '''
    p = argparse.ArgumentParser()
    p.add_argument('-v', '--verbose', action='store_true', \
        help='show test results')
    args = p.parse_args()
    
    test_qry_loader(args.verbose)
    test_extraction(args.verbose) # this will call qry_exec
    
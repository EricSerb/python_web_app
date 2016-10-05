# stdlibs
import os, sys, time
import solr

SOLR_PORT = 8983
SOLR_ENDPOINT = 'http://localhost:{}/solr/samos'.format(SOLR_PORT)


class handler(object):
    global SOLR_ENDPOINT
    '''
    '''
    def __init__(self, endpoint=SOLR_ENDPOINT):
        '''
        '''
        try:
            self.endpoint = SOLR_ENDPOINT
            self.solr = solr.Solr(self.endpoint)
        except (KeyboardInterrupt, SystemExit) as e:
            raise e
        except Exception as e:
            sys.stderr.write('Error with Solr connection')
            raise e
    
    def __del__(self):
        '''
        '''
        pass
     
    def spatial_query(self, lats, lons):
        '''
        Handles the execution of querying the solr endpoint with a 
        bounding box representing lat/lon ranges.
        '''
        for x, y in zip(lats, lons):
            assert -180 < x <= 180 and -90 < y <= 90, "Spatial parameters out of bounds:" \
                " -180 < x <= 180 and -90 < y <= 90"
        bbox = [lats, lons].flatten()
        qry = '{}/select?q={}'

def test_spatial():
    handle = handler()
    handle.spatial_query((10.0, 11.0), (20.5, 22.6))
    assert True





if __name__ == '__main__':
    test_spatial()




        




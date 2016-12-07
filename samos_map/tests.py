import unittest
import kd
import requests


class Test(unittest.TestCase):

    con = kd.Container(limit=100)

    def test_vars(self):
        assert Test.con.limit == 100, 'Error, Test.con.limit should have ' \
                                      'been {}'.format(100)
        assert Test.con.loadtime > 0, 'Error, Test.con.loadtime should have ' \
                                      'been {}'.format(0)
        assert Test.con.tree, 'Error, Test.con.tree was empty'
        assert Test.con.size > 0, 'Error, Test.con.size should have ' \
                                  'been {}'.format(0)
        assert Test.con.total > 0, 'Error, Test.con.total should have ' \
                                   'been {}'.format(0)
        assert Test.con.api, 'Error, Test.con.api was empty'
        assert Test.con.data, 'Error, Test.con.data as empty'

    def test_nearest(self):
        assert isinstance(Test.con.nearest(0, 0), str), 'Error, ' \
                                                        'Test.con.limit ' \
                                                        'should have been a ' \
                                                        'string'

    def test_data(self):
        assert len(Test.con.data['time']) == len(Test.con.data['meta']) == \
               len(Test.con.data['loc']), 'Error, Test.con.data[{} and {} ' \
                                          'and {}] were not equal ' \
                                          'length'.format('time', 'meta', 'loc')
        assert Test.con.data['meta'][99], 'Error, Test.con.data["meta"][99] ' \
                                          'is empty'
        assert not Test.con.data['meta'][100], 'Error, ' \
                                               'Test.con.data["meta"][100] ' \
                                               'is empty'

    def test_anc(self):
        anc = Test.con.ancillary(Test.con.data['meta'][99])
        assert isinstance(anc, dict)
        for key in ['meta', 'time', 'loc', 'wind_u', 'wind_v', 'wind_speed',
                    'SSS', 'SST', 'thredds']:
            assert key in anc, 'Error, anc dict missing key {}'.format(key)
        res = requests.get(anc['thredds'])
        assert res.status_code == 200, 'Error hyperlink {} is not ' \
                                       'good'.format(anc['thredds'])

    def test_convpoint(self):
        lat_lon = Test.con._convpoint('50.0440711975, -128.118637085')
        assert isinstance(lat_lon, tuple), 'Error lat_lon should be a tuple'
        assert lat_lon[0] == -128.118637085, 'Error lat_lon[{}] should be ' \
                                             '{}'.format(0, -128.118637085)
        assert lat_lon[1] == 50.0440711975, 'Error lat_lon[{}] should be ' \
                                             '{}'.format(0, 50.0440711975)
        lat_lon = Test.con._convpoint('-50.0440711975, -128.118637085')
        assert isinstance(lat_lon, tuple), 'Error lat_lon should be a tuple'
        assert lat_lon[0] == -128.118637085, 'Error lat_lon[{}] should be ' \
                                             '{}'.format(0, -128.118637085)
        assert lat_lon[1] == -50.0440711975, 'Error lat_lon[{}] should be ' \
                                             '{}'.format(0, -50.0440711975)

    def test_bbox(self):
        pnts = Test.con.bbox((91, -91), (-181, 181))
        assert len(pnts) == Test.con.limit, 'Error, len(pnts) should be ' \
                                            'equal to the limit {}'.format(100)


if __name__ == "__main__":
    unittest.main()

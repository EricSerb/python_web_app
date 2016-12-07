import unittest
import kd
import requests

con = None
lim = None


class Test(unittest.TestCase):

    def test_vars(self):
        assert con.limit == lim, 'Error, con.limit should have ' \
                                      'been {}, was {}'.format(lim,
                                                               con.limit)
        assert con.tree, 'Error, con.tree was empty'
        assert con.size > 0, 'Error, con.size should have ' \
                                  'been greater than {}, was {}'.format(0,
                                                                 con.size)
        assert con.total > 0, 'Error, con.total should have ' \
                                   'been greater than {}, was {}'.format(0,
                                   con.total)
        assert con.api, 'Error, con.api was empty'
        assert con.data, 'Error, con.data was empty'

    def test_nearest(self):
        res = con.nearest(0, 0)
        assert isinstance(res, str), 'Error, con.limit should have been ' \
                                     'a string, was a {}'.format(type(res))

    def test_data(self):
        assert len(con.data['time']) == len(con.data['meta']) == \
               len(con.data['loc']), 'Error, con.data[time and meta' \
                                          ' and loc] were not equal ' \
                                          'length. Lengths were time: {}, ' \
                                          'meta: {}, loc: {}'.format(
                                          len(con.data['time']),
                                          len(con.data['meta']),
                                          len(con.data['loc']))
        assert con.data['meta'][lim-1], 'Error, con.data["meta"][99] ' \
                                          'is empty'
        assert not con.data['meta'][lim], 'Error, con.data["meta"][{}] ' \
                                          'is not empty, contains {}'\
                                          ''.format(lim, con.data['meta'][lim])

    def test_anc(self):
        anc = con.ancillary(con.data['meta'][lim-1])
        assert isinstance(anc, dict)
        for key in ['meta', 'time', 'loc', 'wind_u', 'wind_v', 'wind_speed',
                    'SSS', 'SST', 'thredds']:
            assert key in anc, 'Error, anc dict missing key {}'.format(key)
        res = requests.get(anc['thredds'])
        assert res.status_code == 200, 'Error hyperlink {} is not ' \
                                       'good'.format(anc['thredds'])

    def test_convpoint(self):
        lat_lon = con._convpoint('50.0440711975, -128.118637085')
        assert isinstance(lat_lon, tuple), 'Error lat_lon should be a tuple, ' \
                                           'but it is {}'.format(type(lat_lon))
        assert lat_lon[0] == -128.118637085, 'Error lat_lon[{}] should be ' \
                                             '{}, got {}'.format(
                                             0, -128.118637085, lat_lon[0])
        assert lat_lon[1] == 50.0440711975, 'Error lat_lon[{}] should be ' \
                                            '{}, got {}'.format(
                                            0, 50.0440711975, lat_lon[1])
        lat_lon = con._convpoint('-50.0440711975, -128.118637085')
        assert isinstance(lat_lon, tuple), 'Error lat_lon should be a tuple, ' \
                                           'but it is {}'.format(type(lat_lon))
        assert lat_lon[0] == -128.118637085, 'Error lat_lon[{}] should be ' \
                                             '{}, got {}'.format(
                                             0, -128.118637085, lat_lon[0])
        assert lat_lon[1] == -50.0440711975, 'Error lat_lon[{}] should be ' \
                                             '{}, got {}'.format(
                                             0, -50.0440711975, lat_lon[1])

    def test_bbox(self):
        pnts = con.bbox((91, -91), (-181, 181))
        assert len(pnts) == con.limit, 'Error, len(pnts) should be ' \
                                            'equal to the limit {}, ' \
                                            'got {}'.format(lim, len(pnts))


if __name__ == "__main__":
    for l in [100, 1001, 1999, 2000]:
        con = kd.Container(limit=l)
        lim = l
        unittest.main()

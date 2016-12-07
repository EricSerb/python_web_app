import unittest
import kd
import requests


class Test(unittest.TestCase):

    con = kd.Container(limit=100)

    def test_vars(self):
        assert Test.con.limit == 100
        assert Test.con.loadtime > 0
        assert not isinstance(Test.con.tree, None)
        assert Test.con.size > 0
        assert Test.con.total > 0
        assert not isinstance(Test.con.api, None)
        assert not isinstance(Test.con.data, None)

    def test_nearest(self):
        assert isinstance(Test.con.nearest(0, 0), str)

    def test_data(self):
        assert len(Test.con.data['time']) == len(Test.con.data['meta']) == \
               len(Test.con.data['loc'])
        assert Test.con.data['meta'][99]
        assert not Test.con.data['meta'][100]

    def test_anc(self):
        anc = Test.con.ancillary(Test.con.data['meta'][99])
        assert isinstance(anc, dict)
        for key in ['meta', 'time', 'loc', 'wind_u', 'wind_v', 'wind_speed',
                    'SSS', 'SST', 'thredds']:
            assert key in anc
        res = requests.get(anc['thredds'])
        assert res.status_code == 200

    def test_convpoint(self):
        lat_lon = Test.con._convpoint('50.0440711975, -128.118637085')
        assert isinstance(lat_lon, tuple)
        assert lat_lon[0] == -128.118637085
        assert lat_lon[1] == 50.0440711975
        lat_lon = Test.con._convpoint('-50.0440711975, -128.118637085')
        assert isinstance(lat_lon, tuple)
        assert lat_lon[0] == -128.118637085
        assert lat_lon[1] == -50.0440711975

    def test_bbox(self):
        pnts = Test.con.bbox((91, -91), (-181, 181))
        assert len(pnts) == len(Test.con.limit)


if __name__ == "__main__":
    unittest.main()

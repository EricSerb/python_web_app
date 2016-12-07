import unittest
import kd
import requests


class Test(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.con = kd.Container(limit=100)
        super(self, Test).__init__(*args, **kwargs)

    def test_vars(self):
        assert self.con.limit == 100
        assert self.con.loadtime > 0
        assert not isinstance(self.con.tree, None)
        assert self.size > 0
        assert self.total > 0
        assert not isinstance(self.con.api, None)
        assert not isinstance(self.con.data, None)

    def test_nearest(self):
        assert isinstance(self.con.nearest(0, 0), str)

    def test_data(self):
        assert len(self.con.data['time']) == len(self.con.data['meta']) == \
               len(self.con.data['loc'])
        assert self.con.data['meta'][99]
        assert not self.con.data['meta'][100]

    def test_anc(self):
        anc = self.con.ancillary(self.con.data['meta'][99])
        assert isinstance(anc, dict)
        for key in ['meta', 'time', 'loc', 'wind_u', 'wind_v', 'wind_speed',
                    'SSS', 'SST', 'thredds']:
            assert key in anc
        res = requests.get(anc['thredds'])
        assert res.status_code == 200

    def test_convpoint(self):
        lat_lon = self.con._convpoint('50.0440711975, -128.118637085')
        assert isinstance(lat_lon, tuple)
        assert lat_lon[0] == -128.118637085
        assert lat_lon[1] == 50.0440711975
        lat_lon = self.con._convpoint('-50.0440711975, -128.118637085')
        assert isinstance(lat_lon, tuple)
        assert lat_lon[0] == -128.118637085
        assert lat_lon[1] == -50.0440711975

    def test_bbox(self):
        pnts = self.con.bbox((91, -91), (-181, 181))
        assert len(pnts) == len(self.con.limit)


if __name__ == "__main__":
    unittest.main()

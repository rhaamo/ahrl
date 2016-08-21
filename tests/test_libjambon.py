import sys
sys.path.insert(0, sys.path[0] + '/../')
from geohelper import bearing
from libjambon import coordinates2adif, adif2coordinates, adif, geo_bearing_star
import unittest


class TestLibjambon(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # Latitude
    def test_latitude_pos(self):
        t = [46.3048, 44.5639, 41.9, 56]
        for tt in t:
            a = coordinates2adif(tt, "Latitude")
            b = adif2coordinates(a)
            self.assertAlmostEqual(tt, b)

    def test_latitude_neg(self):
        t = [-26.9861]
        for tt in t:
            a = coordinates2adif(tt, "Latitude")
            b = adif2coordinates(a)
            self.assertAlmostEqual(tt, b)

    # Longitude
    def test_longitude_pos(self):
        t = [10.9409, 12.5]
        for tt in t:
            a = coordinates2adif(tt, "Longitude")
            b = adif2coordinates(a)
            self.assertAlmostEqual(tt, b)

    def test_longitude_neg(self):
        t = [-3.18, -9.01677, -0.12, -8.73333, -8.04333]
        for tt in t:
            a = coordinates2adif(tt, "Longitude")
            b = adif2coordinates(a)
            self.assertAlmostEqual(tt, b, places=5)

    def test_adif(self):
        t = [['notes', 5], ['call', 4], ['foo bar baz', 11]]
        for tt in t:
            a = adif("foo", tt[0])
            self.assertEqual(a, "<FOO:{0}>{1} ".format(tt[1], tt[0]))

    def test_bearing(self):
        # Always lon, lat
        _from = [2.208333333333343, 48.97916666666666]
        to = [[33.54166666666666, 44.64583333333334, 89.5777047195586],
              [-0.5416666666666572, 38.39583333333334, 191.6123173992922],
              [18.125, 42.64583333333334, 113.8162224705103]]
        for tt in to:
            z = bearing.initial_compass_bearing(_from[1], _from[0], tt[1], tt[0])
            self.assertEqual(z, tt[2])

    def test_bearing_star(self):
        # Always lon, lat
        _from = [2.208333333333343, 48.97916666666666]
        to = [[33.54166666666666, 44.64583333333334, "E"],
              [-0.5416666666666572, 38.39583333333334, "SW"],
              [18.125, 42.64583333333334, "SE"]]
        for tt in to:
            z = bearing.initial_compass_bearing(_from[1], _from[0], tt[1], tt[0])
            a = geo_bearing_star(z)
            self.assertEqual(a, tt[2])
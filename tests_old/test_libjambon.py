import sys

sys.path.insert(0, sys.path[0] + "/../")
from geohelper import bearing  # noqa: E402
from libjambon import coordinates2adif, adif2coordinates, adif, geo_bearing_star  # noqa: E402
import unittest  # noqa: E402
from parameterized import parameterized  # noqa: E402


class TestLibjambon(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # Latitude
    @parameterized.expand([(46.3048,), (44.5639,), (41.9,), (56,)])
    def test_latitude_pos(self, pos):
        a = coordinates2adif(pos, "Latitude")
        b = adif2coordinates(a)
        self.assertAlmostEqual(pos, b)

    @parameterized.expand([(-26.9861,)])
    def test_latitude_neg(self, pos):
        a = coordinates2adif(pos, "Latitude")
        b = adif2coordinates(a)
        self.assertAlmostEqual(pos, b)

    # Longitude
    @parameterized.expand([(10.9409,), (12.5,)])
    def test_longitude_pos(self, pos):
        a = coordinates2adif(pos, "Longitude")
        b = adif2coordinates(a)
        self.assertAlmostEqual(pos, b)

    @parameterized.expand([(-3.18,), (-9.01677,), (-0.12,), (-8.73333,), (-8.04333,)])
    def test_longitude_neg(self, pos):
        a = coordinates2adif(pos, "Longitude")
        b = adif2coordinates(a)
        self.assertAlmostEqual(pos, b, places=5)

    @parameterized.expand([("notes", 5), ("call", 4), ("foo bar baz", 11)])
    def test_adif(self, value, size):
        a = adif("foo", value)
        self.assertEqual(a, "<FOO:{0}>{1} ".format(size, value))

    @parameterized.expand(
        [
            (33.54166666666666, 44.64583333333334, 89.5777047195586),
            (-0.5416666666666572, 38.39583333333334, 191.6123173992922),
            (18.125, 42.64583333333334, 113.8162224705103),
        ]
    )
    def test_bearing(self, lon, lat, bear):
        # Always lon, lat
        _from = [2.208333333333343, 48.97916666666666]
        z = bearing.initial_compass_bearing(_from[1], _from[0], lat, lon)
        self.assertEqual(z, bear)

    @parameterized.expand(
        [
            (33.54166666666666, 44.64583333333334, "E"),
            (-0.5416666666666572, 38.39583333333334, "SW"),
            (18.125, 42.64583333333334, "SE"),
        ]
    )
    def test_bearing_star(self, lon, lat, bear):
        # Always lon, lat
        _from = [2.208333333333343, 48.97916666666666]
        z = bearing.initial_compass_bearing(_from[1], _from[0], lat, lon)
        a = geo_bearing_star(z)
        self.assertEqual(a, bear)

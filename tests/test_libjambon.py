from geohelper import bearing
from libjambon import coordinates2adif, adif2coordinates, adif, geo_bearing_star
from parameterized import parameterized
import pytest


# Latitude
@parameterized.expand([(46.3048,), (44.5639,), (41.9,), (56,)])
def test_latitude_pos(pos):
    a = coordinates2adif(pos, "Latitude")
    b = adif2coordinates(a)
    assert b == pytest.approx(pos)


@parameterized.expand([(-26.9861,)])
def test_latitude_neg(pos):
    a = coordinates2adif(pos, "Latitude")
    b = adif2coordinates(a)
    assert b == pytest.approx(pos)


# Longitude
@parameterized.expand([(10.9409,), (12.5,)])
def test_longitude_pos(pos):
    a = coordinates2adif(pos, "Longitude")
    b = adif2coordinates(a)
    assert b == pytest.approx(pos)


@parameterized.expand([(-3.18,), (-9.01677,), (-0.12,), (-8.73333,), (-8.04333,)])
def test_longitude_neg(pos):
    a = coordinates2adif(pos, "Longitude")
    b = adif2coordinates(a)
    assert b == pytest.approx(pos, rel=5)


@parameterized.expand([("notes", 5), ("call", 4), ("foo bar baz", 11)])
def test_adif(value, size):
    a = adif("foo", value)
    assert a == "<FOO:{0}>{1} ".format(size, value)


@parameterized.expand(
    [
        (33.54166666666666, 44.64583333333334, 89.5777047195586),
        (-0.5416666666666572, 38.39583333333334, 191.6123173992922),
        (18.125, 42.64583333333334, 113.81622247051024),
    ]
)
def test_bearing(lon, lat, bear):
    # Always lon, lat
    _from = [2.208333333333343, 48.97916666666666]
    z = bearing.initial_compass_bearing(_from[1], _from[0], lat, lon)
    assert z == bear


@parameterized.expand(
    [
        (33.54166666666666, 44.64583333333334, "E"),
        (-0.5416666666666572, 38.39583333333334, "SW"),
        (18.125, 42.64583333333334, "SE"),
    ]
)
def test_bearing_star(lon, lat, bear):
    # Always lon, lat
    _from = [2.208333333333343, 48.97916666666666]
    z = bearing.initial_compass_bearing(_from[1], _from[0], lat, lon)
    a = geo_bearing_star(z)
    assert a == bear

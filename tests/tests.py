from libjambon import adif_coordinate, coordinates_adif
a = adif_coordinate(-0.0401757, "Longitude")
b = adif_coordinate(4.11116, "Longitude")

c = adif_coordinate(-26.9861, "Latitude")
d = adif_coordinate(46.3048, "Latitude")

a1 = coordinates_adif(a)
b1 = coordinates_adif(b)

c1 = coordinates_adif(c)
d1 = coordinates_adif(d)

print("[LON] -0.0401757; a: {0}; a1: {1}".format(a, a1))
print("[LON] 4.11116; b: {0}; b1: {1}".format(b, b1))
print("[LAT] -26.9861; c: {0}; a1: {1}".format(c, c1))
print("[LAT] 46.3048; d: {0}; d1: {1}".format(d, d1))

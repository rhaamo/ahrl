import sys
sys.path.insert(0, sys.path[0] + '/../')
from utils import gen_random_str
import unittest


class TestUtils(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_gen_random_str(self):
        z = 0
        while True:
            a = gen_random_str(20)
            b = gen_random_str(20)
            self.assertNotEqual(a, b)
            z += 1
            if z >= 100:
                break

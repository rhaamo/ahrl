from utils import gen_random_str


def test_gen_random_str():
    times = 0
    while True:
        a = gen_random_str(20)
        b = gen_random_str(20)
        assert a != b
        times += 1
        if times >= 100:
            break

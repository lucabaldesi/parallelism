import os

import parallelism as pll


def dummiest_worker(i):
    pass


def crashing_worker(i):
    1/0


def dummy_worker(i):
    print(f"{i}")
    return i**2


def test_launch_workers():
    inp = [dict(i=1), dict(i=2), dict(i=3), dict(i=4)]

    res = pll.launch_workers([], dummiest_worker)
    assert(sorted(res) == [])

    res = pll.launch_workers(inp, dummiest_worker)
    assert(res == [None, None, None, None])

    res = pll.launch_workers(inp, dummy_worker)
    assert(sorted(res) == [1, 4, 9, 16])

    res = pll.launch_workers(inp, dummy_worker, inputs_per_worker=1)
    assert(sorted(res) == [1, 4, 9, 16])

    filename = "/tmp/testparallelismpy"
    if os.path.isfile(filename):
        os.remove(filename)
    with open(filename, "w") as f:
        res = pll.launch_workers(inp, dummy_worker, inputs_per_worker=1,
                                outfile=f)

    assert(sorted(res) == [1, 4, 9, 16])
    with open(filename, "r") as f:
        assert(sorted(f.readlines()) ==
               ["1\n", "2\n", "3\n", "4\n"])
    os.remove(filename)


def test_crahses():
    inp = [dict(i=1), dict(i=2), dict(i=3), dict(i=4)]
    res = pll.launch_workers(inp, crashing_worker, inputs_per_worker=1, parallelism=2)
    assert(res == [])

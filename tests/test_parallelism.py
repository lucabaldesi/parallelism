import os

import parallelism as pll


def dummiest_worker(inputlist, outqueue, printqueue):
    pass


def crashing_worker(inputlist, outqueue, printqueue):
    outqueue.put(1)
    1/0
    outqueue.put(2)


def dummy_worker(inputlist, outqueue, printqueue):
    for i in inputlist:
        outqueue.put(i**2)
        if printqueue:
            printqueue.put(str(len(inputlist)) + "-" + str(i) + " ")


def test_launch_workers():
    inp = [1, 2, 3, 4]

    res = pll.launch_workers([], dummiest_worker)
    assert(sorted(res) == [])

    res = pll.launch_workers(inp, dummiest_worker)
    assert(sorted(res) == [])

    res = pll.launch_workers(inp, dummy_worker)
    assert(sorted(res) == [1, 4, 9, 16])

    res = pll.launch_workers(inp, dummy_worker, inputs_per_worker=1)
    assert(sorted(res) == [1, 4, 9, 16])

    filename = "/tmp/testparallelismpy"
    if os.path.isfile(filename):
        os.remove(filename)
    res = pll.launch_workers(inp, dummy_worker, inputs_per_worker=1,
                             outfile=filename)
    assert(sorted(res) == [1, 4, 9, 16])
    with open(filename) as f:
        assert(sorted(f.readline().split(" ")) ==
               ["", "1-1", "1-2", "1-3", "1-4"])
    os.remove(filename)

    filename = "/tmp/testparallelismpy"
    if os.path.isfile(filename):
        os.remove(filename)
    res = pll.launch_workers(inp, dummy_worker, inputs_per_worker=3,
                             outfile=filename)
    assert(sorted(res) == [1, 4, 9, 16])
    with open(filename) as f:
        assert(sorted(f.readline().split(" ")) ==
               ["", "1-4", "3-1", "3-2", "3-3"])
    os.remove(filename)


def test_stakanovs():
    inp = [1, 2, 3, 4]

    filename = "/tmp/testparallelismpy"
    if os.path.isfile(filename):
        os.remove(filename)
    res = pll.stakanovs(inp, dummy_worker, outfile=filename)
    assert(sorted(res) == [1, 4, 9, 16])
    with open(filename) as f:
        assert(sorted(f.readline().split(" ")) ==
               ["", "1-1", "1-2", "1-3", "1-4"])
    os.remove(filename)

    filename = "/tmp/testparallelismpy"
    if os.path.isfile(filename):
        os.remove(filename)
    res = pll.stakanovs(inp, dummy_worker, parallelism=2, outfile=filename)
    assert(sorted(res) == [1, 4, 9, 16])
    with open(filename) as f:
        assert(sorted(f.readline().split(" ")) ==
               ["", "2-1", "2-2", "2-3", "2-4"])
    os.remove(filename)

    filename = "/tmp/testparallelismpy"
    if os.path.isfile(filename):
        os.remove(filename)
    res = pll.stakanovs(inp, dummy_worker, parallelism=3, outfile=filename)
    assert(sorted(res) == [1, 4, 9, 16])
    with open(filename) as f:
        assert(sorted(f.readline().split(" ")) ==
               ["", "2-1", "2-2", "2-3", "2-4"])
    os.remove(filename)


def test_crahses():
    inp = [1, 2, 3, 4]
    res = pll.launch_workers(inp, crashing_worker, inputs_per_worker=1, parallelism=2)
    assert(sorted(res) == [1]*4)

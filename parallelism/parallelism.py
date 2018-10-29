#    Copyright (C) 2016 Luca Baldesi
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Allows launching functions in parallel, executing on different processes"""

import math
import time
import multiprocessing as mp
import sys


def broadcasting_wrapper(input_list, func, outqueue, printer):
    times = []
    sys.stdout = printer
    for e in input_list:
        times.append(func(**e))
    for t in times:
        outqueue.put(t)


class Printer(object):
    def __init__(self, outfile, print_queue):
        self.outfile = outfile
        self.print_queue = print_queue
        self.running = True

    def write(self, s):
        if self.running:
            self.print_queue.put(s)

    def waterfall(self):
        while self.running or self.print_queue.qsize() > 0:
            if self.print_queue.qsize() > 0:
                m = self.print_queue.get()
                if self.outfile:
                    self.outfile.write(str(m))
                    self.outfile.flush()
                else:
                    print(str(m))

    def close(self):
        self.running = False


def launch_workers(input_list, func, parallelism=4, inputs_per_worker=1000,
                   outfile=None):
    """Launch several parallel process executing a specified function

    Parameters
    ----------
    input_list: list
        List with input data for the function, given as a dictionary of
        parameter values.
    func: function
        The job worker, it has to accept the input_list parameter values
    parallelism: integer
        Maximum number of process to start as workers
    inputs_per_worker: integer
        Number of elements of input_list to be passed to each function instance
    outfile:
        Object implementing write() and flush() methods. If func prints
        something and outfile is defined, then output is redirected to outfile.

    Returns
    -------
        list with all the returned values

    Examples
    --------
    >>> import parallelism as pll
    >>> def dummy(a):
    ...:    return 1
    ...:
    >>> pll.launch_workers([dict(a=5), dict(a=3)], dummy)
        [1, 1]
    """
    queue = mp.Queue()
    procList = []
    outList = []
    deadProc = []
    print_queue = mp.Queue()

    printer = Printer(outfile, print_queue)
    printer_proc = mp.Process(target=printer.waterfall, args=())
    printer_proc.start()

    while len(input_list):
        # if somenthing ended, collect the result
        for p in procList:
            if not p.is_alive():
                p.join()
                deadProc.append(p)
        for p in deadProc:
            procList.remove(p)
        deadProc = []

        # if we can launch a process, start it
        if len(input_list) > 0 and len(procList) < parallelism:
            feed = input_list[:inputs_per_worker]
            input_list = input_list[inputs_per_worker:]
            p = mp.Process(target=broadcasting_wrapper, args=(
                feed, func, queue, printer))
            procList.append(p)
            p.start()

    # wait for working processes
    for p in procList:
        p.join()

    time.sleep(1)
    printer_proc.terminate()
    printer_proc.join()

    while not queue.empty():
        outList.append(queue.get())

    return outList


def stakanovs(input_list, func, parallelism=4, outfile=None):
    """
    Same as launch_workers but automatically assigning the maximum number of
    inputs to each worker (inputs_per_worker=len(input_list)/parallelism)
    """
    return launch_workers(input_list, func, parallelism,
                          int(math.ceil(len(input_list)/float(parallelism))),
                          outfile)


def minions(input_list, func, parallelism=4, outfile=None):
    """
    Same as launch_workers but automatically assigning only one input to each
    worker (inputs_per_worker=1)
    """
    return launch_workers(input_list, func, parallelism, 1, outfile)

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


def _printer(outfile, print_queue):
    with open(outfile, "a") as f:
        while 1:
            m = print_queue.get()
            f.write(str(m))
            f.flush()


def launch_workers(input_list, func, parallelism=4, inputs_per_worker=1000,
                   outfile=None):
    """Launch several parallel process executing a specified function

    Parameters
    ----------
    input_list: list
        List with input data for the function
    func: function
        The worker function; it has to accept as input a list and a queue.
        The list is used to pass the actual input, a fraction of input_list, the
        queue is the mean used by the func to return values (using queue.put())
    parallelism: integer
        maximum number of process to start as workers
    inputs_per_worker: integer
        number of elements of input_list to be passed to each function instance

    Returns
    -------
        list with all the returned values
    """
    queue = mp.Queue()
    procList = []
    outList = []
    deadProc = []
    print_queue = None

    if outfile:
        print_queue = mp.Queue()
        printer_proc = mp.Process(target=_printer, args=(outfile, print_queue))
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
            p = mp.Process(target=func, args=(feed, queue, print_queue))
            procList.append(p)
            p.start()

    # wait for working processes
    for p in procList:
        p.join()

    if outfile:
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

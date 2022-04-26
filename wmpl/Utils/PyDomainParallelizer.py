from __future__ import print_function

import multiprocessing
import sys
import time
from contextlib import closing
from functools import partial


def parallelComputeGenerator(
    generator, workerFunc, resultsCheckFunc, req_num, n_proc=None, results_check_kwagrs=None, max_runs=None
):
    """ Given a generator which generates inputs for the workerFunc function, generate and process results 
        until req_num number of results satisfies the resultsCheckFunc function.

    Arguments:
        generator: [generator] Generator function which creates inputs for the workerFunc. It should
            return a list of arguments that will be fed into the workerFunc.
        workerFunc: [function] Worker function.
        resultsCheckFunc: [function] A function which takes a lists of results and returns only those which
            satisfy some criteria.
        req_num: [int] Number of good results required. A good results is the one that passes the 
            resultsCheckFunc check.

    Keyword arguments:
        n_proc: [int] Number of processes to use. None by default, in which case all available processors
            will be used.
        results_check_kwargs: [dict] Keyword arguments for resultsCheckFunc. None by default.
        max_runs: [int] Maximum number of runs. None by default, which will limit the runs to 10x req_num.

    Return:
        [list] A list of results.
    """

    # If the number of processes was not given, use all available CPUs
    if n_proc is None:
        n_proc = multiprocessing.cpu_count()

    if results_check_kwagrs is None:
        results_check_kwagrs = {}

    # Limit the maxlimum number or runs
    if max_runs is None:
        max_runs = 10 * req_num

    # Init the pool
    with multiprocessing.Pool(processes=n_proc) as pool:

        results = []

        total_runs = 0

        # Generate an initial input list
        input_list = [next(generator) for i in range(req_num)]

        # Run the initial list
        results = pool.map(workerFunc, input_list)

        total_runs += len(input_list)

        # Only take good results
        results = resultsCheckFunc(results, **results_check_kwagrs)

        # If there are None, do not continue, as there is obviously a problem
        if len(results) == 0:
            print("No successful results after the initial run!")
            return results

        # Run the processing until a required number of good values is returned
        while len(results) < req_num:

            # Generate an input for processing
            input_list = [next(generator) for i in range(n_proc)]

            # Map the inputs
            results_temp = pool.map(workerFunc, input_list)

            total_runs += len(input_list)

            # Only take good results
            results += resultsCheckFunc(results_temp, **results_check_kwagrs)

            # Check if the number of runs exceeded the maximum
            if total_runs >= max_runs:
                print("Total runs exceeded! Stopping...")
                break

        # Make sure that there are no more results than needed
        if len(results) > req_num:
            results = results[:req_num]

        return results


def unpackDecorator(func):
    def dec(args):
        return func(*args)

    return dec


def formatTime(t):
    """ Converts time in seconds to a string with hours, minutes and seconds """
    return f'{int(t//3600):2d}h {(int(t//60))%60:2d}m {t%60:5.2f}s'


def domainParallelizer(domain, function, cores=None, kwarg_dict=None, display=False):
    """ Runs N (cores) functions as separate processes with parameters given in the domain list.

    Arguments:
        domain: [list] a list of separate data (arguments) to feed individual function calls
        function: [function object] function that will be called with one entry from the domain
    
    Keyword arguments:
        cores: [int] Number of CPU cores, or number of parallel processes to run simultaneously. None by 
            default, in which case all available cores will be used.
        kwarg_dict: [dictionary] a dictionary of keyword arguments to be passed to the function, None by default
        display: [bool] Whether to display progress every 100 items in the domain

    Return:
        results: [list] a list of function results

    """
    t1 = time.perf_counter()

    def _logResult(result, counter=[0]):
        """ Save the result from the async multiprocessing to a results list.
        
        keyword arguments:
            counter: [list] tracks the amount that the function has been called 
                (jank but easy and is functionally perfect)
        """
        counter[0] += 1
        total = len(domain)
        if counter[0] % 100 == 99 and display:
            now = time.perf_counter()
            print(
                " " * (len(str(total)) - len(str(counter[0])))
                + f'{counter[0]}/{total}: {counter[0]/total*100:5.2f}% computed  -  '
                f'Time: {formatTime(now - t1)}  -  '
                f'ETA: {formatTime((now - t1)/counter[0]*(total - counter[0]))}',
                end='\r',
            )

    if kwarg_dict is None:
        kwarg_dict = {}

    # If the number of cores was not given, use all available cores
    if cores is None:
        cores = multiprocessing.cpu_count()

    # Special case when running on only one core, run without multiprocessing
    if cores == 1:
        for i, args in enumerate(domain):
            results = [function(*args, **kwarg_dict)]

    # Run real multiprocessing if more than one core
    elif cores > 1:

        # Generate a pool of workers
        with closing(multiprocessing.Pool(cores)) as pool:
            results = pool.starmap_async(partial(function, **kwarg_dict), domain, callback=_logResult)

        pool.join()

    else:
        raise ValueError(
            'The number of CPU cores defined is not in an expected range (1 or more.) '
            'Use cpu_cores = 1 as a fallback value.'
        )

    return results.get()


##############################
## USAGE EXAMPLE


def mpWorker(inputs, wait_time, kwarg=0):
    """ Example worker function. This function will print out the name of the worker and wait 'wait_time
        seconds. 

    """

    print(" Processs %s\tWaiting %s seconds. Argument %d" % (inputs, wait_time, kwarg))

    time.sleep(int(wait_time))

    print(f" Process {inputs}\tDONE")

    # Must use if you want print to be visible on the screen!
    sys.stdout.flush()

    return int(wait_time)


if __name__ == '__main__':

    # List of function arguments for every run
    data = [['a', '2'], ['b', '4'], ['c', '6'], ['d', '8'], ['e', '1'], ['f', '3'], ['g', '5'], ['h', '7']]

    # Get the number of cpu cores available
    cpu_cores = multiprocessing.cpu_count()

    # Run the parallelized function
    results = domainParallelizer(data, mpWorker, cores=(cpu_cores - 1), kwarg_dict={'kwarg': 3})

    print('Results:', results)


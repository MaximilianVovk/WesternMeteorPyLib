""" Preprocess the simulations before feeding them into the neural network. """

from __future__ import print_function, division, absolute_import, unicode_literals


import os
import random

import numpy as np

from wmpl.MetSim.ML.GenerateSimulations import MetParam, ErosionSimContainer, ErosionSimParametersCAMO, \
    extractSimData
from wmpl.Utils.Pickling import loadPickle
from wmpl.Utils.PyDomainParallelizer import domainParallelizer


def validateSimulation(data_path, file_name, min_frames_visible):

    # Load the pickle file
    sim = loadPickle(data_path, file_name)

    # Extract simulation data
    res = extractSimData(sim, min_frames_visible=min_frames_visible, check_only=True)

    # If the simulation didn't satisfy the filters, skip it
    if res is None:
        return None


    print("Good:", file_name)

    return file_name, res


def postprocessSims(data_path, min_frames_visible=10):
    """ Preprocess simulations generated by the ablation model to prepare them for training. 
    
    From all simulations, make fake observations by taking only data above the limiting magnitude and
    add noise to simulated data.

    Arguments:
        dir_path:
        output_dir:

    """

    # Go through all simulations and create a list for processing
    processing_list = []
    for file_name in os.listdir(data_path):

        file_path = os.path.join(data_path, file_name)

        # Check if the given file is a pickle file
        if os.path.isfile(file_path) and file_name.endswith(".pickle"):

            processing_list.append([data_path, file_name, min_frames_visible])



    # Validate simulation (parallelized)
    print("Starting postprocessing in parallel...")
    results_list = domainParallelizer(processing_list, validateSimulation)

    # Reject all None's from the results
    good_list = [entry for entry in results_list if entry is not None]

    # Randomize the list
    random.shuffle(good_list)

    # Load one simulation to get simulation parameters
    sim = loadPickle(data_path, good_list[0][0])

    # Compute the average minimum time the meteor needs to be visible
    min_time_visible = min_frames_visible/sim.params.fps \
        + (sim.params.len_delay_min + sim.params.len_delay_max)/2

    # Save the list of good files to disk
    good_list_file_name = "lm{:+04.1f}_mintime{:.3f}s_good_files.txt".format( \
        (sim.params.lim_mag_faintest + sim.params.lim_mag_brightest)/2, min_time_visible)

    with open(os.path.join(data_path, good_list_file_name), 'w') as f:

        # Write header
        f.write("# File name, lim mag, lim mag length, length delay (s)")

        # Write entries
        for file_name, random_params in good_list:
            f.write("{:s}, {:.8f}, {:.8f}, {:.8f}\n".format(file_name, *random_params))

    print("{:d} entries saved to {:s}".format(len(good_list), good_list_file_name))





if __name__ == "__main__":

    import argparse


    ### COMMAND LINE ARGUMENTS

    # Init the command line arguments parser
    arg_parser = argparse.ArgumentParser(description="Check that the simulations in the given directory satisfy the given conditions and create a file with the list of simulation to use for training.")

    arg_parser.add_argument('dir_path', metavar='DIR_PATH', type=str, \
        help="Path to the directory with simulation pickle files.")

    # Parse the command line arguments
    cml_args = arg_parser.parse_args()

    #########################

    # Postprocess simulations
    postprocessSims(cml_args.dir_path)
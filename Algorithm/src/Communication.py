

# Import libraries:
import pandas as pd
import os
import random
from param import parameters
from SimulationEnv import Simulation


# Parameters

# Classes

# Functions

def read_results():
    """
    Function to read FlexSim results csv file
    """
    out_f_name = "statcol.csv"
#    results = pd.read_csv(ver+"/"+out_f_name, sep=';', decimal=',')
    results = pd.read_csv(out_f_name)
    print(results)
    return results


def print_out(*msg):
    """
    Function to write to an external file (log)
    """
    print(*msg)
    file = r"_output.txt"
    with open(file, "a+") as f:
        # f.write(msg+"\r\n")
        for i in msg:
            f.write(str(i))
        f.write("\n")


def clear_output_file():
    """
    Function to remove external file (log)
    """
    try:
        os.remove(r"_output.txt")
    except OSError:
        pass


if __name__ == "__main__":

    param = parameters()

    #seed = random.randint(1, 100)
    Input_file = "New Model/LocationToGo.csv"
    simu = Simulation(param, Input_file)

    # Choose solution algorithm:
    simu.run_simulation()
    results = read_results()

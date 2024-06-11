import pandas as pd
import random
import os
from aux_functions import read_tests, read_instance ,printSolution, solution_to_dataframe
from Solver import SimHeuristic
from param import parameters

# Read tests from the file
tests = read_tests("Sim_Algorithm3/tests/test2run.txt")
#cost = 0
#stochastic_cost = 0

for test in tests:
    random.seed(test.seed) # Python default RNG, used during BR
    print('\nInstance: ', test.instanceName)
    #print('Var level (k in Var = k*mean):', test.varLevel)
    # Read input data from instance file
    file_name = "Sim_Algorithm3/data" + os.sep + test.instanceName + ".txt"
    fleetSize, routeMaxCost, nodes = read_instance(file_name)
    param = parameters()

    OBD, OBS = SimHeuristic(test, fleetSize, routeMaxCost, nodes)


    # Print summary results
    print('Cost for OBD sol in a Det. env. =', OBD.cost)
    print('Reward for OBD sol in a Det. env. =', OBD.reward)
    print('Cost for OBD sol in a stoch. env. =', OBD.stochastic_cost)

    print('Reward for OBD sol in a Stoch. env. =', OBD.reward_sim)
    print('Cost for OBS sol in a stoch. env. =', OBS.stochastic_cost)

    print('Reward for OBS sol in a Stoch. env. =', OBS.reward_sim)
    print('Routes for OBD sol')
    printSolution(OBD)
    #solution_to_dataframe(OBD)
    print('Routes for OBS sol')
    printSolution(OBS)
    #solution_to_dataframe(OBS)



    results = pd.DataFrame({ 
        "OBD cost": [OBD.cost],
        "OBD reward_det": [OBD.reward],
        "OBD cost_Stoch": [OBD.stochastic_cost],
        "OBD reward_Stoc": [OBD.reward_sim],
        "OBS cost": [OBS.stochastic_cost],
        "OBS reward": [OBS.reward_sim]
    }, index=[0])        
    results.to_csv("results.csv")

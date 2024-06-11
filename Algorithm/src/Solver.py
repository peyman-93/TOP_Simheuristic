import time
from param import parameters
from collections import deque
from Communication import read_results
from SimulationEnv import Simulation
from aux_functions import  printSolution, solution_to_dataframe
from simheu import genInitSol, merging

"""

def run_Flexsim(ref_sol, param, ord_f_name, FS_RUNS):
    stochastic_cost = 0
    for loop in range(FS_RUNS):
        simu = Simulation(param, ord_f_name, seed = loop)
        simu.run_simulation()
        result_i = read_results()
        for i, route in enumerate(ref_sol.routes):
            route.cost_sim += result_i['ExitTime'].iloc[i]
        stochastic_cost += result_i['ExitTime'].sum()
    for route in ref_sol.routes:
        route.cost_sim /= FS_RUNS
    return stochastic_cost / FS_RUNS
"""

def run_Flexsim(ref_sol, param, ord_f_name, FS_RUNS):
    stochastic_cost = 0
    max_stochastic_cost = 0  # Initialize the maximum stochastic cost

    for loop in range(FS_RUNS):
        simu = Simulation(param, ord_f_name, seed=loop)
        simu.run_simulation()
        result_i = read_results()
        for i, route in enumerate(ref_sol.routes):
            route.cost_sim += result_i['ExitTime'].iloc[i]
        stochastic_cost += result_i['ExitTime'].sum()

    for route in ref_sol.routes:
        route.cost_sim /= FS_RUNS
        if route.cost_sim > max_stochastic_cost:
            max_stochastic_cost = route.cost_sim  # Update the maximum stochastic cost

    average_stochastic_cost = stochastic_cost / FS_RUNS  # Calculate the average stochastic cost across all routes
    return average_stochastic_cost, max_stochastic_cost








"""
Simheuristic Execution
"""
def SimHeuristic(test, fleetSize, routeMaxCost, nodes):
    param = parameters()
    ord_f_name = "LocationToGo.csv"

  
    # generate an initial solution and efficiency list (greedy solution (BR = False) for the current alpha value)
    eff_list, init_sol = genInitSol(test, fleetSize, routeMaxCost, nodes)
    # Simulate init solution in a stochastic environment
    solution_to_dataframe(init_sol)
    init_sol.stochastic_cost, init_sol.max_stochastic_cost = run_Flexsim(init_sol, param, ord_f_name , param.FS_SHORT_RUNS)

    #total_reward_sim = sum(route.reward for route in init_sol.routes)
    
    # Apply a penalization to the init solution 
    # Apply half of the collected reward as the penalization
  
    """

    reward_sim = 0
    for route in init_sol.routes:
        if route.cost_sim <= routeMaxCost:
            reward_sim += route.reward
        else:
            reward_sim += 0.5 * route.reward
    init_sol.reward_sim = reward_sim
    """

    reward_sim = 0
    for route in init_sol.routes:
        if route.cost_sim <= routeMaxCost:
            reward_sim += route.reward  # No penalty if within max cost
        else:
            # Calculate the proportion by which the cost exceeds the maximum allowed cost
            excess_percentage = (route.cost_sim - routeMaxCost) / routeMaxCost
            # Apply penalty proportional to the excess percentage
            reward_lost = excess_percentage * route.reward
            reward_sim += (route.reward - reward_lost)  # Subtract the lost reward from the original reward

    init_sol.reward_sim = reward_sim


    print("####  This is result for the init_sol ####")
    printSolution(init_sol)

    print("####          ##########               ####")

    print("####  This is result for the Greedy_sol ####")

    print("Greedy solution deterministic Total cost", init_sol.cost)
    print("Greedy solution deterministic Total reward", init_sol.reward)

    print('Greedy solution stochastic Total cost', init_sol.stochastic_cost)
    print("Greedy solution stochastic Total reward:", init_sol.reward_sim)
    print('Greedy solution stochastic Max cost', init_sol.max_stochastic_cost)

    print("###########    ############      ##########   ###########       ####")
    # Set initial solution as OBD and OBS solutions
    OBD = init_sol
    OBS = init_sol
    # Define a set of elite stochastic solutions to consider
    eliteSols = deque(maxlen = 10) # define max number of elite sols
    eliteSols.append(OBS)

    # Stage 1: start the main loop searching for better det and stoch sols
    elapsed = 0
    startTime = time.time()
    while elapsed < test.maxTime:
        # Use the merging process of the PJs heuristic to generate a new det sol
        newSol = merging(True, test, fleetSize, routeMaxCost, nodes, eff_list)
        #print(OBS.reward_sim)
        #printSolution(newSol)
        # If new sol is promising, update OBD if appropriate
        if newSol.reward > OBD.reward:
            OBD = newSol
        # If new sol is promising, update OBS if appropriate
        if newSol.reward > OBS.reward:
            # Simulate new det solution in a stochastic environment
            solution_to_dataframe(newSol)
            newSol.stochastic_cost,  newSol.max_stochastic_cost = run_Flexsim(newSol, param, ord_f_name , param.FS_SHORT_RUNS) 

            #total_reward_sim = sum(route.reward for route in newSol.routes)
            #print("stage1_totalreward:", total_reward_sim)
            # Apply a penalization to the new det solution

            """
            
            reward_sim = 0
            for route in newSol.routes:
                if route.cost_sim <= routeMaxCost:
                    reward_sim += route.reward
                else:
                    reward_sim += 0.5 * route.reward
            newSol.reward_sim = reward_sim

            """

            reward_sim = 0
            for route in newSol.routes:
                if route.cost_sim <= routeMaxCost:
                    reward_sim += route.reward  # No penalty if within max cost
                else:
                    # Calculate the proportion by which the cost exceeds the maximum allowed cost
                    excess_percentage = (route.cost_sim - routeMaxCost) / routeMaxCost
                    # Apply penalty proportional to the excess percentage
                    reward_lost = excess_percentage * route.reward
                    reward_sim += (route.reward - reward_lost)  # Subtract the lost reward from the original reward

            newSol.reward_sim = reward_sim

            print("newSol solution deterministic cost", newSol.cost)
            print("newSol solution deterministic reward", newSol.reward)
            print('newSol solution stochastic cost', newSol.stochastic_cost)
            print("newSol solution stochastic reward:", newSol.reward_sim)
            # If new sol is promising in stochastic enviroment, update OBS if appropiate
            if newSol.reward_sim > OBS.reward_sim:
                OBS = newSol
                # Update set of elite solutions with new sol
                eliteSols.append(newSol) # the list removes the first element if max elite sols are saved
        # Update the elapsed time before evaluating the stopping criterion
        elapsed = time.time() - startTime

    # Stage 2: simulate elite solutions in a stochastic environment
    solution_to_dataframe(OBD)
    OBD.stochastic_cost, OBD.max_stochastic_cost = run_Flexsim(OBD, param, ord_f_name , param.FS_LONG_RUNS)

    #total_reward_sim = sum(route.reward for route in OBD.routes)
    #print("stage2_totalreward:", total_reward_sim)
    # Apply a penalization to the new det solution

    """

    reward_sim = 0
    for route in OBD.routes:
        if route.cost_sim <= routeMaxCost:
            reward_sim += route.reward
        else:
            reward_sim += 0.5 * route.reward
    OBD.reward_sim = reward_sim

    """

    reward_sim = 0
    for route in OBD.routes:
        if route.cost_sim <= routeMaxCost:
            reward_sim += route.reward  # No penalty if within max cost
        else:
            # Calculate the proportion by which the cost exceeds the maximum allowed cost
            excess_percentage = (route.cost_sim - routeMaxCost) / routeMaxCost
            # Apply penalty proportional to the excess percentage
            reward_lost = excess_percentage * route.reward
            reward_sim += (route.reward - reward_lost)  # Subtract the lost reward from the original reward

    OBD.reward_sim = reward_sim

    # Define the lower bound sol reward to improve
    OBS = OBD
    for eliteSol in eliteSols:
        # Simulate elite solution in a stochastic environment
        solution_to_dataframe(eliteSol)
        eliteSol.stochastic_cost, eliteSol.max_stochastic_cost = run_Flexsim(eliteSol, param, ord_f_name , param.FS_LONG_RUNS)
        # Apply a penalization to the new det solution
        #total_reward_sim = sum(route.reward for route in eliteSol.routes)
 
        """
    
        reward_sim = 0
        for route in eliteSol.routes:
            if route.cost_sim <= routeMaxCost:
                reward_sim += route.reward
            else:
                reward_sim += 0.5 * route.reward
        eliteSol.reward_sim = reward_sim
        """

        reward_sim = 0
        for route in eliteSol.routes:
            if route.cost_sim <= routeMaxCost:
                reward_sim += route.reward  # No penalty if within max cost
            else:
                # Calculate the proportion by which the cost exceeds the maximum allowed cost
                excess_percentage = (route.cost_sim - routeMaxCost) / routeMaxCost
                # Apply penalty proportional to the excess percentage
                reward_lost = excess_percentage * route.reward
                reward_sim += (route.reward - reward_lost)  # Subtract the lost reward from the original reward

        eliteSol.reward_sim = reward_sim


        print("stoch_eliteSol_cost:", eliteSol.stochastic_cost)
        print("stoch_eliteSol_reward:",eliteSol.reward_sim)

        if eliteSol.reward_sim > OBS.reward_sim:
            OBS = eliteSol

    return OBD, OBS

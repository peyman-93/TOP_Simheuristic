''' Reviewed by Angel A. Juan 2023.11 for the TOP with stochastic / dynamic travel times '''

import time
import copy
import math
import random
import operator
import numpy as np

from collections import deque

from aux_objects import Edge, Route, Solution
from simulation_Simheu import simulation

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        MAIN SIMHEURISTIC ALGORITHM BASED ON THE PJ'S HEURISTIC
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def algorithm(test, fleetSize, routeMaxCost, nodes):
    # Generate an efficiency list and initial solution using the best alpha value
    effList, initSol = genInitSol(test, fleetSize, routeMaxCost, nodes)
    simulation(initSol, test.shortSim, routeMaxCost, test.varLevel)
    # Set initial solution as OBD and OBS solutions
    OBD = initSol
    OBS = initSol
    # Define a set of elite stochastic solutions to consider
    eliteSols = deque(maxlen = 10) # define max number of elite sols
    eliteSols.append(OBS)

    # Stage 1: start the main loop searching for better det and stoch sols
    elapsed = 0
    startTime = time.time()
    while elapsed < test.maxTime:
        # Use the merging process of the PJs heuristic to generate a new det sol
        newSol = merging(True, test, fleetSize, routeMaxCost, nodes, effList)
        # If new sol is promising, update OBD if appropriate
        if newSol.reward > OBD.reward:
            OBD = newSol
        # If new sol is promising, update OBS if appropriate
        if newSol.reward > OBS.reward:
            # Simulate new det solution in a stochastic environment
            simulation(newSol, test.shortSim, routeMaxCost, test.varLevel)
            # If new sol is promising in stochastic enviroment, update OBS if appropiate
            if newSol.rewardSim > OBS.rewardSim:
                OBS = newSol
                # Update set of elite solutions with new sol
                eliteSols.append(newSol) # the list removes the first element if max elite sols are saved
        # Update the elapsed time before evaluating the stopping criterion
        elapsed = time.time() - startTime

    # Stage 2: simulate elite solutions in a stochastic environment
    simulation(OBD, test.longSim, routeMaxCost, test.varLevel)
    OBS = OBD # Define the lower bound sol reward to improve
    for eliteSol in eliteSols:
        simulation(eliteSol, test.longSim, routeMaxCost, test.varLevel)
        if eliteSol.rewardSim > OBS.rewardSim:
            OBS = eliteSol

    return OBD, OBS

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                    GENERATE DUMMY SOLUTION
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

""" Generate Dummy Solution """
def dummySolution(routeMaxCost, nodes):
    sol = Solution()
    for node in nodes[1:-1]: # excludes the start and finish depots
        snEdge = node.dnEdge
        nfEdge = node.ndEdge
        snfRoute = Route() # construct the route (start, node, finish)
        snfRoute.edges.append(snEdge)
        snfRoute.cost += node.service_t
        snfRoute.reward += node.reward
        snfRoute.cost += snEdge.cost
        snfRoute.edges.append(nfEdge)
        snfRoute.cost += nfEdge.cost
        node.inRoute = snfRoute # save in node a reference to its current route
        node.isLinkedToStart = True # this node is currently linked to start depot
        node.isLinkedToFinish = True # this node is currently linked to finish depot
        if snfRoute.cost <= routeMaxCost:
            sol.routes.append(snfRoute) # add this route to the solution
            sol.cost += snfRoute.cost
            sol.reward += snfRoute.reward # total reward in route


    return sol

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    SELECT ALPHA, BUILD THE EFFICIENCY LIST AND GENERATE AN INITIAL SOLUTION
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def genInitSol(test, fleetSize, routeMaxCost, nodes):
    bestReward = 0
    # Tune the alpha value for generating enhanced savings
    for alpha in np.linspace(0, 1, 11):
        newEffList = generateEfficiencyList(nodes, alpha)
        # Obtain a greedy solution (BR = False) for the current alpha value
        sol = merging(False, test, fleetSize, routeMaxCost, nodes, newEffList)
        if sol.reward > bestReward:
            bestReward = sol.reward
            effList = newEffList
            initSol = sol

    return effList, initSol

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                    GENERATE EFFICIENCY LIST
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

""" Generate efficiency list of nodes: construct edges and effList from nodes """
def generateEfficiencyList(nodes, alpha):
    start = nodes[0]
    finish = nodes[-1]
    for node in nodes[1:-1]: # excludes the start and finish depots
        snEdge = Edge(start, node) # creates the (start, node) edge (arc)
        nfEdge = Edge(node, finish) # creates the (node, finish) edge (arc)
        # compute the Euclidean distance as cost
        snEdge.cost = math.sqrt((node.x - start.x)**2 + (node.y - start.y)**2)
        nfEdge.cost = math.sqrt((node.x - finish.x)**2 + (node.y - finish.y)**2)
        # save in node a reference to the (depot, node) edge (arc)
        node.dnEdge = snEdge
        node.ndEdge = nfEdge

    efficiencyList = []
    for i in range(1, len(nodes) - 2): # excludes the start and finish depots
        iNode = nodes[i]
        for j in range(i + 1, len(nodes) - 1):
            jNode = nodes[j]
            ijEdge = Edge(iNode, jNode) # creates the (i, j) edge
            jiEdge = Edge(jNode, iNode)
            ijEdge.invEdge = jiEdge # sets the inverse edge (arc)
            jiEdge.invEdge = ijEdge
            # compute the Euclidean distance as cost
            ijEdge.cost = math.sqrt((jNode.x - iNode.x)**2 + (jNode.y - iNode.y)**2)
            jiEdge.cost = ijEdge.cost # assume symmetric costs
            # compute efficiency as proposed by Panadero et al.(2020)
            ijSavings = iNode.ndEdge.cost + jNode.dnEdge.cost - ijEdge.cost
            edgeReward = iNode.reward + jNode.reward
            ijEdge.savings = ijSavings
            ijEdge.efficiency = alpha * ijSavings + (1 - alpha) * edgeReward
            jiSavings = jNode.ndEdge.cost + iNode.dnEdge.cost - jiEdge.cost
            jiEdge.savings = jiSavings
            jiEdge.efficiency = alpha * jiSavings + (1 - alpha) * edgeReward
            # save both edges in the efficiency list
            efficiencyList.append(ijEdge)
            efficiencyList.append(jiEdge)

    # sort the list of edges from higher to lower efficiency
    efficiencyList.sort(key = operator.attrgetter("efficiency"), reverse = True)
    return efficiencyList

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            MERGING PROCESS IN THE PJ'S HEURISTIC
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

""" Perform the BR edge-selection & routing-merging iterative process """
def merging(useBR, test, fleetSize, routeMaxCost, nodes, effCopy):
    sol = dummySolution(routeMaxCost, nodes) # compute the dummy solution
    effList = copy.copy(effCopy) # make a shallow copy of the efficiency list since it will be modified
    while len(effList) > 0: # list is not empty
        position = 0
        if useBR == True:
            position = getRandomPosition(test.firstParam, test.secondParam, len(effList))
        else:
            position = 0  # greedy behavior
        ijEdge = effList.pop(position) # select the next edge from the list
        # determine the nodes i < j that define the edge
        iNode = ijEdge.origin
        jNode = ijEdge.end
        # determine the routes associated with each node
        iRoute = iNode.inRoute
        jRoute = jNode.inRoute
        # check if merge is possible
        isMergeFeasible = checkMergingConditions(iNode, jNode, iRoute, jRoute, ijEdge, routeMaxCost)
        # if all necessary conditions are satisfied, merge and delete edge (j, i)
        if isMergeFeasible == True:
        # if still in list, delete edge (j, i) since it will not be used
            jiEdge = ijEdge.invEdge
            if jiEdge in effList:
                effList.remove(jiEdge)
            # iRoute will contain edge (i, finish)
            iEdge = iRoute.edges[-1] # iEdge is (i, finish)
            # remove iEdge from iRoute and update iRoute cost
            iRoute.edges.remove(iEdge)
            iRoute.cost -= iEdge.cost
            # node i will not be linked to finish depot anymore
            iNode.isLinkedToFinish = False
            # jRoute will contain edge (start, j)
            jEdge = jRoute.edges[0]
            # remove jEdge from jRoute and update jRoute cost
            jRoute.edges.remove(jEdge)
            jRoute.cost -= jEdge.cost
            # node j will not be linked to start depot anymore
            jNode.isLinkedToStart = False
            # add ijEdge to iRoute
            iRoute.edges.append(ijEdge)
            iRoute.cost += ijEdge.cost
            iRoute.cost += jNode.service_t

            iRoute.reward += jNode.reward
            jNode.inRoute = iRoute
            # add jRoute to new iRoute
            for edge in jRoute.edges:
                iRoute.edges.append(edge)
                iRoute.cost += edge.cost
                iRoute.cost += edge.end.service_t
                iRoute.reward += edge.end.reward
                edge.end.inRoute = iRoute
            # delete jRoute from emerging solution
            sol.cost -= ijEdge.savings
            sol.routes.remove(jRoute)

    # sort the list of routes in sol by reward (reward) and delete extra routes
    sol.routes.sort(key = operator.attrgetter("reward"), reverse = True)
    for route in sol.routes[fleetSize:]:
        sol.reward -= route.reward # update reward
        sol.cost -= route.cost # update cost
        sol.routes.remove(route) # delete extra route
    return sol

""" Gets a random position according to a Gemetric(beta) """
def getRandomPosition(beta1, beta2, size):
    # randomly select a beta value between beta1 and beta2
    beta = beta1 + random.random() * (beta2 - beta1)
    index = int(math.log(random.random())/math.log(1 - beta))
    index = index % size
    return index

""" Check if merging conditions are met """
def checkMergingConditions(iNode, jNode, iRoute, jRoute, ijEdge, routeMaxCost):
    # condition 1: iRoute and jRoure are not the same route object
    if iRoute == jRoute: return False
    # condition 2: jNode has to be linked to start and i node to finish
    if iNode.isLinkedToFinish == False or jNode.isLinkedToStart == False: return False
    # condition 3: cost after merging does not exceed maxTime (or maxCost)
    if iRoute.cost + jRoute.cost - ijEdge.savings > routeMaxCost: return False
    # else, merging is feasible
    return True


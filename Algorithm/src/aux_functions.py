''' Reviewed by Angel A. Juan 2023.06 for the TOP with stochastic / dynamic travel times '''

from aux_objects import Test, Node
import pandas as pd

""" Generate a list of tests to run from a file """
def read_tests(file_name):
    with open(file_name) as file:
        tests = []
        for line in file:
            tokens = line.split("\t")
            if '#' not in tokens[0]:
                aTest = Test(*tokens) # '*' unpacks tokens as parameters
                tests.append(aTest)
    return tests

""" Generate a list of nodes from instance file """
def read_instance(file_name):
    with open(file_name) as instance:
        i = -3 # we start at -3 so that the first node is node 0
        nodes = []
        for line in instance:
            if i == -3: nNodes = int(line.split(';')[1]) # line 0 contains the number of nodes, not needed
            elif i == -2: fleetSize = int(line.split(';')[1])
            elif i == -1: routeMaxCost = float(line.split(';')[1])
            else:
                # array data with node data: x, y, reward
                data = [float(x) for x in line.split(';')]
                # create instance nodes
                service_t = 0 if i != 0 and i != nNodes - 1 else 0
                aNode = Node(i, data[0], data[1], data[2], service_t)
                nodes.append(aNode)
            i += 1
    return fleetSize, routeMaxCost, nodes

""" Print routes in a solution """
def printRoutes(sol):
    for route in sol.routes:
        print("0", end = "")
        for e in route.edges:
            print("->", e.end.ID, end="")
        print("\nRoute det reward:", route.reward, "; det cost:", route.cost)
    print("Solution time: ", sol.time)

"""

def printSolution(sol):
	for i, route in enumerate(sol.routes, start=1):
		print('List{:d}: {:d}-{:s} '.format(i, route.edges[0].origin.ID+1, '-'.join(str(edge.end.ID +1) for edge in route.edges)))
	print("Cost: {:.2f}".format(sol.cost))
	print("Reward: {:.2f}".format(sol.reward))
	print("Time: {:.2f}\n".format(sol.time))
"""    

def printSolution(sol):
    max_cost = float('-inf')  # Initialize max cost


    for i, route in enumerate(sol.routes, start=1):
        route_display = '{:d}-{:s}'.format(route.edges[0].origin.ID + 1, '-'.join(str(edge.end.ID + 1) for edge in route.edges))
        print('List{:d}: {}'.format(i, route_display))
        print("Route #{:d} cost: {:.2f}".format(i, route.cost))
        print("Route #{:d} reward: {:.2f}".format(i, route.reward))

        # Update max cost and reward if current route's cost or reward is greater
        if route.cost > max_cost:
            max_cost = route.cost
            max_reward_for_max_cost = route.reward

    # After all routes are processed, print the max cost and reward
    print("Maximum Cost among Routes: {:.2f}".format(max_cost))
    print("Reward of Max Cost Routes: {:.2f}".format(max_reward_for_max_cost))     
 

"""

def solution_to_dataframe(sol):
    # Create an empty list to hold the data
    data = []
    
    # Extract routes data
    for i, route in enumerate(sol.routes, start=1):
        # Prepare a row with 'List#' as the first column and route IDs as subsequent columns
        row = ['List' + str(i)] + [route.edges[0].origin.ID+1] + [edge.end.ID +1 for edge in route.edges]
        data.append(row)
    
        print('Route #{:d}: {:d}-{:s} '.format(i, route.edges[0].origin.ID + 1, '-'.join(str(edge.end.ID + 1) for edge in route.edges)))
        print("Route #{:d} cost: {:.2f}".format(i, route.cost))
        print("Route #{:d} reward: {:.2f}".format(i, route.reward))    
    
    # Find the maximum number of columns any route might have for consistent DataFrame shape
    max_cols = max(len(row) for row in data)
    
    # Create a DataFrame, filling missing values with NaN (or any placeholder you prefer)
    df = pd.DataFrame(data, columns=[''] + ['NN' for _ in range(max_cols - 1)]).fillna('')
    
    # Save the DataFrame to a CSV file
    df.to_csv('LocationToGo.csv', index=False)
    
    # Print statements for cost, reward, and time can be kept or adjusted as needed
    print("Cost: {:.2f}".format(sol.cost))
    print("Reward: {:.2f}".format(sol.reward))
    print("Time: {:.2f}\n".format(sol.time))
    
    return df

"""

def solution_to_dataframe(sol):
    data = []  # To hold the route data for the DataFrame
    max_cost = float('-inf')  # Initialize max cost

    # Extract routes data and track maximum cost and reward
    for i, route in enumerate(sol.routes, start=1):
        row = ['List' + str(i)] + [route.edges[0].origin.ID+1] + [edge.end.ID + 1 for edge in route.edges]
        data.append(row)
        
        print(f'Route #{i}: {row[1]}-{"-".join(map(str, row[2:]))}')
        print(f"Route #{i} cost: {route.cost:.2f}")
        print(f"Route #{i} reward: {route.reward:.2f}")
        
        # Update max cost and reward if current route's cost or reward is greater
        if route.cost > max_cost:
            max_cost = route.cost
            max_reward_for_max_cost = route.reward

    # Create DataFrame from data list
    max_cols = max(len(row) for row in data)  # Find maximum number of columns for consistent DataFrame shape
    df = pd.DataFrame(data, columns=['List#'] + ['NN' + str(i) for i in range(1, max_cols)]).fillna('')
    df.to_csv('LocationToGo.csv', index=False)  # Save the DataFrame to a CSV file

    # Print the overall solution's cost, reward, time, and the maximums found
    print("Overall Cost: {:.2f}".format(sol.cost))
    print("Overall Reward: {:.2f}".format(sol.reward))
    print("Overall Time: {:.2f}\n".format(sol.time))
    print("Maximum Cost among Routes: {:.2f}".format(max_cost))
    print("Reward of Max Cost Routes: {:.2f}".format(max_reward_for_max_cost))  

    return df

# Copyright 2010-2018 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# [START program]
"""Capacited Vehicles Routing Problem (CVRP)."""

# [START import]
from __future__ import print_function
from functools import partial
from six.moves import xrange
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
# [END import]


# [START data_model]
def create_data_model(inputData):
    # datamatrix,psngr_no,buscap,num_vehicles
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix']=inputData['distance_matrix']

    print("DIST MATRIX============")
    print(data['distance_matrix'])

    # data['distance_matrix'] = [
    #  [0, 141099, 9528, 11708, 4359, 1590, 5806, 5261, 412373, 6962, 591816, 22617, 9144, 792, 4056, 4586, 6381, 6027],
    #  [141102, 0, 156102, 156027, 151283, 142486, 153469, 153475, 343114, 151434, 737372, 155464, 155025, 141879, 137062, 150571, 151293, 151592],
    #  [9734, 154652, 0, 3671, 5631, 10293, 4458, 5087, 410413, 4711, 584708, 15650, 475, 8996, 14828, 7453, 4800, 4102], 
    #  [10805, 157778, 5160, 0, 7952, 11365, 5228, 5951, 412733, 8978, 588010, 11978, 5546, 10067, 16782, 9774, 7121, 6767], 
    #  [4359, 150265, 6093, 8614, 0, 4918, 3460, 3466, 406026, 2983, 588685, 27231, 5016, 3621, 8400, 1440, 1674, 1478], 
    #  [1714, 142013, 10029, 12209, 4860, 0, 6307, 5762, 409511, 5998, 593633, 24123, 9645, 2044, 5562, 4288, 5942, 6528],
    #  [5802, 152511, 3813, 5993, 3491, 6361, 0, 1187, 408272, 4517, 587474, 15105, 3430, 5064, 9843, 5313, 2660, 2307], 
    #  [5336, 146420, 4913, 7093, 3525, 5895, 1191, 0, 408306, 4559, 588023, 14415, 4529, 4598, 9377, 5074, 2694, 2340], 
    #  [412157, 343311, 411222, 413743, 406403, 413541, 408589, 408595, 0, 406554, 740487, 421556, 410145, 412183, 404015, 406134, 406414, 406712], 
    #  [6935, 150342, 4452, 7497, 3199, 5943, 4515, 4547, 406103, 0, 584652, 27308, 3950, 6197, 10573, 3399, 2368, 2798],
    #  [595465, 738014, 586070, 587696, 593068, 594132, 588611, 588840, 736898, 586738, 0, 614795, 584865, 596242, 595440, 592799, 593079, 588019], 
    #  [24018, 150627, 15269, 13389, 29236, 25402, 14539, 14530, 421856, 29387, 615206, 0, 15654, 24044, 22214, 28524, 29247, 16078],
    #  [9259, 154177, 524, 4150, 5156, 9818, 4004, 4633, 409938, 3784, 584186, 16128, 0, 8521, 14581, 6978, 4325, 3627], 
    #  [792, 141876, 8790, 10970, 3621, 1920, 5068, 4523, 412411, 6224, 592594, 22655, 8406, 0, 4834, 3848, 5643, 5289], 
    #  [4041, 137043, 15219, 17533, 8385, 5424, 9832, 9286, 404540, 10551, 592211, 20964, 14142, 4818, 0, 8612, 10411, 10709], 
    #  [4586, 149835, 7850, 10371, 1440, 4497, 5217, 5223, 405596, 3663, 588254, 26800, 6773, 3848, 8627, 0, 3607, 2928], 
    #  [5083, 150625, 6340, 8861, 714, 5642, 2508, 3010, 406386, 3343, 589045, 27591, 5263, 4345, 9124, 2164, 0, 1329]
    #  ]
    # [START demands_capacities]
    # data['demands'] = [0, 0, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
    # data['demands'].append(0)
    # data['demands'].append(0)
    data['demands']=inputData['passengerCount']
    data['demands'][0]=0
    data['demands'][1]=0
    
    print("psngr_no======================")
    print(data['demands'])
    # data['vehicle_capacities'] = [20, 5, 10, 35]
    data['vehicle_capacities']=inputData['busCapacity']
    # print("vehicle_capacities======================")
    # print(data['vehicle_capacities'])
    # # # [END demands_capacities]
    data['num_vehicles'] = len(inputData['busCapacity'])
    data['time_per_demand_unit'] = 5  # 5 minutes/unit
    data['num_locations'] = len(inputData['distance_matrix'])
    # data['depot']=0
    data['starts'] = [0]*data['num_vehicles']
    data['ends'] = [1]*data['num_vehicles']
    
    data['time_windows'] = inputData['time_windows']

    data['vehicle_speed'] = 83  # Travel speed: 5km/h converted in m/min

    return data
    # [END data_model]

def create_time_evaluator(data):
    """Creates callback to get total times between locations."""

    def service_time(data, node):
        """Gets the service time for the specified location."""
        return data['demands'][node] * data['time_per_demand_unit']

    def travel_time(data, from_node, to_node):
        """Gets the travel times between two locations."""
        if from_node == to_node:
            travel_time = 0
        else:
            # travel_time = manhattan_distance(data['locations'][from_node], data[
            #     'locations'][to_node]) / data['vehicle_speed']
            travel_time = data['distance_matrix'][from_node][to_node]/data['vehicle_speed']
        return travel_time

    _total_time = {}
    # precompute total time to have time callback in O(1)
    for from_node in xrange(data['num_locations']):
        _total_time[from_node] = {}
        for to_node in xrange(data['num_locations']):
            if from_node == to_node:
                _total_time[from_node][to_node] = 0
            else:
                _total_time[from_node][to_node] = int(
                    service_time(data, from_node) + travel_time(
                        data, from_node, to_node))

    def time_evaluator(manager, from_node, to_node):
        """Returns the total time between the two nodes"""
        return _total_time[manager.IndexToNode(from_node)][manager.IndexToNode(
            to_node)]

    return time_evaluator

def add_time_window_constraints(routing, manager, data, time_evaluator_index):
    """Add Global Span constraint"""
    time = 'Time'
    horizon = 500
    routing.AddDimension(
        time_evaluator_index,
        horizon,  # allow waiting time
        horizon,  # maximum time per vehicle
        False,  # don't force start cumul to zero since we are giving TW to start nodes
        time)
    time_dimension = routing.GetDimensionOrDie(time)
    # Add time window constraints for each location except depot
    # and 'copy' the slack var in the solution object (aka Assignment) to print it
    for location_idx, time_window in enumerate(data['time_windows']):
        index = manager.NodeToIndex(location_idx)
        if index == -1:
            continue
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        routing.AddToAssignment(time_dimension.SlackVar(index))
    # Add time window constraints for each vehicle start node
    # and 'copy' the slack var in the solution object (aka Assignment) to print it
    for vehicle_id in xrange(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(data['time_windows'][data['starts'][vehicle_id]][0],
                                                data['time_windows'][data['starts'][vehicle_id]][1])
        routing.AddToAssignment(time_dimension.SlackVar(index))
        # Warning: Slack var is not defined for vehicle's end node
        #routing.AddToAssignment(time_dimension.SlackVar(self.routing.End(vehicle_id)))



def print_solution(data, manager, routing, assignment):  # pylint:disable=too-many-locals
    """Prints assignment on console"""
    # Display dropped nodes.
    droppedNodes=[]
    routes=[]
    emptyVehicle=[]
    dropped_nodes = 'Dropped nodes:'
    for node in range(routing.Size()):
        if routing.IsStart(node) or routing.IsEnd(node):
            continue
        if assignment.Value(routing.NextVar(node)) == node:
            dropped_nodes += ' {}'.format(manager.IndexToNode(node))
            droppedNodes.append(manager.IndexToNode(node))
    # print(dropped_nodes)
    print('Objective: {}'.format(assignment.ObjectiveValue()))
    total_distance = 0
    total_load = 0
    total_time = 0
    capacity_dimension = routing.GetDimensionOrDie('Capacity')
    time_dimension = routing.GetDimensionOrDie('Time')
    for vehicle_id in xrange(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        distance = 0
        route={}
        route['bus']=vehicle_id
        route['nodes']=[]
        while not routing.IsEnd(index):
            node={}
            load_var = capacity_dimension.CumulVar(index)
            time_var = time_dimension.CumulVar(index)
            slack_var = time_dimension.SlackVar(index)
            node['index']=manager.IndexToNode(index)
            node['load_var']=assignment.Value(load_var)
            node['max_time_var']=assignment.Max(time_var)
            node['min_time_var']=assignment.Min(time_var)
            node['max_slack_var']=assignment.Max(slack_var)
            node['min_slack_var']=assignment.Min(slack_var)
            route['nodes'].append(node)
            plan_output += ' {0} Load({1}) Time({2},{3}) Slack({4},{5}) ->'.format(
                manager.IndexToNode(index),
                assignment.Value(load_var),
                assignment.Min(time_var),
                assignment.Max(time_var),
                assignment.Min(slack_var), assignment.Max(slack_var))
            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            distance += routing.GetArcCostForVehicle(previous_index, index,
                                                     vehicle_id)
        load_var = capacity_dimension.CumulVar(index)
        time_var = time_dimension.CumulVar(index)
        slack_var = time_dimension.SlackVar(index)
        plan_output += ' {0} Load({1}) Time({2},{3})\n'.format(
            manager.IndexToNode(index),
            assignment.Value(load_var),
            assignment.Min(time_var), assignment.Max(time_var))
        node={}
        node['index']=manager.IndexToNode(index)
        node['load_var']=assignment.Value(load_var)
        node['max_time_var']=assignment.Max(time_var)
        node['min_time_var']=assignment.Min(time_var)
        route['nodes'].append(node)
        route['totalDistance']=distance
        route['routeLoad']=assignment.Value(load_var)
        route['totalTime']=assignment.Value(time_var)
        plan_output += 'Distance of the route: {0}m\n'.format(distance)
        plan_output += 'Load of the route: {}\n'.format(
            assignment.Value(load_var))
        plan_output += 'Time of the route: {}\n'.format(
            assignment.Value(time_var))
        print(plan_output)
        total_distance += distance
        total_load += assignment.Value(load_var)
        total_time += assignment.Value(time_var)
        # print(route)
        if len(route['nodes'])<3:
            emptyVehicle.append(vehicle_id)
        else:    
            routes.append(route)
    # print(routes)
    data={}
    data['routes']=routes
    data['droppedNodes']=droppedNodes
    data['totalDistace']=total_distance
    data['totalLoad']=total_load
    data['totalTime']=total_time    
    print('Total Distance of all routes: {0}m'.format(total_distance))
    print('Total Load of all routes: {}'.format(total_load))
    print('Total Time of all routes: {0}min'.format(total_time))
    # print(data)
    return data

    
    #return data['routes']=[{"Bus no",[{},{},{}]},{}]
    #route['Bus_no']=3 route['nodes']=[{},{},{}]
    #route['Total']=
    #route['Total']=
    #route['Total']=
    #route['nodes'][0]={'stop':0,'load':2,'windows':}


def solver(inputData):
    # datamatrix,psngr_no,buscap,num_vehicles
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    # [START data]
    data = create_data_model(inputData)

    # [END data]
    print("in solver")
    # Create the routing index manager.
    # [START index_manager]
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'],
                                        #    data['depot'],
                                           data['starts'],
                                           data['ends']
                                        )
    # [END index_manager]

    # Create Routing Model.
    # [START routing_model]
    routing = pywrapcp.RoutingModel(manager)

    # [END routing_model]

    # Create and register a transit callback.
    # [START transit_callback]
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    # [END transit_callback]

    # Define cost of each arc.
    # [START arc_cost]
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # [END arc_cost]

 # Add Distance constraint.
    # dimension_name = 'Distance'
    # routing.AddDimension(
    #     transit_callback_index,
    #     0,  # no slack
    #     3000,  # vehicle maximum travel distance
    #     True,  # start cumul to zero
    #     dimension_name)
    # distance_dimension = routing.GetDimensionOrDie(dimension_name)
    # distance_dimension.SetGlobalSpanCostCoefficient(100)


    # Add Capacity constraint.
    # [START capacity_constraint]
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')
    # [END capacity_constraint]

    # Add Time Window constraint
    time_evaluator_index = routing.RegisterTransitCallback(
        partial(create_time_evaluator(data), manager))
    add_time_window_constraints(routing, manager, data, time_evaluator_index)

    penalty = 20000
    for node in range(0, len(data['distance_matrix'])):
        if manager.NodeToIndex(node) == -1:
            continue
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)



    # Setting first solution heuristic.
    # [START parameters]
    # Setting first solution heuristic (cheapest addition).
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)  # pylint: disable=no-membe
    # [END parameters]

    # Solve the problem.
    # [START solve]
    assignment = routing.SolveWithParameters(search_parameters)
    # [END solve]
    data['previous_solution'] = assignment
    # Print solution on console.
    # [START print_solution]
    print(assignment)
    if assignment:
        return print_solution(data, manager, routing, assignment)
    # [END print_solution]

    print('\n\n\n')
    ### Running new instance ####
    # data['demands'][14] = 0
    
    # new_solution = routing.SolveFromAssignmentWithParameters(data['previous_solution'] , search_parameters)
    
    # if new_solution:
    #     print('New solution from previous one : ')
    #     print_solution(data, manager , routing, new_solution)
        

# if __name__ == '__main__':
#     # print(":jias")
#     main()
# [END program]

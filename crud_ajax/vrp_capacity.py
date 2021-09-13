# [START import]
from __future__ import print_function
from functools import partial
from six.moves import xrange
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# [END import]


# [START data_model]
def create_data_model(inputData):
    # print("inputData===================")
    # print(inputData)
    # datamatrix,psngr_no,buscap,num_vehicles
    """Stores the data for the problem."""
    data = {}
    data['duration_matrix'] = inputData['duration_matrix']
    data['distance_matrix']=inputData['distance_matrix']
    data['demands']=inputData['passengerCount']
    # data['demands'][0]=0
    # data['demands'][1]=0
    data['vehicle_capacities']=inputData['busCapacity']
    data['num_vehicles'] = len(inputData['busCapacity'])
    data['time_per_demand_unit'] = inputData['time_per_demand_unit']
    # data['time_per_demand_unit'] = 0.5
    data['lower_stop']  = 1
    data['pickup'] = inputData['pickup']
    data['num_locations'] = len(inputData['duration_matrix'])
    if inputData['pickup'] == 1:
        data['starts'] = inputData['starts']
        data['ends'] = inputData['ends']
        # data['office_end'] = inputData['office_end']
    else:
        data['starts'] = inputData['ends']
        data['ends'] = inputData['starts']
        # data['office_start'] = inputData['office_start']        
    data['time_windows'] = inputData['time_windows']
    data['soft_time_windows'] = inputData['soft_time_windows']
    data['max_allowed_time']  = inputData['max_allowed_time']
    data['vehicle_speed'] = 830  # Travel speed: 5km/h converted in m/min
    data['drop_penalty'] = 100000
    data['soft_min_occ_penalty'] = 20000
    data['soft_time_penalty'] = 2000
    data['soft_min_occupancy'] = inputData['soft_min_occupancy']
    data['hard_min_occupancy'] = inputData['hard_min_occupancy']
    print('data############')
    print(data)
    return data
    # [END data_model]

def create_time_evaluator(data):
    """Creates callback to get total times between locations."""

    def service_time(data, node):
        """Gets the service time for the specified location."""
        return data['lower_stop'] + int(data['demands'][node] * data['time_per_demand_unit'])

    def travel_time(data, from_node, to_node):
        """Gets the travel times between two locations."""
        if from_node == to_node:
            travel_time = 0
        else:
            # travel_time = manhattan_distance(data['locations'][from_node], data[
            #     'locations'][to_node]) / data['vehicle_speed']
            # travel_time = data['distance_matrix'][from_node][to_node]/data['vehicle_speed']
            travel_time = data['duration_matrix'][from_node][to_node]
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
    horizon = data['max_allowed_time']
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
    
    print("1st")
    # Add time window constraints for each vehicle start node
    # and 'copy' the slack var in the solution object (aka Assignment) to print it
    for vehicle_id in xrange(data['num_vehicles']):
        index = routing.Start(vehicle_id) 
        time_dimension.CumulVar(index).SetRange(data['time_windows'][data['starts'][vehicle_id]][0],
                                                data['time_windows'][data['starts'][vehicle_id]][1])
        routing.AddToAssignment(time_dimension.SlackVar(index)) 
        # Warning: Slack var is not defined for vehicle's end node
        #routing.AddToAssignment(time_dimension.SlackVar(self.routing.End(vehicle_id)))
    print("2st")
    ## soft constraint
    soft_time_penalty = data['soft_time_penalty']
    for location_idx, soft_time_window in enumerate(data['soft_time_windows']):
        index = manager.NodeToIndex(location_idx)
        if index == -1:
            continue
        time_dimension.SetCumulVarSoftLowerBound(index, soft_time_window[0], soft_time_penalty)
        # time_dimension.SetCumulVarSoftUpperBound(index, soft_time_window[1], soft_time_penalty)
        
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
    print(dropped_nodes)
    print('Objective: {}'.format(assignment.ObjectiveValue()))
    total_duration = 0
    total_load = 0
    total_time = 0
    capacity_dimension = routing.GetDimensionOrDie('Capacity')
    time_dimension = routing.GetDimensionOrDie('Time')
    for vehicle_id in xrange(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        duration = 0
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
            duration += routing.GetArcCostForVehicle(previous_index, index,
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
        route['totalDuration']=duration
        route['routeLoad']=assignment.Value(load_var)
        route['duration']=assignment.Value(time_var)
        # route['start_time'] = data['office_start'] -  
        # route['start_time'] = data['office_end'] - node['min_time_var'] 
        plan_output += 'Duration of the route: {0}m\n'.format(duration)
        plan_output += 'Load of the route: {}\n'.format(
            assignment.Value(load_var))
        plan_output += 'Time of the route: {}\n'.format(
            assignment.Value(time_var))
        print(plan_output)
        total_duration += duration
        total_load += assignment.Value(load_var)
        total_time += assignment.Value(time_var)
        # route['duration'] = time_var
        # print(route)
        if len(route['nodes'])<3:
            emptyVehicle.append(vehicle_id)
        else:    
            routes.append(route)
    data2={}
    data2['routes']=routes
    data2['status'] = routing.status()
    data2['dropped_nodes']= droppedNodes
    # data2['totalDuration']= total_duration
    data2['totalLoad']=total_load
    data2['totalTime']=total_time    
    data2['empty_vehicle'] = emptyVehicle
    print("empty vehicle")
    print(emptyVehicle)
    data2['pickup'] = data['pickup']
    print('Total Distance of all routes: {0}m'.format(total_duration))
    print('Total Load of all routes: {}'.format(total_load))
    print('Total Time of all routes: {0}min'.format(total_time))
    # print(data)
    # print("ROUTES=====================FINAL====")        
    # print(routes)
    return data2


def solver(inputData):
    # datamatrix,psngr_no,buscap,num_vehicles
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    # [START data]
    print(inputData)
    data = create_data_model(inputData)
    print("after data model")
    # [END data]
    # print("in solver")
    # # Create the routing index manager.
    # # [START index_manager]
    # print(data['starts'])
    # print(data['num_vehicles'])
    manager = pywrapcp.RoutingIndexManager(len(data['duration_matrix']),
                                           data['num_vehicles'],
                                           data['starts'],
                                           data['ends']
                                        )
    # [END index_manager]
    # print("ERRROR")
    # Create Routing Model.
    # [START routing_model]
    routing = pywrapcp.RoutingModel(manager)

    # [END routing_model]

    # Create and register a transit callback.
    # [START transit_callback]
    def duration_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['duration_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(duration_callback)
    # [END transit_callback]

    # Define cost of each arc.
    # [START arc_cost]
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # [END arc_cost]

#   Add Distance constraint.
    # dist_dimension_name = 'Distance'
    # routing.AddDimension(
    #     transit_callback_index,
    #     0,  # no slack
    #     3000,  # vehicle maximum travel distance
    #     True,  # start cumul to zero
    #     dist_dimension_name)
    # distance_dimension = routing.GetDimensionOrDie(dist_dimension_name)
    # distance_dimension.SetGlobalSpanCostCoefficient(100)    


    # distance_dimension.SetCumulVarSoftUpperBound(index, time_window[1], soft_time_penalty)            
    #     Add Capacity constraint.
    # [START capacity_constraint]
    # Create and register a transit callback.
    # [START transit_callback]
    # print("before distance")
    # def distance_callback(from_index, to_index):
    #     """Returns the distance between the two nodes."""
    #     # Convert from routing variable Index to distance matrix NodeIndex.
    #     from_node = manager.IndexToNode(from_index)
    #     to_node = manager.IndexToNode(to_index)
    #     return data['distance_matrix'][from_node][to_node]

    # distance_callback_index = routing.RegisterUnaryTransitCallback(
    #     distance_callback)
    # routing.AddDimension(
    #     distance_callback_index,
    #     0,  # null capacity slack
    #     2000000,  # vehicle maximum capacities
    #     True,  # start cumul to zero
    #     'distance')
    # distance_dimension = routing.GetDimensionOrDie('dimension')
    # # distance_dimension.SetGlobalSpanCostCoefficient(0)
    # # [END capacity_constraint]
    # print("after dist")
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

    demand_dimension = routing.GetDimensionOrDie('Capacity')
    
    print("before hard demand")
    soft_min_occ_penalty = data['soft_min_occ_penalty']
    index = manager.NodeToIndex(data['ends'][0])
    for vehicle_id in range(data['num_vehicles']):
        index = routing.End(vehicle_id)
        demand_dimension.SetCumulVarSoftLowerBound(index,data['soft_min_occupancy'][vehicle_id], soft_min_occ_penalty)
        if data['hard_min_occupancy']:
            print("HARD#######################")
            demand_dimension.CumulVar(routing.End(vehicle_id)).RemoveInterval(1, data['hard_min_occupancy'][vehicle_id])
    print("after hard demand")
    # Add Time Window constraint
    time_evaluator_index = routing.RegisterTransitCallback(
        partial(create_time_evaluator(data), manager))
    add_time_window_constraints(routing, manager, data, time_evaluator_index)
    print("after time wi")
    drop_penalty = data['drop_penalty']
    for node in range(0, len(data['duration_matrix'])):
        if manager.NodeToIndex(node) == -1:
            continue
        routing.AddDisjunction([manager.NodeToIndex(node)], drop_penalty)



    # Setting first solution heuristic.
    # [START parameters]
    # Setting first solution heuristic (cheapest addition).
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)  # pylint: disable=no-member
    search_parameters.time_limit.seconds = 100
    # [END parameters]

    # Solve the problem.
    # [START solve]
    assignment = routing.SolveWithParameters(search_parameters)
    # [END solve]
    print("assignment")
    print()
    data['previous_solution'] = assignment
    # Print solution on console.
    # [START print_solution]
    # print(assignment)
    print("before print")
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

#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import io
import random
from deap import base, creator, tools


# In[2]:


base_individual = [] # will be used to fill in the existing route itself
def load_data(data):
    instance = {}
    instance['number_busses'] = len(data['busCapacity'])
    nb=len(data['busCapacity'])
    L = [(data['busCapacity'][i], i) for i in range(len(data['busCapacity']))]
    L.sort(reverse=True)
    instance['vehicle_capacity'] , instance['perm'] = zip(*L)
    #instance['vehicle_capacity'] = data['busCapacity']
    instance['distance_matrix'] = data['duration_matrix']
    # instance['distance_matrix'] = [[item/830 for item in subl] for subl in data['duration_matrix']]
    # print('distance matrix ===============> ')
    # print(instance['distance_matrix'])
    instance['tot_stops'] = len(data['duration_matrix'])
    instance['ready_time'] = []
    instance['due_time'] = []
    for j in data['time_windows']:
        instance['ready_time'].append(j[0])
        instance['due_time'].append(j[1])
    instance['demand'] = data['passengerCount']
    print(' >>>>>>>>>>>>>>>>>> ' ,instance['demand'])
    #instance['bus_starts'] = data['starts']
    instance['bus_starts'] = [data['starts'][ instance['perm'][i] ] for i in range(nb)]
    #instance['bus_ends'] = data['ends']
    instance['bus_ends'] = [data['ends'][ instance['perm'][i] ] for i in range(nb)]
    tmp_set = set(data['starts'])
    for j in data['ends']:
        tmp_set.add(j)
    instance['valid_stations'] = []
    instance['rev_map'] = {}
    for j in range(instance['tot_stops']):
        if(j not in tmp_set):
            instance['valid_stations'].append(j)
    sz = len(instance['valid_stations'])
    for j in range(sz):
        instance['rev_map'][instance['valid_stations'][j]] = j
        
    instance['good_nodes'] = sz   # nodes that actually matter and will determine solution
    return instance


# In[ ]:





# In[3]:


def mutz(individual):
    # print("INDI")
    if(len(individual) <= 4):
        cpy = individual
        random.shuffle(cpy)
        return cpy
        
    start, stop = sorted(random.sample(range(len(individual)), 2))
    while(start >= stop or start == 0 or stop+1 == len(individual)):
        print(start)
        print(stop)
        start, stop = sorted(random.sample(range(len(individual)), 2))
    #print("after while") 
    individual = individual[:start] + individual[stop:start-1:-1] + individual[stop+1:]
    return individual


# In[4]:


def mut_inverse_indexes(individual):
    '''gavrptw.core.mut_inverse_indexes(individual)'''
    start, stop = sorted(random.sample(range(len(individual)), 2))
    
    individual = individual[:start] + individual[stop:start-1:-1] + individual[stop+1:]
    return (individual, )


# In[5]:


def converts(soln, instance):
    
    ret = []
    routes = soln['routes']
    buses = {}

    for loops in routes:
        curbus = loops['bus']
        tmp=[]
        for j in loops['nodes']:
            if(j['index'] == instance['bus_starts'][curbus]):
                continue
            elif(j['index'] == instance['bus_ends'][curbus]):
                continue
            tmp.append(j['index'])
        buses[curbus]=tmp

    for j in instance['perm']:
        if(j in buses and len(buses[j]) > 0):
            for x in buses[j]:
                ret.append(x)


    for j in instance['valid_stations']:
        if(j not in ret):
            ret.append(j)

    for j in range(len(ret)):
        ret[j] = instance['rev_map'][ret[j]]

    return ret


# In[6]:


def initPopulation(baze):
    ## return some random initialization
    prob = random.random()
    mutation_prob = 0.5
    #base_individual = [12,11,15,13,9,14,16,10,2,1,4,3,7,8,6,5]
    individual = baze
    # print("ing")
    # print(individual)
    if(prob < mutation_prob):
        individual = mutz(individual)
    return individual


# In[7]:


def ind2route(individual, instance):
    '''gavrptw.core.ind2route(individual, instance)'''
    route = []
    vehicle_capacity = instance['vehicle_capacity'][0]
    ptr = 0
    depart_due_time = instance['due_time'][ instance['bus_starts'][0] ]
    tot_bus = instance['number_busses']
    # Initialize a sub-route
    sub_route = []
    vehicle_load = 0
    elapsed_time = 0
    last_customer_id = instance['bus_starts'][ptr]
    for customer_id in individual:
        customer = instance['valid_stations'][customer_id]
        demand = instance['demand'][customer]
        updated_vehicle_load = vehicle_load + demand
        # Update elapsed time
        #service_time = instance[f'customer_{customer_id}']['service_time']
        return_time = instance['distance_matrix'][customer][ instance['bus_ends'][ptr] ]
        updated_elapsed_time = elapsed_time +             instance['distance_matrix'][last_customer_id][customer] + return_time
        # Validate vehicle load and elapsed time
        if (((updated_vehicle_load <= vehicle_capacity) and (updated_elapsed_time <= depart_due_time)) or (ptr + 1 == tot_bus)):
            # Add to current sub-route
            sub_route.append(customer)
            vehicle_load = updated_vehicle_load
            elapsed_time = updated_elapsed_time - return_time
        else:
            # Save current sub-route
            route.append(sub_route)
            # Initialize a new sub-route and add to it
            sub_route = [customer]
            vehicle_load = demand
            ptr += 1
            vehicle_capacity = instance['vehicle_capacity'][ptr]
            elapsed_time = instance['distance_matrix'][ instance['bus_starts'][ptr] ][customer]
        # Update last customer ID
        last_customer_id = customer
    if sub_route != []:
        # Save current sub-route before return if not empty
        route.append(sub_route)
    return route


# In[8]:


def print_route(route, instance, base_solution,merge=False):
    '''gavrptw.core.print_route(route, merge=False)'''
    route_str = '0'
    sub_route_count = 0
    bestr = 'bus_ends'
    not_avail = 'not_avilable'
    final_routes = {}
    final_routes['routes'] = []
    totload = 0
    timesum = 0
    for sub_route in route:
        sub_route_count += 1
        curbus = instance['perm'][sub_route_count-1]
        thisdict = {}
        curload = 0
        route_time = 0
        thisdict['bus'] = curbus
        thisdict['nodes'] = []
        sub_route_str = str(instance['bus_starts'][curbus])
        lastindex = instance['bus_starts'][curbus]
        tmp_dict = {'index': 0, 'load_var': 0, 'max_time_var': 0, 'min_time_var': 0, 'max_slack_var': not_avail, 'min_slack_var': not_avail}
        tmp_dict['index'] = instance['bus_starts'][curbus]
        tmp_dict['load_var'] = 0
        thisdict['nodes'].append(tmp_dict)
        for customer_id in sub_route:
            #customer = instance['valid_stations'][customer_id]
            route_time += instance['distance_matrix'][lastindex][customer_id]
            sub_route_str = f'{sub_route_str} - {customer_id}'
            route_str = f'{route_str} - {customer_id}'
            curload += instance['demand'][customer_id]
            tmp_dict = {'index': 0, 'load_var': 0, 'max_time_var': 0, 'min_time_var': 0, 'max_slack_var': not_avail, 'min_slack_var': not_avail}
            tmp_dict['index'] = customer_id
            tmp_dict['load_var'] = curload
            tmp_dict['min_time_var'] = route_time
            thisdict['nodes'].append(tmp_dict)
            lastindex = customer_id
        sub_route_str = f'{sub_route_str} - {instance[bestr][sub_route_count-1]}'

        tmp_dict = {'index': 0, 'load_var': 0, 'max_time_var': 0, 'min_time_var': 0, 'max_slack_var': not_avail, 'min_slack_var': not_avail}
        route_time += instance['distance_matrix'][lastindex][ instance['bus_ends'][curbus] ]
        tmp_dict['index'] = instance['bus_ends'][curbus]
        tmp_dict['load_var']=curload
        tmp_dict['min_time_var'] = route_time
        thisdict['nodes'].append(tmp_dict)
        thisdict['totalDistance'] = 0
        thisdict['routeLoad'] = curload
        thisdict['totalTime'] = route_time
        thisdict['duration'] = route_time
        final_routes['routes'].append(thisdict)
        timesum += route_time
        totload += curload
        if not merge:
            S = (f'  Vehicle {curbus}\'s route: {sub_route_str}')
            #final_routes.append(S)
        route_str = f'{route_str} - 0'
    final_routes['status']=1
    final_routes['dropped_nodes'] = []
    final_routes['totalDistace'] = 0
    final_routes['totalLoad']=totload
    final_routes['totalTime'] = timesum
    final_routes['empty_vehicle'] = []
    if(len(base_solution) > 0):
        final_routes['pickup'] = base_solution['pickup']
    else:
        final_routes['pickup'] = 1
    if merge:
        print(route_str)
    return final_routes


# In[9]:


def eval_vrptw(individual, instance, time_p=2000, horiz=5000, hor_p=1500,load_p=20000, debg=False):
    '''gavrptw.core.eval_vrptw(individual, instance, unit_cost=1.0, init_cost=0, wait_cost=0,
        delay_cost=0)'''
    time_window_penalty = time_p
    
    horizonz = horiz
    horizonz_penalty = hor_p
    hcost = 0
    load_penalty = load_p
    load_penalty = 20000
    route = ind2route(individual, instance)
    total_cost = 0
    vptr = 0
    for sub_route in route: # every bus route , individually
        sub_route_time_cost = 0
        sub_route_distance = 0
        elapsed_time = 0
        last_customer_id = instance['bus_starts'][vptr]
        #last_customer_id = instance['rev_map'][last_customer_id]
        vcap = instance['vehicle_capacity'][vptr]
        route_demand = 0
        hcost = 0
        for customer_id in sub_route:
            # Calculate section distance
            customer = customer_id     ############### same as customer_id ###########################
            distance = instance['distance_matrix'][last_customer_id][customer]
            # Update sub-route distance
            if(sub_route_distance <= horizonz and sub_route_distance + distance > horizonz):
                hcost += horizonz_penalty
            sub_route_distance = sub_route_distance + distance
            # Calculate time cost
            arrival_time = elapsed_time + distance
            route_demand += instance['demand'][customer]

            time_cost = 0
            if(arrival_time < instance['ready_time'][customer] or arrival_time > instance['due_time'][customer]):
                time_cost = time_window_penalty
            # Update sub-route time cost
            sub_route_time_cost = sub_route_time_cost + time_cost
            
            elapsed_time = arrival_time
            last_customer_id = customer
        # Calculate transport cost
        sub_route_distance = sub_route_distance + instance['distance_matrix'][last_customer_id][instance['bus_ends'][vptr]]
        #sub_route_transport_cost = init_cost + unit_cost * sub_route_distance
        # Obtain sub-route cost
        sub_route_cost = sub_route_time_cost + sub_route_distance
        if(route_demand > vcap):
            if(debg):
                print('Busses that go bad >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ')
                print(instance['perm'][vptr])
                print(vcap, route_demand)
            sub_route_cost += (route_demand - vcap)*load_penalty
        # Update total cost
        total_cost = total_cost + sub_route_cost + hcost
        vptr += 1
    if(total_cost == 0):
        # total cost zero is not ever going to happen, will only happen if
        # the route is completely empty, we dont want this, hence fitness is less
        print('Fucked up shit happening\n\n\n')
        total_cost= 1e18
    fitness = 1.0 / total_cost
    return (fitness, )


# In[10]:


def cx_partialy_matched(ind1, ind2):
    '''gavrptw.core.cx_partialy_matched(ind1, ind2)'''
    size = min(len(ind1), len(ind2))
    cxpoint1, cxpoint2 = sorted(random.sample(range(size), 2))
    temp1 = ind1[cxpoint1:cxpoint2+1] + ind2
    temp2 = ind1[cxpoint1:cxpoint2+1] + ind1
    ind1 = []
    for gene in temp1:
        if gene not in ind1:
            ind1.append(gene)
    ind2 = []
    for gene in temp2:
        if gene not in ind2:
            ind2.append(gene)
    return ind1, ind2


# In[11]:


def run_gavrptw(data, cx_pb, mut_pb, n_gen,initRoute=False, base_solution={}, pop_size = 400,      time_p=2000, horiz=10000, hor_p=1500,load_p=20000):
    '''gavrptw.core.run_gavrptw(instance_name, unit_cost, init_cost, wait_cost, delay_cost,
        ind_size, pop_size, cx_pb, mut_pb, n_gen, export_csv=False, customize_data=False)'''
    # print("basse")
    # print(base_solution)
    instance = load_data(data)
    #print(instance)
    actual_size = instance['good_nodes']
    
    
    # take a second look at this
    ind_size = instance['tot_stops']
    
    
    
    creator.create('FitnessMax', base.Fitness, weights=(1.0,))
    creator.create('Individual', list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()
    # Attribute generator


    if(initRoute):
        base_individual = converts(base_solution, instance)
    # print("baseee")
    # print(base_individual)
    if(initRoute):
        toolbox.register('indexes', initPopulation, baze = base_individual)
    else:
        toolbox.register('indexes', random.sample, range(0, actual_size), actual_size)
    
    # Structure initializers
    toolbox.register('individual', tools.initIterate, creator.Individual, toolbox.indexes)
    
    
    
    
    toolbox.register('population', tools.initRepeat, list, toolbox.individual)
    #toolbox.register('population', initPopulation, list, toolbox.individual)
    
    
    # time_p=2000, horiz=5000, hor_p=1500,load_p=20000
    # Operator registering
    toolbox.register('evaluate', eval_vrptw, instance=instance, time_p = time_p, horiz = horiz, hor_p = hor_p,load_p = load_p)
    toolbox.register('select', tools.selRoulette)
    toolbox.register('mate', cx_partialy_matched)
    toolbox.register('mutate', mut_inverse_indexes)
    
    
    #change this too in case you want custom initial population
    pop = toolbox.population(n=pop_size)
    
    
    # Results holders for exporting results to CSV file
    csv_data = []
    print('Start of evolution')
    #print(' &&&&&&&&&&&&&&&&&&&&&&&&&&&& ')
    #print(len(pop))
    
    #print(pop)
    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    #print(fitnesses)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    print(f'  Evaluated {len(pop)} individuals')
    # Begin the evolution
    for gen in range(n_gen):
        print(f'-- Generation {gen} --')
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        #print(type(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))
        #print(offspring)
        
        # Apply crossover and mutation on the offspring
        #print('$$$$$$$$$$$$$$$$$ ', len(offspring))
        packz = zip(offspring[::2], offspring[1::2])
        #print('$$$$$$$$$$$$$$$$$$$$$$$ ', packz.size)
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            #print(len(offspring) , '  ------  ', len(offspring) )
            if random.random() < cx_pb:
                #print(len(child1), ' $$$$$$$$$$$$$$$$$$$$$ ', len(child2))
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
        for mutant in offspring:
            if random.random() < mut_pb:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        print(f'  Evaluated {len(invalid_ind)} individuals')
        # The population is entirely replaced by the offspring
        pop[:] = offspring
        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]
        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5
        print(f'  Min {min(fits)}')
        print(f'  Max {max(fits)}')
        print(f'  Avg {mean}')
        print(f'  Std {std}')
        
        
    print('-- End of (successful) evolution --')
    best_ind = tools.selBest(pop, 1)[0]
    eval_vrptw(best_ind, instance, debg=True)
    print(f'Best individual: {best_ind}')
    print(f'Fitness: {best_ind.fitness.values[0]}')
    print(f'Total cost: {1 / best_ind.fitness.values[0]}')

    return print_route(ind2route(best_ind, instance), instance = instance, base_solution = base_solution)
    

##
# # In[12]:


# dataz = {'duration_matrix': [[0, 0, 5336, 2694, 4559], [0, 0, 5336, 2694, 4559], [5261, 5261, 0, 6381, 6962], [3010, 3010, 5083, 0, 3343], [4547, 4547, 6935, 2368, 0]], 'pickup': 1, 'passengerCount': [0, 0, 12, 13, 14], 'busCapacity': [15, 15, 10, 16], 'time_windows': [(0, 200), (0, 200), (0, 200), (0, 200), (0, 200)], 'starts': [0, 0, 0, 0], 'ends': [1, 1, 1, 1], 'max_allowed_time': 10000, 'soft_time_windows': [(0, 200), (0, 200), (0, 200), (0, 200), (0, 200)], 'soft_min_occupancy': [12, 12, 8, 13]}


# # In[13]:


# dataz['duration_matrix']
# dataz['time_windows'] = [(0,50000) for i in range(5)]


# # In[14]:


# dataz


# # In[15]:

# ans=run_gavrptw(dataz, 0.85, 0.02,50)

# print(ans)

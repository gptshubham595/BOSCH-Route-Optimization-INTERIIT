from django.shortcuts import render
from django.urls import reverse_lazy
from .models import CrudUser
from django.views.generic import TemplateView, View, DeleteView
from django.core import serializers
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .RouteOptimization import mySolver
from .vrp_capacity import solver
import utm
from .ga_sbrp import run_gavrptw
#import requests
import json
import urllib
from urllib.request import urlopen
from  geopy.geocoders import Nominatim
from .stop_assign import assign_stops
#import pandas as pd
import random 
import pickle
from .ga_sbrp import run_gavrptw
buscap=[]
count=[]
num_vehicles=0
def FrontView(request):
    users=CrudUser.objects.all()
    # mySolver()
    return render(request,'front_page.html',{'users':users})




# please pass the locations in the form [office_location, other bus stops, ...]
class BusStopSelection(View):
    def post(self, request):
        passengerDetails=json.loads(request.POST['passenger'])

        # #############################################################
        # MAKE SURE THAT potentialBusStops[0] is office location
        # as it wont be considered as a bus stop while assigning people
        potentialBusStops=json.loads(request.POST['busStops'])
        # read the above note
        # #############################################################


        print(' >>>>>>>>>>>>>>>>>>>>\n')
        print(passengerDetails)
        print(' <<<<<<<<<<<<<<<<<<<<\n')
        print(potentialBusStops)
        inf = 10000000000000000
        geolocator = Nominatim()
        stud_data = {}
        stop_data = {}
        times = []
        for j in range(len(passengerDetails)):
            #stud_data[j] = geolocator.geocode(passengerDetails[j]['pickup'])
            loc = geolocator.geocode(passengerDetails[j]['pickup'])
            X,Y,Z,D = utm.from_latlon(loc.latitude, loc.longtitude)
            stud_data[j] = (X, Y)
            print(j , passengerDetails[j]['pickup'], stud_data[j])
            times.append((passengerDetails[j]['start_time']  ,  passengerDetails[j]['end_time']))


        for j in range(len(potentialBusStops)):
            loc = geolocator.geocode(potentialBusStops[j])
            X,Y,Z,D = utm.from_latlon(loc.latitude, loc.longtitude)
            stop_data[j] = (X, Y)


        # create final map


        assignment, tw = assign_stops(stud_data, stop_data, 20000, 20, times)

        data = {}
        data['bus_stop_info'] = {}
        for j in range(len(potentialBusStops)):
            data['bus_stop_info'][potentialBusStops[j]] = {}
            data['bus_stop_info'][potentialBusStops[j]]['psngrCount'] = counts[j]
            if(j in tw):
                data['bus_stop_info'][potentialBusStops[j]]['time_window'] = tw[j]
            else:
                data['bus_stop_info'][potentialBusStops[j]]['time_window'] = (0, inf)

        
        data['student_info'] = {}
        for j in range(len(passengerDetails)):
            data['student_info'][j] = potentialBusStops[assignment[j]]

        return JsonResponse(data)    



def create_distance_matrix(data):
    addresses = data["addresses"]
    API_key = data["API_key"]
    # Distance Matrix API only accepts 100 elements per request, so get rows in multiple requests.
    max_elements = 100
    num_addresses = len(addresses) # 16 in this example.
    # Maximum number of rows that can be computed per request (6 in this example).
    max_rows = max_elements // num_addresses
    # num_addresses = q * max_rows + r (q = 2 and r = 4 in this example).
    q, r = divmod(num_addresses, max_rows)
    dest_addresses = addresses
    distance_matrix = []
    duration_matrix =[]
    # Send q requests, returning max_rows rows per request.
    for i in range(q):
        origin_addresses = addresses[i * max_rows: (i + 1) * max_rows]
        # print("origin address###############")
        # print(i)
        print(origin_addresses)
        response = send_request(origin_addresses, dest_addresses, API_key)
        distance_matrix += build_distance_matrix(response)
        duration_matrix += build_duration_matrix(response)

    # Get the remaining remaining r rows, if necessary.
    if r > 0:
        origin_addresses = addresses[q * max_rows: q * max_rows + r]
        print("origin address###############")
        # print(i)
        print(origin_addresses)
        response = send_request(origin_addresses, dest_addresses, API_key)
        distance_matrix += build_distance_matrix(response)
        duration_matrix += build_duration_matrix(response)
    return distance_matrix,duration_matrix


def send_request(origin_addresses, dest_addresses, API_key):
    """ Build and send request for the given origin and destination addresses."""
    def build_address_str(addresses):
        # Build a pipe-separated string of addresses
        address_str = ''
        for i in range(len(addresses) - 1):
            address_str += addresses[i] + '|'
        address_str += addresses[-1]
        return address_str

    request = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial'
    origin_address_str = build_address_str(origin_addresses)
    dest_address_str = build_address_str(dest_addresses)
    request = request + '&origins=' + origin_address_str + '&destinations=' + \
                        dest_address_str + '&key=' + API_key
    # print("request#####")
    # print(request)
    jsonResult = urlopen(request).read()
    # print("jsonresult")
    # print(jsonResult)
    response = json.loads(jsonResult)
    return response


def build_distance_matrix(response):
    print("response#############")
    print(response)
    distance_matrix = []
    for row in response['rows']:
        print("row===================")
        print(row['elements'])
        row_list = [row['elements'][j]['distance']['value'] for j in range(len(row['elements']))]
        distance_matrix.append(row_list)
    print("build complete")
    return distance_matrix  


def build_duration_matrix(response):
    print("response#############")
    print(response)
    distance_matrix = []
    for row in response['rows']:
        print("row2===================")
        print(row['elements'])
        row_list = [row['elements'][j]['duration']['value'] for j in range(len(row['elements']))]
        distance_matrix.append(row_list)
    print("build2 complete")
    return distance_matrix  


class RouteView(View):
    def post(self, request):
        print(request.POST)
        locations=json.loads(request.POST['locations'])
        print("locations#####")
        print(locations)
        busdetails=json.loads(request.POST['busdetails'])
        starts = json.loads(request.POST['starts'])
        ends = json.loads(request.POST['ends'])
        # pickup = json.loads(request.POST['pickup'])
        pickup = 1
        previous_result = json.loads(request.POST['previous_result2'])
        print(locations)
        print("BUS=====================")
        print(busdetails)

        passengerPerStop=[]
        busCapacity=[]
        dataForSolver={}
        dataForDistanceMatrix = {}

        dataForDistanceMatrix['API_key'] = 'AIzaSyDmwBs8dSuwg56fTWsbJyMdrvXYU3_Pim4'
        dataForDistanceMatrix['addresses']=[]

        for i in range(0,len(locations)):
            x=locations[i]['name'].replace(", ", "+").replace(" ","+").replace(".","+").replace(")","+").replace("(","+")
            dataForDistanceMatrix['addresses'].append(x)
            passengerPerStop.append(int(locations[i]['count']))

        dataForDistanceMatrix['addresses']=list(dataForDistanceMatrix['addresses'])    
        print("dataForDistanceMatrix")
        print(dataForDistanceMatrix)
        
        distance_matrix,duration_matrix = create_distance_matrix(dataForDistanceMatrix)   
        print("dist")
        print(distance_matrix)
        
        for i in range(0,len(busdetails)):
            busCapacity.append(int(busdetails[i]['buscapacity']))

        dataForSolver['distance_matrix']=distance_matrix
        dataForSolver['pickup'] = pickup
        dataForSolver['passengerCount']=passengerPerStop
        dataForSolver['busCapacity']=busCapacity
        dataForSolver['time_windows']=[(0,200)]*len(locations)
        dataForSolver['starts'] = starts
        dataForSolver['ends'] = ends
        dataForSolver['max_allowed_time'] = 120
        dataForSolver['soft_time_windows'] = dataForSolver['time_windows']
        dataForSolver['soft_min_occupancy'] = [int((85/100)*x) for x in dataForSolver['busCapacity']]
        dataForSolver['previous_result'] = previous_result
        dataForSolver['duration_matrix'] = [ [y//60 for y in x] for x in duration_matrix ]
        dataForSolver['hard_min_occupancy'] = []
        results = {}
        if previous_result['ga'] == True:
            results = run_gavrptw(dataForSolver,0.85,0.02,100,True,previous_result)
        else:
            print("before solver")
            results=solver(dataForSolver)
            print("after solver")
        print("printing optimal route")
        print(results)
        new_results = run_gavrptw(data = dataForSolver, cx_pb=0.85, mut_pb=0.02, n_gen=50, time_p=0, hor_p=0, initRoute=False, base_solution = results)
        print('New results ==========================>')
        print(new_results)
        print('\n\n')
        #print(x[0]["name"])
        #x[{},{}]

        # data={'lat':22.2,'lng':77.8,'arr':12,'depa':32,'count':20}

        # useGA = True
        # if(useGA):
        #     results = new_results


        routes=[]
        print("results")
        print(results)
        for i in range(0,len(results['routes'])): #for each route
            route={}
            route['bus']="NH123"
            route['color']="red"    
            route['type']=results['pickup']
            route['nodes']=[]
            route['distance'] = 0
            previous_index = results['routes'][i]['nodes'][0]['index']
            for j in range(0,len(results['routes'][i]['nodes'])): # for each stop
                node={}
                stopIndex=results['routes'][i]['nodes'][j]['index']
                node['index'] = stopIndex
                route['distance'] += dataForSolver['distance_matrix'][previous_index][stopIndex]
                node['lat']=locations[stopIndex]['lat']
                node['lng']=locations[stopIndex]['lng']
                node['load']=results['routes'][i]['nodes'][j]['load_var']
                try:
                    node['max_slack']=results['routes'][i]['nodes'][j]['max_slack_var']
                    node['min_slack']=results['routes'][i]['nodes'][j]['min_slack_var']
                except:
                    node['max_slack']=0
                    node['min_slack']=0
                node['max_time']=results['routes'][i]['nodes'][j]['max_time_var']
                node['min_time']=results['routes'][i]['nodes'][j]['min_time_var']
                route['nodes'].append(node)    
            routes.append(route)
        print(routes)
        # route={}
        # route['bus']="NH123"
        # route['color']="red"
        # route['type']="pickup/drop"
        # route['nodes']=[]
        # for i in range(0,len(locations)):
        #     route['nodes'].append(locations[i])
        #     count.append(int(locations[i]['count']))
        # print("PSNGR NO ================")    
        # print(count)
        # for i in range(0,len(busdetails)):
        #     # route['bus'].append(busdetails[i])
        #     buscap.append(int(busdetails[i]['buscapacity']))
        # print("buscapacity================")    
        # print(buscap)
        # num_vehicles=len(buscap)
        # routes.append(route)
        # data['routes']=routes
        # # data['routes']=route['nodes'] 

        # print("ROUTES==================================")
        # # print(routes[len(routes)]['nodes'][len(routes[0]['nodes'])]['name'])
        # print(routes[0]['nodes'][0]['name'])
        # print(routes[0]['nodes'][0]['name'].replace(", ", "+"))
        # print("ROUTES=============OVER=================")   
        data={}
        data['routes']=routes
        data['empty_vehicle'] = results['empty_vehicle']
        data['dropped_nodes'] = results['dropped_nodes']
        print("DROPPED NODE==================================")
        print(data['dropped_nodes'])
        data['status'] = results['status']
        data['pickup'] = results['pickup'] 
        data['locations'] = locations
        print("DATA++++++++=========================")
        print(data)
        # print(data['routes'][0]['nodes'])
        return JsonResponse(data)


class CrudView(TemplateView):
    template_name = 'crud_ajax/crud.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = CrudUser.objects.all()
        return context


class CreateCrudUser(View):
    def  get(self, request):
        name1 = request.GET.get('name', None)
        address1 = request.GET.get('address', None)
        age1 = request.GET.get('age', None)

        obj = CrudUser.objects.create(
            name = name1,
            address = address1,
            age = age1
        )

        user = {'id':obj.id,'name':obj.name,'address':obj.address,'age':obj.age}

        data = {
            'user': user
        }
        print(user)
        return JsonResponse(data)

class DeleteCrudUser(View):
    def  get(self, request):
        id1 = request.GET.get('id', None)
        usr=CrudUser.objects.get(id=id1)
        location=usr.name
        print(location)
        usr.delete()

        print("STARTED INIT!!");
        data = {
            'deleted': True,
            'location':location
        }
        return JsonResponse(data)


class UpdateCrudUser(View):
    def  get(self, request):
        id1 = request.GET.get('id', None)
        name1 = request.GET.get('name', None)
        address1 = request.GET.get('address', None)
        age1 = request.GET.get('age', None)

        obj = CrudUser.objects.get(id=id1)
        obj.name = name1
        obj.address = address1
        obj.age = age1
        obj.save()

        user = {'id':obj.id,'name':obj.name,'address':obj.address,'age':obj.age}

        data = {
            'user': user
        }
        return JsonResponse(data)

def SimulationView(request):  
    return render(request,'simulation.html',)

class SimulatorView(View):
    def post(self, request):
        dataIndex=json.loads(request.POST['index'])
        starts = json.loads(request.POST['starts'])
        ends = json.loads(request.POST['ends'])
        previous_result = json.loads(request.POST['previous_result2'])
        previndex=dataIndex
        increment=random.choice([0,1])
        dataIndex=(dataIndex+increment)%3
        # print("index",dataIndex)
        dbfile = open('SimulationData', 'rb')      
        db = pickle.load(dbfile) 
        dbfile.close() 
        currData=db[dataIndex]
        # print(currData)
        dataForSolver={}
        routeBetweenIJ=[]
        allRoutes=[]
        
        dataForSolver['distance_matrix']=[]
        for i in range(0,len(currData['CostMatrix'])):
            distanceFromI=[]
            routeFromI=[]
            for j in range(0,len(currData['CostMatrix'][i])):
                minCostRouteIJ=100000000000
                intermediateRoute=[]
                for k in range(0,len(currData['CostMatrix'][i][j])):
                    currIntermediateRouteWithBusStop=[]
                    currIntermediateRouteWithBusStop.append(currData['busStopDetails'][i])
                    for l in range(0,len(currData['CostMatrix'][i][j][k]['intermediateNodes'])):
                        currIntermediateRouteWithBusStop.append(currData['CostMatrix'][i][j][k]['intermediateNodes'][l])
                    if currData['CostMatrix'][i][j][k]['distTotal']<minCostRouteIJ:
                        minCostRouteIJ=currData['CostMatrix'][i][j][k]['distTotal']
                        intermediateRoute=currData['CostMatrix'][i][j][k]['intermediateNodes']
                    currIntermediateRouteWithBusStop.append(currData['busStopDetails'][j])
                    allRoutes.append(currIntermediateRouteWithBusStop)
                distanceFromI.append(minCostRouteIJ)
                routeFromI.append(intermediateRoute)
            dataForSolver['distance_matrix'].append(distanceFromI)
            routeBetweenIJ.append(routeFromI)
        # print(dataForSolver['distance_matrix'])
        dataForSolver['passengerCount']=[]
        for i in range(0,len(currData['busStopDetails'])):
            dataForSolver['passengerCount'].append(currData['busStopDetails'][i]['passengerCount'])
        dataForSolver['busCapacity']=[]
        for i in range(0,len(currData['busDetails'])):
            dataForSolver['busCapacity'].append(currData['busDetails'][i]['capacity'])

        dataForSolver['time_windows']=[(0,200)]*len(currData['busStopDetails'])
        dataForSolver['pickup'] = 1
        dataForSolver['starts'] = starts
        dataForSolver['ends'] = ends
        dataForSolver['max_allowed_time'] = 120
        dataForSolver['soft_time_windows'] = dataForSolver['time_windows']
        dataForSolver['soft_min_occupancy'] = [int((85/100)*x) for x in dataForSolver['busCapacity']]
        dataForSolver['duration_matrix'] = dataForSolver['distance_matrix']
        dataForSolver['hard_min_occupancy'] = []
        dataForSolver['previous_result'] = previous_result
        
        output=solver(dataForSolver)
        result=output['routes']
        
        # print("RESult=========")
        # print(result)
        data={}
        routes=[]
        for i in range(0,len(result)):
            route=[]
            # print("getting new route")
            node={}
            node['type']='busStop'
            busStopIndex=result[i]['nodes'][0]['index']
            node['lat']=currData['busStopDetails'][busStopIndex]['lat']
            node['lng']=currData['busStopDetails'][busStopIndex]['lng']
            node['load']=result[i]['nodes'][0]['load_var']
            route.append(node)
            for j in range(1,len(result[i]['nodes'])):
                
                busStopIndex=result[i]['nodes'][j]['index']
                # print(busStopIndex)
                intermediateNode=routeBetweenIJ[result[i]['nodes'][j-1]['index']][result[i]['nodes'][j]['index']]
                for k in range(0,len(intermediateNode)):
                    node={}    
                    node['type']='intermediateStop'
                    node['lat']=intermediateNode[k]['lat']
                    node['lng']=intermediateNode[k]['lng']
                    route.append(node)
                    
                node={}    
                node['type']='busStop'
                node['lat']=currData['busStopDetails'][busStopIndex]['lat']
                node['lng']=currData['busStopDetails'][busStopIndex]['lng']
                node['load']=result[i]['nodes'][j]['load_var']
                route.append(node)
            routes.append(route)
        # print(routes)                    
        # data['updated']=False
        # if increment:
        #     data['updated']=True
        data['updated']=True
        data['routes']=routes
        data['allRoutes']=allRoutes
        data['index']=dataIndex
        return JsonResponse(data)

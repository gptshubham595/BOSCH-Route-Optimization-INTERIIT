import math
import pickle
import random
BasicInstance={}
BasicInstance['officeDetails']={
    'lat':30,
    'lng':-40
}
BasicInstance['startDetails']={
    'lat':-10,
    'lng':20
}
BasicInstance['busDetails']=[
    {
        'name':'VOLVO1',
        'capacity':36
    },
    {
        'name':'VOVLO4',
        'capacity':36
    },
    {
        'name':'VOVLO5',
        'capacity':36
    },
    {
        'name':'VOVLO6',
        'capacity':36
    }
]
BasicInstance['busStopDetails']=[
    {
        #start
        'passengerCount':0,
        'lat':30,
        'lng':-40
    },
    {
        #depot
        'passengerCount':0,
        'lat':-10,
        'lng':20
    },
    {
        'passengerCount':16,
        'lat':0,
        'lng':0,
    },
    {
        'passengerCount':10,
        'lat':-10,
        'lng':0,
    },
    {
        'passengerCount':15,
        'lat':10,
        'lng':0,
    },
    {
        'passengerCount':20,
        'lat':0,
        'lng':10,
    },
    {
        'passengerCount':20,
        'lat':0,
        'lng':-10,
    },
    {
        'passengerCount':15,
        'lat':10,
        'lng':10,   
    }
]
BasicInstance['CostMatrix']=[]
for j in range(0,len(BasicInstance['busStopDetails'])):
    distanceFromJ=[]
    print("J===",j)
    for k in range(0,len(BasicInstance['busStopDetails'])):
        print("k===",k)
        distanceBetweenIJ=[]
        numRoutesBetweenIJ=random.randint(1,3)
        for l in range(0,numRoutesBetweenIJ):
            print("L===",l)
            route={}
            distTotal=0
            timeTotal = 0
            #k7l1m1
            route['intermediateNodes']=[]
            numIntermidiate=random.randint(1,1)
            prev = [BasicInstance['busStopDetails'][j]['lat'] , BasicInstance['busStopDetails'][j]['lng']]
            for m in range(0,numIntermidiate):
                print("M===",m)
                intermediateNode={}
                x1 = BasicInstance['busStopDetails'][j]['lat']
                x1 += BasicInstance['busStopDetails'][k]['lat']
                x1 /= 2

                y1 = BasicInstance['busStopDetails'][j]['lng']
                y1 += BasicInstance['busStopDetails'][k]['lng']
                y1 /= 2

                offset = 1

                costhe = random.random()
                sinthe = math.sqrt(1 - costhe*costhe)

                radius = random.random() * offset

                newX = x1 + costhe*radius
                newY = y1 + sinthe*radius
                D = (newX - prev[0])**2 + (newY-prev[1])**2
                distTotal += math.sqrt(D)
                prev = [newX, newY]
                # print("distance", D)
                speed = random.randint(40, 100)
                timeTotal += (( math.sqrt(D)) / speed)*60
                # intermediateNode['dist']=random.randint(0, 4)
                intermediateNode['lat']= newX
                intermediateNode['lng']= newY
                route['intermediateNodes'].append(intermediateNode)
            print("############")    
            print(distTotal) 
            print(timeTotal)   
            route['distTotal']=distTotal
            route['timeTotal']=timeTotal   
            distanceBetweenIJ.append(route)
        distanceFromJ.append(distanceBetweenIJ)
    BasicInstance['CostMatrix'].append(distanceFromJ)
# print(BasicInstance)
Instances={}
for i in range(0,2):
    Instance={}
    Instance['officeDetails']=BasicInstance['officeDetails']
    Instance['startDetails']=BasicInstance['startDetails']
    Instance['busDetails']=BasicInstance['busDetails']
    Instance['busStopDetails']=BasicInstance['busStopDetails']
    Instance['CostMatrix']=BasicInstance['CostMatrix']
    for j in range(0,len(Instance['CostMatrix'])):
        print("J======",j)
        for k in range(0,len(Instance['CostMatrix'][j])):
            print("K======",k)
            for l in range(0,len(Instance['CostMatrix'][j][k])):
                print("L======",l)
                currTime=Instance['CostMatrix'][j][k][l]['timeTotal']
                print("=============")
                print(currTime)
                ran=random.random()
                print(ran)
                if ran>0.75:
                    ran=10  
                currTime=currTime+currTime*ran
                print(currTime)
                Instance['CostMatrix'][j][k][l]['timeTotal']=currTime
    Instances[i]=Instance    
dbfile = open('SimulationData', 'wb') 
# source, destination 
pickle.dump(Instances, dbfile)                      
dbfile.close()        
# Instances={}
# for i in range(0,10):
#     Instance={}
#     Instance['officeDetails']={
#         'lat' : 0,
#         'lng': 0
#     }
#     Instance['startDetails']={
#         'lat':random.random()*100,
#         'lng':random.random()*100
#     }
#     Instance['busDetails']=[
#         {
#             'name':'VOLVO1',
#             'capacity':15
#         },
#         {
#             'name':'VOVLO4',
#             'capacity':10
#         },
#         {
#             'name':'VOVLO2',
#             'capacity':10
#         },
#         {
#             'name':'VOLVO3',
#             'capacity':15
#         }
#     ]
#     Instance['busStopDetails']=[
#         {
#             'passengerCount':7,
#             'lat':10.908126, 
#             'lng':77.547909
#         },
#         {
#             'passengerCount':2,
#             'lat':12.902504, 
#             'lng':78.518625
#         },
#         {
#             'passengerCount':2,
#             'lat':15.907055, 
#             'lng':79.519618
#         },
#         {
#             'passengerCount':4,
#             'lat':13.933152, 
#             'lng': 77.550016
#         },
#         {
#             'passengerCount':5,
#             'lat':12.919742, 
#             'lng':76.542100
#         },
#         {

#             'passengerCount':5,
#             'lat':13.930625, 
#             'lng':76.553374
#         },
#         {

#             'passengerCount':5,
#             'lat':12.923682, 
#             'lng':77.553366
#         },
#         {

#             'passengerCount':5,
#             'lat':15.909265, 
#             'lng':77.558069
#         }
#     ]
#     Instance['durationMatrix']=[]
#     Instance['CostMatrix']=[]
#     for .j in range(0,len(Instance['busStopDetails'])):
#         distanceFromJ=[]
#         for k in range(0,len(Instance['busStopDetails'])):
#             distanceBetweenIJ=[]
#             numRoutesBetweenIJ=random.randint(1,3)
#             for l in range(0,numRoutesBetweenIJ):
#                 route={}
#                 distTotal=0
#                 timeTotal = 0
#                 route['intermediateNodes']=[]
#                 numIntermidiate=random.randint(0,2)
#                 prev = [Instance['busStopDetails'][j]['lat'] , Instance['busStopDetails'][j]['lng']]
#                 for m in range(0,numIntermidiate):
#                     intermediateNode={}
#                     x1 = Instance['busStopDetails'][j]['lat']
#                     x1 += Instance['busStopDetails'][k]['lat']
#                     x1 /= 2

#                     y1 = Instance['busStopDetails'][j]['lng']
#                     y1 += Instance['busStopDetails'][k]['lng']
#                     y1 /= 2

#                     offset = 0.05

#                     costhe = random.random()
#                     sinthe = math.sqrt(1 - costhe*costhe)

#                     radius = random.random() * offset

#                     newX = x1 + costhe*radius
#                     newY = y1 + sinthe*radius
#                     D = (newX - prev[0])**2 + (newY-prev[1])**2
#                     distTotal += math.sqrt(D) * 111000
#                     prev = [newX, newY]

#                     speed = random.randint(40, 100)
#                     timeTotal += ((111 * math.sqrt(D)) / speed)*60
#                     # intermediateNode['dist']=random.randint(0, 4)
#                     intermediateNode['lat']= newX
#                     intermediateNode['lng']= newY
#                     route['intermediateNodes'].append(intermediateNode)
#                 route['distTotal']=distTotal   
#                 distanceBetweenIJ.append(route)
#             distanceFromJ.append(distanceBetweenIJ)
#         Instance['CostMatrix'].append(distanceFromJ)    
#     Instances[i]=Instance
#     # print(Instance)
# dbfile = open('SimulationData', 'wb') 
# # source, destination 
# pickle.dump(Instances, dbfile)                      
# dbfile.close()     
# import pickle
# import random
# Instances={}
# for i in range(0,3):
#     Instance={}
#     Instance['officeDetails']={
#         'lat':random.random()*100,
#         'lng':random.random()*100
#     }
#     Instance['startDetails']={
#         'lat':random.random()*100,
#         'lng':random.random()*100
#     }
#     Instance['busDetails']=[
#         {
#             'name':'MH123',
#             'capacity':36
#         },
#         {
#             'name':'MH143',
#             'capacity':36
#         }
#     ]
#     Instance['busStopDetails']=[
#         {
#             'passengerCount':16,
#             'lat':random.random()*100,
#             'lng':random.random()*100,
#         },
#         {
#             'passengerCount':10,
#             'lat':random.random()*100,
#             'lng':random.random()*100,
#         },
#         {
#             'passengerCount':15,
#             'lat':random.random()*100,
#             'lng':random.random()*100,
#         },
#         {
#             'passengerCount':20,
#             'lat':random.random()*100,
#             'lng':random.random()*100,
#         },
#         {
#             'passengerCount':26,
#             'lat':random.random()*100,
#             'lng':random.random()*100,
#         }
#     ]
#     Instance['CostMatrix']=[]
#     for j in range(0,len(Instance['busStopDetails'])):
#         distanceFromJ=[]
#         for k in range(0,len(Instance['busStopDetails'])):
#             distanceBetweenIJ=[]
#             numRoutesBetweenIJ=random.randint(1,5)
#             for l in range(0,numRoutesBetweenIJ):
#                 route={}
#                 route['distTotal']=random.randint(0,20)
#                 route['intermediateNodes']=[]
#                 numIntermidiate=random.randint(1,5)
#                 for m in range(0,numIntermidiate):
#                     intermediateNode={}
#                     intermediateNode['dist']=random.randint(0, 4)
#                     intermediateNode['lat']=random.random()*100
#                     intermediateNode['lng']=random.random()*100
#                     route['intermediateNodes'].append(intermediateNode)
#                 distanceBetweenIJ.append(route)
#             distanceFromJ.append(distanceBetweenIJ)
#         Instance['CostMatrix'].append(distanceFromJ)    

#     Instances[i]=Instance
# dbfile = open('SimulationData', 'wb') 
# # source, destination 
# pickle.dump(Instances, dbfile)                      
# dbfile.close() 



# import math
# import pickle
# import random
# Instances={}
# for i in range(0,10):
#     Instance={}
#     Instance['officeDetails']={
#         'lat' : 0,
#         'lng': 0
#     }
#     Instance['startDetails']={
#         'lat':random.random()*100,
#         'lng':random.random()*100
#     }
#     Instance['busDetails']=[
#         {
#             'name':'VOLVO1',
#             'capacity':15
#         },
#         {
#             'name':'VOVLO4',
#             'capacity':10
#         },
#         {
#             'name':'VOVLO2',
#             'capacity':10
#         },
#         {
#             'name':'VOLVO3',
#             'capacity':15
#         }
#     ]
#     Instance['busStopDetails']=[
#         {
#             'passengerCount':7,
#             'lat':12.908126, 
#             'lng':77.547909
#         },
#         {
#             'passengerCount':2,
#             'lat':12.902504, 
#             'lng':77.518625
#         },
#         {
#             'passengerCount':2,
#             'lat':12.907055, 
#             'lng':77.519618
#         },
#         {
#             'passengerCount':4,
#             'lat':12.933152, 
#             'lng': 77.550016
#         },
#         {
#             'passengerCount':5,
#             'lat':12.919742, 
#             'lng':77.542100
#         },
#         {

#             'passengerCount':5,
#             'lat':12.930625, 
#             'lng':77.553374
#         },
#         {

#             'passengerCount':5,
#             'lat':12.923682, 
#             'lng':77.553366
#         },
#         {

#             'passengerCount':5,
#             'lat':12.909265, 
#             'lng':77.558069
#         }
#     ]
#     Instance['durationMatrix']=[]
#     Instance['CostMatrix']=[]
#     for j in range(0,len(Instance['busStopDetails'])):
#         distanceFromJ=[]
#         for k in range(0,len(Instance['busStopDetails'])):
#             distanceBetweenIJ=[]
#             numRoutesBetweenIJ=random.randint(1,3)
#             for l in range(0,numRoutesBetweenIJ):
#                 route={}
#                 distTotal=0
#                 timeTotal = 0
#                 route['intermediateNodes']=[]
#                 numIntermidiate=random.randint(0,2)
#                 prev = [Instance['busStopDetails'][j]['lat'] , Instance['busStopDetails'][j]['lng']]
#                 for m in range(0,numIntermidiate):
#                     intermediateNode={}
#                     x1 = Instance['busStopDetails'][j]['lat']
#                     x1 += Instance['busStopDetails'][k]['lat']
#                     x1 /= 2

#                     y1 = Instance['busStopDetails'][j]['lng']
#                     y1 += Instance['busStopDetails'][k]['lng']
#                     y1 /= 2

#                     offset = 0.05

#                     costhe = random.random()
#                     sinthe = math.sqrt(1 - costhe*costhe)

#                     radius = random.random() * offset

#                     newX = x1 + costhe*radius
#                     newY = y1 + sinthe*radius
#                     D = (newX - prev[0])**2 + (newY-prev[1])**2
#                     distTotal += math.sqrt(D) * 111000
#                     prev = [newX, newY]

#                     speed = random.randint(40, 100)
#                     timeTotal += ((111 * math.sqrt(D)) / speed)*60
#                     # intermediateNode['dist']=random.randint(0, 4)
#                     intermediateNode['lat']= newX
#                     intermediateNode['lng']= newY
#                     route['intermediateNodes'].append(intermediateNode)
#                 route['distTotal']=distTotal   
#                 distanceBetweenIJ.append(route)
#             distanceFromJ.append(distanceBetweenIJ)
#         Instance['CostMatrix'].append(distanceFromJ)    
#     Instances[i]=Instance
#     # print(Instance)
# dbfile = open('SimulationData', 'wb') 
# # source, destination 
# pickle.dump(Instances, dbfile)                      
# dbfile.close()     
# # import pickle
# # import random
# # Instances={}
# # for i in range(0,3):
# #     Instance={}
# #     Instance['officeDetails']={
# #         'lat':random.random()*100,
# #         'lng':random.random()*100
# #     }
# #     Instance['startDetails']={
# #         'lat':random.random()*100,
# #         'lng':random.random()*100
# #     }
# #     Instance['busDetails']=[
# #         {
# #             'name':'MH123',
# #             'capacity':36
# #         },
# #         {
# #             'name':'MH143',
# #             'capacity':36
# #         }
# #     ]
# #     Instance['busStopDetails']=[
# #         {
# #             'passengerCount':16,
# #             'lat':random.random()*100,
# #             'lng':random.random()*100,
# #         },
# #         {
# #             'passengerCount':10,
# #             'lat':random.random()*100,
# #             'lng':random.random()*100,
# #         },
# #         {
# #             'passengerCount':15,
# #             'lat':random.random()*100,
# #             'lng':random.random()*100,
# #         },
# #         {
# #             'passengerCount':20,
# #             'lat':random.random()*100,
# #             'lng':random.random()*100,
# #         },
# #         {
# #             'passengerCount':26,
# #             'lat':random.random()*100,
# #             'lng':random.random()*100,
# #         }
# #     ]
# #     Instance['CostMatrix']=[]
# #     for j in range(0,len(Instance['busStopDetails'])):
# #         distanceFromJ=[]
# #         for k in range(0,len(Instance['busStopDetails'])):
# #             distanceBetweenIJ=[]
# #             numRoutesBetweenIJ=random.randint(1,5)
# #             for l in range(0,numRoutesBetweenIJ):
# #                 route={}
# #                 route['distTotal']=random.randint(0,20)
# #                 route['intermediateNodes']=[]
# #                 numIntermidiate=random.randint(1,5)
# #                 for m in range(0,numIntermidiate):
# #                     intermediateNode={}
# #                     intermediateNode['dist']=random.randint(0, 4)
# #                     intermediateNode['lat']=random.random()*100
# #                     intermediateNode['lng']=random.random()*100
# #                     route['intermediateNodes'].append(intermediateNode)
# #                 distanceBetweenIJ.append(route)
# #             distanceFromJ.append(distanceBetweenIJ)
# #         Instance['CostMatrix'].append(distanceFromJ)    

# #     Instances[i]=Instance
# # dbfile = open('SimulationData', 'wb') 
# # # source, destination 
# # pickle.dump(Instances, dbfile)                      
# # dbfile.close() 
# import math
# import pickle
# import random
# Instances={}
# for i in range(0,10):
#     Instance={}
#     Instance['officeDetails']={
#         'lat' : 0,
#         'lng': 0
#     }
#     Instance['startDetails']={
#         'lat':random.random()*100,
#         'lng':random.random()*100
#     }
#     Instance['busDetails']=[
#         {
#             'name':'VOLVO1',
#             'capacity':15
#         },
#         {
#             'name':'VOVLO4',
#             'capacity':10
#         },
#         {
#             'name':'VOVLO2',
#             'capacity':10
#         },
#         {
#             'name':'VOLVO3',
#             'capacity':15
#         }
#     ]
#     Instance['busStopDetails']=[
#         {
#             'passengerCount':7,
#             'lat':12.908126, 
#             'lng':77.547909
#         },
#         {
#             'passengerCount':2,
#             'lat':12.902504, 
#             'lng':77.518625
#         },
#         {
#             'passengerCount':2,
#             'lat':12.907055, 
#             'lng':77.519618
#         },
#         {
#             'passengerCount':4,
#             'lat':12.933152, 
#             'lng': 77.550016
#         },
#         {
#             'passengerCount':5,
#             'lat':12.919742, 
#             'lng':77.542100
#         },
#         {

#             'passengerCount':5,
#             'lat':12.930625, 
#             'lng':77.553374
#         },
#         {

#             'passengerCount':5,
#             'lat':12.923682, 
#             'lng':77.553366
#         },
#         {

#             'passengerCount':5,
#             'lat':12.909265, 
#             'lng':77.558069
#         }
#     ]
#     Instance['durationMatrix']=[]
#     Instance['CostMatrix']=[]
#     for j in range(0,len(Instance['busStopDetails'])):
#         distanceFromJ=[]
#         for k in range(0,len(Instance['busStopDetails'])):
#             distanceBetweenIJ=[]
#             numRoutesBetweenIJ=random.randint(1,3)
#             for l in range(0,numRoutesBetweenIJ):
#                 route={}
#                 distTotal=0
#                 timeTotal = 0
#                 route['intermediateNodes']=[]
#                 numIntermidiate=random.randint(0,2)
#                 prev = [Instance['busStopDetails'][j]['lat'] , Instance['busStopDetails'][j]['lng']]
#                 for m in range(0,numIntermidiate):
#                     intermediateNode={}
#                     x1 = Instance['busStopDetails'][j]['lat']
#                     x1 += Instance['busStopDetails'][k]['lat']
#                     x1 /= 2

#                     y1 = Instance['busStopDetails'][j]['lng']
#                     y1 += Instance['busStopDetails'][k]['lng']
#                     y1 /= 2

#                     offset = 0.05

#                     costhe = random.random()
#                     sinthe = math.sqrt(1 - costhe*costhe)

#                     radius = random.random() * offset

#                     newX = x1 + costhe*radius
#                     newY = y1 + sinthe*radius
#                     D = (newX - prev[0])**2 + (newY-prev[1])**2
#                     distTotal += math.sqrt(D) * 111000
#                     prev = [newX, newY]

#                     speed = random.randint(40, 100)
#                     timeTotal += ((111 * math.sqrt(D)) / speed)*60
#                     # intermediateNode['dist']=random.randint(0, 4)
#                     intermediateNode['lat']= newX
#                     intermediateNode['lng']= newY
#                     route['intermediateNodes'].append(intermediateNode)
#                 route['distTotal']=distTotal   
#                 distanceBetweenIJ.append(route)
#             distanceFromJ.append(distanceBetweenIJ)
#         Instance['CostMatrix'].append(distanceFromJ)    
#     Instances[i]=Instance
#     # print(Instance)
# dbfile = open('SimulationData', 'wb') 
# # source, destination 
# pickle.dump(Instances, dbfile)                      
# dbfile.close()     
# # import pickle
# # import random
# # Instances={}
# # for i in range(0,3):
# #     Instance={}
# #     Instance['officeDetails']={
# #         'lat':random.random()*100,
# #         'lng':random.random()*100
# #     }
# #     Instance['startDetails']={
# #         'lat':random.random()*100,
# #         'lng':random.random()*100
# #     }
# #     Instance['busDetails']=[
# #         {
# #             'name':'MH123',
# #             'capacity':36
# #         },
# #         {
# #             'name':'MH143',
# #             'capacity':36
# #         }
# #     ]
# #     Instance['busStopDetails']=[
# #         {
# #             'passengerCount':16,
# #             'lat':random.random()*100,
# #             'lng':random.random()*100,
# #         },
# #         {
# #             'passengerCount':10,
# #             'lat':random.random()*100,
# #             'lng':random.random()*100,
# #         },
# #         {
# #             'passengerCount':15,
# #             'lat':random.random()*100,
# #             'lng':random.random()*100,
# #         },
# #         {
# #             'passengerCount':20,
# #             'lat':random.random()*100,
# #             'lng':random.random()*100,
# #         },
# #         {
# #             'passengerCount':26,
# #             'lat':random.random()*100,
# #             'lng':random.random()*100,
# #         }
# #     ]
# #     Instance['CostMatrix']=[]
# #     for j in range(0,len(Instance['busStopDetails'])):
# #         distanceFromJ=[]
# #         for k in range(0,len(Instance['busStopDetails'])):
# #             distanceBetweenIJ=[]
# #             numRoutesBetweenIJ=random.randint(1,5)
# #             for l in range(0,numRoutesBetweenIJ):
# #                 route={}
# #                 route['distTotal']=random.randint(0,20)
# #                 route['intermediateNodes']=[]
# #                 numIntermidiate=random.randint(1,5)
# #                 for m in range(0,numIntermidiate):
# #                     intermediateNode={}
# #                     intermediateNode['dist']=random.randint(0, 4)
# #                     intermediateNode['lat']=random.random()*100
# #                     intermediateNode['lng']=random.random()*100
# #                     route['intermediateNodes'].append(intermediateNode)
# #                 distanceBetweenIJ.append(route)
# #             distanceFromJ.append(distanceBetweenIJ)
# #         Instance['CostMatrix'].append(distanceFromJ)    

# #     Instances[i]=Instance
# # dbfile = open('SimulationData', 'wb') 
# # # source, destination 
# # pickle.dump(Instances, dbfile)                      
# # dbfile.close() 
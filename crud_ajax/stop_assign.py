#!/usr/bin/env python3

import numpy as np
import random
from .time_window import get_time_windows


class Router():
    def __init__(self, stud_data, stop_data, maxwalk, capacity):
        self.stops = None
        self.students = None
        self.maxwalk = maxwalk
        self.capacity = capacity
        self.student_near_stops = None
        self.stop_near_stops = None
        self.global_path_list = None
        self.global_students_dict = None

        self.assigned_stops_to_stud = None

        self.process_file(stud_data, stop_data)
        self.generate_student_near_stops()
        self.generate_stop_near_stops()
        self.generate_stop_near_students()


    def process_file(self, stud_data, stop_data):
    	#read input file and populate student pickup/drop location and bus potential stop locations in variable students and stops
        #read constraint maxwalk and capacity from file and store
        self.stops = dict()#stop number as key and lat long array as valule
        self.students = dict()
        stops_max = len(stop_data)
        students_max = len(stud_data)
        # with open(fn, 'r') as f:
        #     for num,line in enumerate(f):
        #         if num == 0:
        #             conf = line.split()
        #             stops_max = int(conf[0])
        #             students_max = int(conf[2])
        #             self.maxwalk = float(conf[4])
        #             self.capacity = int(conf[7])
        #         else:
        #             if len(line) < 2:
        #                 ## empty line
        #                 continue
        #             else:
        #                 s_num, s_x, s_y = [float(v) for v in line.split()]
        #                 if (current_stop < stops_max):
        #                     current_stop = current_stop+1
        #                     self.stops[int(s_num)] = np.array([s_x, s_y])
        #                 elif (current_student <= students_max):
        #                     current_student = current_student+1
        #                     self.students[int(s_num)] = np.array([s_x, s_y])

        for stop_n, coord in stop_data.items():
            self.stops[stop_n] = np.array([coord[0], coord[1]])

        for stud_n, coord in stud_data.items():
            self.students[stud_n] = np.array([coord[0], coord[1]])


    def generate_student_near_stops(self):
    	#find all possible stops that can be assigned to a student based on maxwalk distance(i.e take all stops within radius of maxwalk)
    	#given student find walkable stop
        '''Calculate distance between students and stops.
        Assign available stops to student
        out = dict( <student_id> : set( <stop_id>, <stop_id>, <stop_id>, ...)
                    <student_id> : set( <stop_id>, <stop_id>, <stop_id>, ...)
                  )
        '''
        self.student_near_stops = dict()
        for k, v in self.students.items():
            available_stops = set()
            for kk, vv in list(self.stops.items())[1:]:
                
                if np.linalg.norm(v-vv) < self.maxwalk:
                    available_stops.add(kk)
            self.student_near_stops[k] = available_stops

    def generate_stop_near_stops(self):
    	#find 2 matrix similar to distance matrix (find distance between all pair of stops)
        '''Calculate distance between stop and other stops
        out = dict( <stop_id> : tuple( tuple(<stop_id>, <distance>), tuple(<stop_id>, <distance>), ...)
                    <stop_id> : tuple( tuple(<stop_id>, <distance>), tuple(<stop_id>, <distance>), ...)
                  )
        '''
        self.stop_near_stops = dict()
        for k, v in list(self.stops.items())[1:]:
            stops_distances = []
            for kk, vv in list(self.stops.items())[1:]:
                if v is not vv:
                    stops_distances.extend([tuple([kk, np.linalg.norm(v-vv)])])
            self.stop_near_stops[k] = tuple(sorted(stops_distances, key=lambda x:x[1]))

    def generate_stop_near_students(self):
    	#find all students that can walk a stop
    	#given a stop find all students which can walk to that stop
        '''Calculate distance between students and stops.
        Assign available student to stops
        out = dict( <stop_id> : set( <student_id>, <student_id>, <student_id>, ...)
                    <stop_id> : set( <student_id>, <student_id>, <student_id>, ...)
                  )
        '''
        self.stop_near_students = dict()
        for k, v in list(self.stops.items())[1:]:
            if k == 0: continue
            available_students = set()
            for kk, vv in self.students.items():
                if np.linalg.norm(v-vv) < self.maxwalk:
                    available_students.add(kk)
            self.stop_near_students[k] = available_students


    def assign_stops(self):
        self.assigned_stops_to_stud = dict()

        is_assigned_stud = set()
        capacity_till_now = dict()
        list_dist_stud_stop = []

        # Compute distance for all stops walkable by each student
        # and store it in list to be sorted according to minimum distance
        for stud, stop_set in student_near_stops:
            for stop in stop_set:
                a = self.students[stud]
                b = self.stops[stop]
                d = np.linalg.norm(a-b)

                #Tuple format : (distance, student, stop)
                list_dist_stud_stop.append((d, stud, stop))

        # Sort in ascending order for minimum distance first
        list_dist_stud_stop.sort()

        for dist, stud, stop in list_dist_stud_stop:
            #If already assigned stop to student, then skip
            if stud in is_assigned_stud:
                continue

            if stop in capacity_till_now:
                # If capacity of the stop is not full
                if capacity_till_now[stop] < self.capacity:
                    assigned_stops_to_stud[stud] = stop
                    capacity_till_now[stop] += 1
                    is_assigned_stud.add(stud)
                # If capacity of the stop is full
                else:
                    pass # do nothing
            else:
                assigned_stops_to_stud[stud] = stop
                capacity_till_now[stop] = 1
                is_assigned_stud.add(stud)

        # All students must be assigned a stop by now
        # If stop not assigned, adding None to it as no stop can be assigned to that student
        for stud, stop_set in student_near_stops:
            if not stud in assigned_stops_to_stud:
                assigned_stops_to_stud[stud] = None

    # this is the main function that we gotta run from outside.
    def route_local_search(self):

        ## find route algorithm
        global_stops = list(self.stops.copy().keys())[1:]# [1:] - remove base stop 0 which is unnecessary
        #why we can remove base stop ??????????????
        base_stop = global_stops[0]
        global_path_list = []

        #init students list and zero dictionary
        global_students_dict = dict()
        global_students = set(self.students.copy().keys())
        for s in range(1, len(self.students)+1):
            global_students_dict[s] = None

        #stops_debug = [61,37,36] # only first stops, in reverse order
        while len(global_students) != 0: ## empty, also some stops can be unassigned. but students must be picked up so thats why this condition
            local_stops = global_stops.copy()
            next_stop = random.choice(local_stops) # if there's fault with routing, replace this with debug stops list
            #next_stop = stops_debug.pop()
            current_stop = 0 # base stop, always 0, by definition of file format
            capacity = self.capacity
            local_path_list = list()

            #below code start with a randomly choosen stop in variable next_stop
            while True:
                if next_stop == None or len(global_students) == 0:
                	#break the while loop after assigning all students there respective stops(i.e. len(global_students)==0)
                    if local_path_list not in global_path_list:
                        global_path_list.extend([local_path_list])
                    break
                #if len(global_students)>capacity and local_stops == []:
                #    return [None,None] # not feasible solution - conflict: not enough capacity to assign students to stop

                # get our stop and generate list of students connected with only our stop or many stops
                student_single = set()#store students who can walk to only one stop
                student_many = set()#store students who can walk to many stops

                #below loop find if a student has one walkable stop or multiple
                for student in self.stop_near_students[next_stop]:
                    temp = [x for x in self.student_near_stops[student] if x in global_stops]#for current student find all stops upto where he can and stop is also in global_stops(same as potential stop removing first)
                    if student in global_students:
                        if len(temp) == 1:
                        	#student has one walkable stop
                            student_single.add(student)
                        elif len(temp) > 1:
                        	#studdent has multiple walkable stops
                            student_many.add(student)
                        else:
                        	#student has no walkable stop
                            print("No stop can be assigned for the student", student, "due to maxwalk constraint")
                            # raise Exception('Student has no stops!')
				#capacity is same as max passanger at one stop(only one bus go to one stop)
                if capacity < len(student_single):#students with the same stop
                	#if total no of students with walkable distance from this stop(i.e next_stop) and having only one walkable stop is more than capacity of stop than break the loop considering this stop and go to next stop if available(local_stop.size()>0)
                    if local_stops == []:
                        if len(global_students)>capacity and local_stops == []:
                            return [None,None] # not feasible solution - conflict: not enough capacity to assign students to stop
                        global_path_list.extend([local_path_list])#?????????
                        next_stop = None
                        break
                    local_stops.remove(next_stop)
                    for s in self.stop_near_stops[next_stop]:
                        if s[0] in local_stops:
                        	#find first neighbour stop of next_stop which is not in local_stops and assign next_stop to this
                            next_stop = s[0]
                            break
                else:
                    current_stop = next_stop
                    for s in student_single:
                        # take single and assign to stop
                        global_students_dict[s] = current_stop
                        # delete single from available list
                        global_students.remove(s)
                        capacity -= 1

                    for s in student_many:
                        if capacity > 0:
                            # take multiple  and assign to stop
                            global_students_dict[s] = current_stop
                            # delete from available list
                            global_students.remove(s)
                            capacity -= 1

                    local_stops.remove(current_stop)
                    global_stops.remove(current_stop)
                    local_path_list.extend([current_stop])

                    if capacity > 0 and local_stops != []:
                        for s in self.stop_near_stops[next_stop]:
                            if s[0] in local_stops:
                                next_stop = s[0]
                                break
                        if np.linalg.norm(current_stop-next_stop) > np.linalg.norm(next_stop-base_stop):
                            next_stop = None
                            global_path_list.extend([local_path_list])
                    else:
                        next_stop = None
                        global_path_list.extend([local_path_list])

        self.global_path_list = global_path_list
        self.global_students_dict = global_students_dict
        return [self.global_path_list, self.global_students_dict]


    def get_stops(self):
        return self.stops

    def get_students(self):
        return self.students

    def get_maxwalk(self):
        return self.maxwalk

    def get_capacity(self):
        return self.capacity

    def get_student_near_stops(self):
        return self.student_near_stops

    def get_distance(self):
        dist = 0.0
        for path in self.global_path_list:
            for i in range(len(path)+1):
                if i == 0:
                    dist += np.linalg.norm(np.array(self.stops[0])-np.array(self.stops[path[0]]))
                elif i == len(path):
                    dist += np.linalg.norm(np.array(self.stops[0])-np.array(self.stops[path[i-1]]))
                elif i < len(path):
                    dist += np.linalg.norm(np.array(self.stops[path[i]])-np.array(self.stops[path[i-1]]))
        return dist





def assign_stops(stud_data, stop_data, maxwalk, capacity, time_windows, horizon):

    router = Router(stud_data, stop_data, maxwalk, capacity)
    path_list, assignment = router.route_local_search()

    print('<><>><><>><><>><>< ')
    print(assignment)
    inf = 1000000000000000
    stop_wins = {}
    for sno, stopno in assignment.items():
        stop_wins[stopno] = []
    for sno, stopno in assignment.items():
        stop_wins[stopno].append(time_windows[sno-1])

    final_wins = {}

    for stopno, wlist in stop_wins.items():
        final_wins[stopno] = get_time_windows(wlist, horizon)

    for j in range(1, len(stop_data)):
        if(j not in final_wins):
            final_wins[j] = (0, inf)

    final_assignment = {}
    for sno, stopno in assignment.items():
        final_assignment[sno-1] = stopno


    return final_assignment , final_wins




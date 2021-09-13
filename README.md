# BOSCH-Route-Optimization-INTERIIT

  Route Optimization which is based on Genetic Algotrithm and Taabu Search in order to find the best possible paths in order to pickup employees in certain time window.
  
## PROBLEM STATEMENT
 
 - Given number of buses, passenger and bus stop locations. Develop a route optimization algorithm to determine route and schedule of buses subject to the provided constraints.
 - System should cater to the real time changing demand of employees
 - Both pickup and drop routes should be generated
 - Heterogeneous Fleet of buses are considered

## Objective

 - Minimize Operational Cost 
 - Fuel cost is the dominant factor
 - Best measured by time 

## Constraints

 - Number of Buses (hard) 
 - Bus Capacity (heterogeneous fleet, hard)  
 - Time window to reach office (hard)
 - Time Window created using employee’s time windows (both hard and soft)
 - Maximum Riding Time (hard) 
 - Minimum Occupancy (both hard and soft)
 
<img src="https://i.ibb.co/y4MDf7x/image.png" alt="image" border="0">

## Inputs
  
  - Can be done manually
  - Excel csv sheets is used to feed
  
## How to start
  
  - "python manage.py runserver"

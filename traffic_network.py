# Assumption: no overtaking; no lanes; single width; only cars; no one-ways; single speed if possible;
# intersection length uniform 2 steps; no U-turns ; rectangular grid; one-at-a-time intersection;
# camera can record everything

from pqdict import maxpq 
import random


class Vehicle(object):

	def __init__(self, number, arrival_time, origin, destination, route): 
		self.speed = 0.5 # steps per time
		self.arrival_time = arrival_time
		self.origin = origin
		self.destination = destination
		self.route = route
		self.intersection = None
		self.road_j = None
		self.road = origin[0]
		self.distance_from_i = origin[1]
		self.distance_travelled = 0.0
		self.time_taken = 0.0
		self.flowing = None
		self.display = False
		self.wait = 0.0

	def move_in_current_road(self):
		move_possibility = True
		for v in self.road.vehicles:
			d = v.distance_from_i
			if d > self.distance_from_i and d - self.distance_from_i < 2 * self.length:
				move_possibility = False
				self.wait += 1.0
				break

		if move_possibility is True:
			self.distance_travelled += self.speed * self.length
			self.distance_from_i += self.speed * self.length
			if self.distance_from_i > self.road.length:
				self.distance_from_i = self.road.length

	def move_to_another_road(self):
		self.road = self.road_j
		self.distance_travelled += self.speed * self.length
		self.distance_from_i = 0.0
		self.road.vehicles.append(self)
		self.intersection.vehicles.remove(self)
		self.intersection = None
		self.road_j = None

	def move_to_intersection(self):
		road = self.road
		intersection_i = self.road.intersection_i
		intersection_j = self.road.intersection_j
		self.distance_travelled += self.speed * self.length
		self.distance_from_i = 0.0
		self.road.vehicles.remove(self)
		self.road = None
		self.intersection = intersection_j
		self.intersection.vehicles.append(self)
		if self.intersection in self.route:
			route.remove(self.intersection)

	def is_at_intersection(self):
		if self.road is not None and self.distance_from_i >= self.road.length :
			self.intersection = self.road.intersection_j
			return True
		else:
			return False

	def is_in_intersection(self):
		return self.road is None

	def signal_allowed(self):
		signal = self.road.intersection_j.signal
		signal_time = self.road.intersection_j.signal_time

		if signal_time > self.road.intersection_j.yellow_time:
			intersection_i = self.road.intersection_j
			intersection_j = self.route[0]
			for f in intersection_i.flows:
				if self.road is f.road_i and intersection_j is f.road_j.intersection_j and intersection_i is f.road_i.intersection_j and intersection_i is f.road_j.intersection_i and f.direction in signal:
					self.road_j = f.road_j
					self.flowing = f.direction
					return True
		return False

	def intersection_empty(self):
		return len(self.intersection.vehicles) is 0

	def reached_destination(self):
		if self.road is self.destination[0] and self.distance_from_i >= self.destination[1] - self.length:
			return True
		return False

	def move(self):
		if self.is_in_intersection():
			self.move_to_another_road()
		elif self.is_at_intersection():
			if self.intersection_empty() and self.signal_allowed():
				self.move_to_intersection()
			else:
				self.wait += 1.0
		else:
			self.move_in_current_road()

		self.time_taken += 1.0

		if self.reached_destination():
			self.road.vehicles.remove(self)
class Car(Vehicle):
	colors = {
		'black'   : (  0,   0,   0),
		'white'   : (255, 255, 255),
		'red'     : (255,   0,   0),
		'green'   : (  0, 255,   0),
		'blue'    : (  0,   0, 255),
		'cyan'    : (  0, 200, 200),
		'magenta' : (200,   0, 200),
		'yellow'  : (255, 255,   0),
		'orange'  : (255, 128,   0)
	}

	def __init__(self, number, arrival_time, origin, destination, route):
		super(self.__class__, self).__init__(number, arrival_time, origin, destination, route)
		self.name = "Car " + str(number)
		self.length = 30 # 20 feet with padding
		self.width = 30 # 10 feet with padding
		self.color = [c for c in self.__class__.colors if c is not "black"][random.randint(0, len(self.__class__.colors) - 2)]

	def __str__(self):
		if self.is_in_intersection():
			return self.name + " is crossing " + self.intersection.name + " towards " + self.road_j.intersection_j.name + " in " + self.flowing + " direction."
		elif self.is_at_intersection():
			return self.name + " is at " + self.road.intersection_j.name + "trying to go towards " + self.route[0].name 
		else:
			return self.name + " is going from " + self.road.intersection_i.name + " to " + self.road.intersection_j.name + " with distance " + str(self.distance_from_i) + " in " + self.road.direction[0] + "-" + self.road.direction[1] + " direction."

class Intersection(object):
	def __init__(self, name, network, neighbours, x, y, radius):
		self.name = "Intersection " + str(name)
		self.network = network
		self.vehicles = []
		self.neighbours = neighbours
		self.flows = []
		self.signals = []
		self.signal = None
		self.signal_time = 0.0
		self.signals_left = self.signals[:]
		self.yellow_time = 0.0
		self.x = x
		self.y = y
		self.radius = radius

	def change_signal(self):
		if self.signal_time > 0.0: # Allow 3 steps for yellow between each change
			self.signal_time -= 1.0
		elif self.signal in self.signals_left:
			self.signals_left.remove(self.signal)
			if len(self.signals_left) is 0:
				self.signals_left = self.signals[:]
			signal, signal_time = self.network.signal_system.change_signal(self, self.signals_left)
			self.signal = signal
			self.signal_time = signal_time

	def get_flows(self):
		flows = []
		for f in self.network.flows:
			if f.intersection is self:
				flows.append(f)
		self.flows = flows

	def __str__(self):
		return self.name + " has signal allowing following directions " + str(self.signal) + " for " + str(self.signal_time) + " steps."


class Road(object):
	def __init__(self, name, network, intersection_i, intersection_j, length, width, x_up, y_up, direction, flows_allowed):
		self.name = "Road " + str(name)
		self.network = network
		self.intersection_i = intersection_i
		self.intersection_j = intersection_j
		self.length = length
		self.width = width
		self.vehicles = []
		self.x_up = x_up
		self.y_up = y_up
		self.direction = direction
		self.flows_allowed = flows_allowed

class Flow(object):
	def __init__(self, name, network, intersection, road_i, road_j, direction):
		self.name = name
		self.network = network
		self.intersection = intersection
		self.road_i = road_i
		self.road_j = road_j
		self.direction = direction

	def __str__(self):
		return self.road_i.intersection_i.name + "-->" + self.road_i.intersection_j.name + "-->" + self.road_j.intersection_i.name + "-->" +self.road_j.intersection_j.name + "-->" +  ":" + self.direction

class TrafficNetwork(object):
	def __init__(self, name):
		self.name = name
		self.signal_system = None
		self.intersections = []
		self.roads = []
		self.flows = []
		self.vehicles = []

	def add_signal_system(self, signal_system):
		self.signal_system =signal_system
		for i in self.intersections:
			i.signals = signal_system.get_all_signals(i.neighbours)
			i.signals_left = i.signals[:]
			i.signal, i.signal_time = signal_system.change_signal(i, i.signals_left)
			i.yellow_time = signal_system.yellow_time

	def add_intersections(self, intersections):
		self.intersections.extend(intersections)
		
	def add_roads(self, roads):
		self.roads.extend(roads)

	def add_flows(self, flows):
		self.flows.extend(flows)
		for i in self.intersections:
			i.get_flows()

	def add_vehicles(self, vehicles):
		self.vehicles.extend(vehicles)
		for v in vehicles:
			v.road.vehicles.append(v)

	def __str__(self):
		return self.name

# class Motorbike(Vehicle):
# 	def __init__(self):
# 		super(self).__init__()
# 		self.length = 8 # feet with padding
# 		self.width = 3 # feet with padding


# class Bus(Vehicle):
# 	def __init__(self):
# 		super(self).__init__()
# 		self.length = 35 # feet with padding
# 		self.width =  10 # feet with padding


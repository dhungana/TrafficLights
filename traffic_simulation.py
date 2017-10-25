
from traffic_network import *
from traffic_system import *
from traffic_visualization import *
from random import randint
from copy import deepcopy
import time
import sys

class BuildNetwork(object):

	def __init__(self):
		self.network = None

	# def build_random_network(self, intersections=10, roads=20):
	# def build_network(self, data):
	# def get_random_vehicles_at_different_times(cls):

	@classmethod 
	def build_network(cls, network, intersections_data, roads_data, vehicles_creation_data):
		random.seed(1)
		intersections = []
		for i in intersections_data:
			intersection = Intersection(i[0],i[1],i[2],i[3],i[4],i[5])
			intersections.append(intersection)
		network.add_intersections(intersections)

		roads = []
		for r in roads_data:
			road = Road(r[0],r[1],intersections[r[2]],intersections[r[3]],r[4],r[5],r[6],r[7],r[8],r[9])
			roads.append(road)
		network.add_roads(roads)
		
		flows = []
		counter = 0
		for in_bound_road in roads:
			for out_bound_road in roads:
				if in_bound_road is not out_bound_road and in_bound_road.intersection_j is out_bound_road.intersection_i and in_bound_road.intersection_i is not out_bound_road.intersection_j:
					flow_direction = in_bound_road.direction[0] + '-' + out_bound_road.direction[1]
					if flow_direction in in_bound_road.flows_allowed:
						flow = Flow(str(counter), network, in_bound_road.intersection_j, in_bound_road, out_bound_road, flow_direction)
						flows.append(flow)
		network.add_flows(flows)


		counter = 0####MIght have bug
		vehicles = []
		flows = [f for f in flows if len(f.road_j.flows_allowed) is 0]
		for t in range(vehicles_creation_data[0], vehicles_creation_data[1], vehicles_creation_data[2]):
			randomized_flow = flows[randint(0, len(flows) - 1)]
			road_i = randomized_flow.road_i
			road_j = randomized_flow.road_j
			dist1 = 0
			dist2 = road_j.length - 30 #int(random() * (road_j.length - 80)) + 40
			vehicle = Car(counter, t, (road_i, dist1), (road_j, dist2), [road_j.intersection_j])
			vehicles.append(vehicle)
			counter += 1
		network.add_vehicles(vehicles)

		return network

	@classmethod
	def build_test_network(cls):

		test_network = TrafficNetwork("Test")

		intersections_data = [(0, test_network, 4, 400, 400, 40),
						 (1, test_network, 1, 40, 400, 32),
						 (2, test_network, 1, 400, 40, 32),
						 (3, test_network, 1, 760, 400, 32),
						 (4, test_network, 1, 400, 760, 32)]
		
		roads_data = [(0, test_network, 1, 0, 320, 30, -32, -15, ("E","W"), ["E-N", "E-W", "E-S"]),
					  (1, test_network, 2, 0, 320, 30, 15, -32, ("N","S"), ["N-E", "N-W", "N-S"]),
					  (2, test_network, 3, 0, 320, 30, 32, 15, ("W","E"), ["W-E", "W-S", "W-N"]),
					  (3, test_network, 4, 0, 320, 30, -15, 32, ("S","N"), ["S-N", "S-E", "S-W"]),
					  (4, test_network, 0, 1, 320, 30, -32, 15, ("W","E"), []),
					  (5, test_network, 0, 2, 320, 30, -15, -32, ("S","N"), []),
					  (6, test_network, 0, 3, 320, 30, 32, -15, ("E","W"), []),
					  (7, test_network, 0, 4, 320, 30, 15, 32, ("N","S"), [])]


		vehicles_creation_data = (0, 800, 5)

		test_network = cls.build_network(test_network, intersections_data, roads_data, vehicles_creation_data)

		return test_network

	@classmethod
	def build_test_network_2(cls):

		test_network = TrafficNetwork("Test")

		intersections_data = [(0, test_network, 4, 400, 400, 65),
						 (1, test_network, 1, 40, 400, 50),
						 (2, test_network, 1, 400, 40, 50),
						 (3, test_network, 1, 760, 400, 50),
						 (4, test_network, 1, 400, 760, 50)]

		roads_data = [(0, test_network, 1, 0, 320, 30, -50, -30, ("E","W"), ["E-N"]),
					  (1, test_network, 2, 0, 320, 30, 30, -50, ("N","S"), ["N-S"]),
					  (2, test_network, 3, 0, 320, 30, 50, 30, ("W","E"), ["W-E"]),
					  (3, test_network, 4, 0, 320, 30, -30, 50, ("S","N"), ["S-N"]),
					  (4, test_network, 0, 1, 320, 30, -50, 30, ("W","E"), []),
					  (5, test_network, 0, 2, 320, 30, -30, -50, ("S","N"), []),
					  (6, test_network, 0, 3, 320, 30, 50, -30, ("E","W"), []),
					  (7, test_network, 0, 4, 320, 30, 30, 50, ("N","S"), []),
					  (8, test_network, 1, 0, 320, 30, -50, 0, ("E","W"), ["E-S", "E-W"]),
					  (9, test_network, 2, 0, 320, 30, 0, -50, ("N","S"), ["N-E","N-W"]),
					  (10, test_network, 3, 0, 320, 30, 50, 0, ("W","E"), ["W-N","W-S"]),
					  (11, test_network, 4, 0, 320, 30, 0, 50, ("S","N"), ["S-W", "S-E"])
					  ]


		vehicles_creation_data = (0, 850, 5) ##TODO: Vehicle_size from here

		test_network = cls.build_network(test_network, intersections_data, roads_data, vehicles_creation_data)

		return test_network

class Simulation(object):

	def update_function(self, network, current_time):
		for i in network.intersections:
			i.change_signal()
			for v in i.vehicles:
				v.move()
		for r in network.roads:
			vehicles = sorted(r.vehicles, key=lambda x:x.distance_from_i, reverse=True)
			for v in vehicles:
				if v.display and v.reached_destination() is False:
					v.move()
				elif v.arrival_time <= current_time and v.reached_destination() is False:
					can_move = True
					for vehicle in v.road.vehicles:
						if vehicle is not v and vehicle.display:
							if  (not(vehicle.distance_from_i > v.distance_from_i and vehicle.distance_from_i - v.distance_from_i > 2 * vehicle.length) and not (vehicle.distance_from_i < v.distance_from_i and v.distance_from_i - vehicle.distance_from_i > 2 * vehicle.length)):
								v.time_taken += 1.0
								v.wait += 1.0
								can_move = False
								break
					if can_move:
						v.display = True
						v.move()

	def simulate_visually(self, network, total_time,start_time=None, display=True, update_delay=1):
		visualizer = Visualizer(network, size=(5*160, 5*160), update_delay=update_delay, display=display)
		visualizer.start_display(self.update_function, total_time, start_time)

	def test_simulation(self, signal_system=(0,0,0,0), start_time=None):
		test_network = BuildNetwork.build_test_network_2()
		if signal_system[0] is 4:
			signal_system = FlowDependentFlexibleTimeVariableSignalSystem(signal_system[1], 0.9, 0.37)
		elif signal_system[0] is 3:
			signal_system = FlowDependentFixedTimeVariableSignalSystem(signal_system[1], signal_system[2], signal_system[3])
		elif signal_system[0] is 2:
			signal_system = FlowDependentFlexibleTimeFixedSignalSystem(signal_system[1], signal_system[2], signal_system[3])
		elif signal_system[0] is 1:
			signal_system = FixedSignalSystem(signal_system[1])
		else:
			signal_system = RandomSignalSystem(signal_system[1])
		test_network.add_signal_system(signal_system)
		self.simulate_visually(test_network, 1000, start_time, True, 0.2)
		self.print_result(test_network)

	def get_best_parameters(self, signal=(0, 0), start_time=None):
		best_alpha = 0.0
		best_beta = 0.0
		average_wait = float("inf")
		for a in range(0, 100, 1):
			for b in range(0, 100, 1):
				alpha = a/100.0
				beta = b/100.0
				if signal[0] is 4:
					signal_system = FlowDependentFlexibleTimeVariableSignalSystem(signal[1], alpha, beta)
				elif signal[0] is 3:
					signal_system = FlowDependentFixedTimeVariableSignalSystem(signal[1], alpha, beta)
				elif signal[0] is 2:
					signal_system = FlowDependentFlexibleTimeFixedSignalSystem(signal[1], alpha, beta)
				elif signal[0] is 1:
					signal_system = FixedSignalSystem(signal[1])
				else:
					signal_system = RandomSignalSystem(signal[1])
				test_network = BuildNetwork.build_test_network_2()
				test_network.add_signal_system(signal_system)
				self.simulate_visually(test_network, 1000, start_time, display=False, update_delay = 0)
				print "Alpha: "+ str(alpha) + "Beta: " + str(beta) 
				self.print_result(test_network)
				if test_network.average_wait < average_wait:
					average_wait = test_network.average_wait
					best_alpha = alpha
					best_beta = beta

		return best_alpha, best_beta

	def print_result(cls, network):
		number_of_cars = 0
		total_distance = 0.0
		total_time_taken = 0.0
		total_waits = 0.0
		max_wait = float("-inf")
		for v in network.vehicles:
			number_of_cars += 1
			total_distance += v.distance_travelled
			total_time_taken += v.time_taken
			total_waits += v.wait
			if v.wait > max_wait:
				max_wait = v.wait

		network.average_wait = total_waits / number_of_cars
		print "================================================="
		print "Signal System: " + str(network.signal_system.__class__)
		print "-------------------------------------------------"
		print "Total Cars: " + str(number_of_cars)
		print "Total Distance Covered: " + str(total_distance)
		print "Total Time Taken: " + str(total_time_taken)
		print "Total Waits: " + str(total_waits)
		print "Average Distance Covered: " + str(total_distance/number_of_cars)
		print "Average Time Taken: " + str(total_time_taken/number_of_cars)
		print "Average Speed: " + str(total_distance/total_time_taken)
		print "Average Waits: " + str(total_waits/number_of_cars)
		print "Max Wait: " + str(max_wait)
		print "================================================="

if __name__ == '__main__':
	###usage###
	# export time_start=$(date +%s)
	# python traffic_simulation.py 0 $time_start & python traffic_simulation.py 1 $time_start

	simulation = Simulation()
	# alpha, beta = simulation.get_best_parameters((int(sys.argv[1]), 30.0),)
	# print "Alpha = " + str(alpha)
	# print "Beta = " + str(beta)
	simulation.test_simulation((int(sys.argv[1]), 30.0,), int(sys.argv[2]) + 15)


# In simulation

	# def print_result():

	# def get_result():

# class Fixed_Simulation(object):
# 	def simulate_fixed_time():

# class Variable_Simulation(object):
# 	def simulate_variable_time():

# class CompareSimulation(object):
# 	def compare_simulation():

# 	def get_result():

# 	def print_result():

# class ImproveParameter(object):
# 	def get_result():
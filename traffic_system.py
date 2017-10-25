from random import randint

class SignalSystem(object):

	def __init__(self):
		self.yellow_time = 3.0

	def get_all_signals(self, neighbours):
		if neighbours == 4:
			return ["E-W W-E E-N W-S", "N-S S-N N-W S-E", "E-S W-N", "N-E S-W"]   # Green = Straight + Left; Red = Stop; Right = Right; Yellow = Wait
		else:
			return []

class RandomSignalSystem(SignalSystem):

	def __init__(self, fixed_time):
		super(self.__class__, self).__init__()
		self.fixed_time = fixed_time

	def change_signal(self, intersection, signals_left):
		signal_time = self.fixed_time
		signal = signals_left[randint(0,len(signals_left) - 1)] if len(signals_left) > 0 else "ALL"
		return signal, signal_time

class FixedSignalSystem(SignalSystem):

	def __init__(self, fixed_time):
		super(self.__class__, self).__init__()
		self.fixed_time = fixed_time

	def change_signal(self, intersection, signals_left):
		signal_time = self.fixed_time
		signal = signals_left[0] if len(signals_left) > 0 else "ALL"
		return signal, signal_time

class FlowDependentFlexibleTimeFixedSignalSystem(SignalSystem):

	def __init__(self, average_time, alpha, beta):
		#alpha between 0 and 1
		super(self.__class__, self).__init__()
		self.average_time = average_time
		self.alpha = alpha
		self.beta = beta

	def change_signal(self, intersection, signals_left):
		signal = signals_left[0] if len(signals_left) > 0 else "ALL"
		if signal == "ALL":
			return signal, self.average_time
		in_roads = [f.road_i for f in intersection.flows if f.direction in signal]
		in_flow_ratio = sum([len(r.vehicles) for r in in_roads])/sum([r.length/3.0 for r in in_roads])
		out_roads = [f.road_j for f in intersection.flows if f.direction in signal]
		out_flow_ratio = sum([len(r.vehicles) for r in out_roads])/sum([r.length/3.0 for r in out_roads])
		signal_time = self.average_time + self.alpha * in_flow_ratio - self.beta * out_flow_ratio
		return signal, signal_time

class FlowDependentFixedTimeVariableSignalSystem(SignalSystem):

	def __init__(self, average_time, alpha, beta):
		#alpha between 0 and 1
		super(self.__class__, self).__init__()
		self.average_time = average_time
		self.alpha = alpha
		self.beta = beta

	def change_signal(self, intersection, signals_left):
		signal = signals_left[0] if len(signals_left) > 0 else "ALL"
		if signal == "ALL":
			return signal, self.average_time
		max_signal_time = float("-inf")
		signal = None
		for s in signals_left:
			in_roads = [f.road_i for f in intersection.flows if f.direction in s]
			in_flow_ratio = sum([len([v for v in r.vehicles if v.display]) for r in in_roads])/sum([r.length/3.0 for r in in_roads])
			out_roads = [f.road_j for f in intersection.flows if f.direction in s]
			out_flow_ratio = sum([len([v for v in r.vehicles if v.display]) for r in out_roads])/sum([r.length/3.0 for r in out_roads])
			signal_time = self.average_time + self.alpha * in_flow_ratio - self.beta * out_flow_ratio
			if signal_time >= max_signal_time:
				max_signal_time = signal_time
				signal = s

		return signal, self.average_time


class FlowDependentFlexibleTimeVariableSignalSystem(SignalSystem):

	def __init__(self, average_time, alpha, beta):
		#alpha between 0 and 1
		super(self.__class__, self).__init__()
		self.average_time = average_time
		self.alpha = alpha
		self.beta = beta

	def change_signal(self, intersection, signals_left):
		signal = signals_left[0] if len(signals_left) > 0 else "ALL"
		if signal == "ALL":
			return signal, self.average_time
		max_signal_time = float("-inf")
		signal = None
		for s in signals_left:
			in_roads = [f.road_i for f in intersection.flows if f.direction in s]
			in_flow_ratio = sum([len([v for v in r.vehicles if v.display]) for r in in_roads])/sum([r.length/3.0 for r in in_roads])
			out_roads = [f.road_j for f in intersection.flows if f.direction in s]
			out_flow_ratio = sum([len([v for v in r.vehicles if v.display]) for r in out_roads])/sum([r.length/3.0 for r in out_roads])
			signal_time = self.average_time * ( 1 + self.alpha * in_flow_ratio - self.beta * out_flow_ratio) / (1 + self.alpha)
			if signal_time >= max_signal_time:
				max_signal_time = signal_time
				signal = s

		return signal, max_signal_time

#class FixedTimeSystem(SignalSystem):


#class VariableTimeSystem(SignalSystem):

#class Flow(object):

# class OutwardFlow(Flow):

# class InwardFlow(Flow):
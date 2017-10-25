# Modified from Udacity smart-car project (Machine Learning NanoDegree)

import os
import time
import random
import importlib

class Visualizer(object):

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

	def __init__(self, network, size=None, update_delay=1.0, display=True):
		self.network = network
		self.size = size if size is not None else (len(network.intersections) * int(max([r.length for r in network.roads])), len(network.intersections) * int(max([r.length for r in network.roads])))
		self.width, self.height = self.size
		
		self.bg_color = self.colors['white']
		self.road_width = 10
		self.road_color = self.colors['black']

		self.quit = False
		self.start_time = None
		self.current_time = 0.0
		self.last_updated = 0.0
		self.update_delay = update_delay  # duration between each step (in secs)

		self.display = display
		if self.display:
			try:
				self.pygame = importlib.import_module('pygame')
				self.pygame.init()
				self.screen = self.pygame.display.set_mode(self.size)

				self.frame_delay = max(1, int(self.update_delay * 1000))  # delay between GUI frames in ms (min: 1)
				self.agent_sprite_size = (30, 30)
				for vehicle in self.network.vehicles:
					vehicle._sprite = self.pygame.transform.smoothscale(self.pygame.image.load(os.path.join("images", "car-{}.png".format(vehicle.color))), self.agent_sprite_size)
					vehicle._sprite_size = (vehicle._sprite.get_width(), vehicle._sprite.get_height())

				self.font = self.pygame.font.Font(None, 28)
				self.paused = False
			except ImportError as e:
				self.display = False
				print "Simulator.__init__(): Unable to import pygame; display disabled.\n{}: {}".format(e.__class__.__name__, e)
			except Exception as e:
				self.display = False
				print "Simulator.__init__(): Error initializing GUI objects; display disabled.\n{}: {}".format(e.__class__.__name__, e)

	def start_display(self, update_function, total_time, start_time):
		self.quit = False
		self.current_time = 0.0
		self.last_updated = 0.0
		self.start_time = start_time if start_time else time.time()
		self.counter = 0.0
		while True:
			try:
				# Update current time
				self.current_time = time.time() - self.start_time
				#print "Simulator.run(): current_time = {:.3f}".format(self.current_time)

				# Handle GUI events
				if self.display:
					for event in self.pygame.event.get():
						if event.type == self.pygame.QUIT:
							self.quit = True
						elif event.type == self.pygame.KEYDOWN:
							if event.key == 27:  # Esc
								self.quit = True
							elif event.unicode == u' ':
								self.paused = True

					if self.paused:
						self.pause()

				# Update environment
				if self.current_time - self.last_updated >= self.update_delay:
					update_function(self.network, self.counter)
					self.last_updated = self.current_time
					self.counter += 1.0

				# Render GUI and sleep
				if self.display:
					self.render()
					self.pygame.time.wait(self.frame_delay)

			except KeyboardInterrupt:
				self.quit = True
			finally:
				if self.quit:
					break

			if self.quit or self.counter > total_time:
				break

	def render(self):
		self.screen.fill(self.bg_color)

		for road in self.network.roads:
			self.pygame.draw.line(self.screen, self.road_color, (road.intersection_i.x + road.x_up, road.intersection_i.y + road.y_up), (road.intersection_j.x + road.x_up, road.intersection_j.y + road.y_up), road.width)
			self.pygame.draw.line(self.screen, self.colors["white"], (road.intersection_i.x + road.x_up + road.width/2, road.intersection_i.y + road.y_up+ road.width/2), (road.intersection_j.x + road.x_up+ road.width/2, road.intersection_j.y + road.y_up+ road.width/2), 1)
			self.pygame.draw.line(self.screen, self.colors["white"], (road.intersection_i.x + road.x_up - road.width/2, road.intersection_i.y + road.y_up- road.width/2), (road.intersection_j.x + road.x_up- road.width/2, road.intersection_j.y + road.y_up- road.width/2), 1)

		for intersection in self.network.intersections:
			self.pygame.draw.circle(self.screen, self.colors["white"], (intersection.x, intersection.y), intersection.radius, 1)
			self.pygame.draw.circle(self.screen, self.road_color, (intersection.x, intersection.y), intersection.radius)
			####TODO: LIGHT PART
			# if intersection.state:  # North-South is open
			#     self.pygame.draw.line(self.screen, self.colors['green'],
			#         (intersection[0] * self.env.block_size, intersection[1] * self.env.block_size - 15),
			#         (intersection[0] * self.env.block_size, intersection[1] * self.env.block_size + 15), self.road_width)
			# else:  # East-West is open
			#     self.pygame.draw.line(self.screen, self.colors['green'],
			#         (intersection[0] * self.env.block_size - 15, intersection[1] * self.env.block_size),
			#         (intersection[0] * self.env.block_size + 15, intersection[1] * self.env.block_size), self.road_width)

		for vehicle in self.network.vehicles:

			if vehicle.display and vehicle.reached_destination() is False:
				rotated_sprite = vehicle._sprite
				if vehicle.is_in_intersection():
					
					vehicle_pos = (vehicle.intersection.x, vehicle.intersection.y)
					vehicle_rotation = 0
					vehicle_rotation = 45 if vehicle.flowing == "E-N"  else vehicle_rotation
					vehicle_rotation = 360 - 45 if vehicle.flowing == "E-S"  else vehicle_rotation
					vehicle_rotation = 180 if vehicle.flowing == "W-E"  else vehicle_rotation
					vehicle_rotation = 135 if vehicle.flowing == "W-N"  else vehicle_rotation
					vehicle_rotation = 360-135 if vehicle.flowing == "W-S"  else vehicle_rotation
					vehicle_rotation = 270 if vehicle.flowing == "N-S" else vehicle_rotation
					vehicle_rotation = 360-135 if vehicle.flowing == "N-E" else vehicle_rotation
					vehicle_rotation = 360-45 if vehicle.flowing == "N-W" else vehicle_rotation
					vehicle_rotation = 90 if vehicle.flowing == "S-N" else vehicle_rotation
					vehicle_rotation = 135 if vehicle.flowing == "S-E" else vehicle_rotation
					vehicle_rotation = 45 if vehicle.flowing == "S-W" else vehicle_rotation

					vehicle_offset = (0, -1 * vehicle.road_j.width/2) if vehicle.flowing == "E-W" else (0,0)
					vehicle_offset = (-1 * vehicle.road_j.width/4, -1 * vehicle.road_j.width/4) if vehicle.flowing == "E-N"  else vehicle_offset
					vehicle_offset = (-1 * vehicle.road_j.width/4, vehicle.road_j.width/4) if vehicle.flowing == "E-S"  else vehicle_offset
					vehicle_offset = (0, vehicle.road_j.width/2) if vehicle.flowing == "W-E"  else vehicle_offset
					vehicle_offset = (vehicle.road_j.width/4, -1 * vehicle.road_j.width/4) if vehicle.flowing == "W-N"  else vehicle_offset
					vehicle_offset = (vehicle.road_j.width/4, vehicle.road_j.width/4) if vehicle.flowing == "W-S"  else vehicle_offset
					vehicle_offset = (vehicle.road_j.width/2, 0) if vehicle.flowing == "N-S" else vehicle_offset
					vehicle_offset = (-1 * vehicle.road_j.width/4, -1 * vehicle.road_j.width/4) if vehicle.flowing == "N-E" else vehicle_offset
					vehicle_offset = (vehicle.road_j.width/4,  -1 * vehicle.road_j.width/4) if vehicle.flowing == "N-W" else vehicle_offset
					vehicle_offset = (-1 * vehicle.road_j.width/2, 0) if vehicle.flowing == "S-N" else vehicle_offset
					vehicle_offset = (-1 * vehicle.road_j.width/4, vehicle.road_j.width/4) if vehicle.flowing == "S-E" else vehicle_offset
					vehicle_offset = (vehicle.road_j.width/4,  vehicle.road_j.width/4) if vehicle.flowing == "S-W" else vehicle_offset
					
					vehicle_pos = vehicle_pos[0] + vehicle_offset[0], vehicle_pos[1] + vehicle_offset[1]
				else:
					intersection_i = vehicle.road.intersection_i ###TODO Handle in intersection
					intersection_j = vehicle.road.intersection_j

					if intersection_j.x > intersection_i.x:
						vehicle_pos = (intersection_i.x + vehicle.road.x_up + vehicle.distance_from_i, intersection_i.y + vehicle.road.y_up )
					elif intersection_j.x < intersection_i.x:
						vehicle_pos = (intersection_i.x + vehicle.road.x_up - vehicle.distance_from_i, intersection_i.y + vehicle.road.y_up )
					elif intersection_j.y > intersection_i.y:
						vehicle_pos = (intersection_i.x + vehicle.road.x_up , intersection_i.y  + vehicle.road.y_up + vehicle.distance_from_i)
					else:
						vehicle_pos = (intersection_i.x + vehicle.road.x_up , intersection_i.y + vehicle.road.y_up - vehicle.distance_from_i)

					vehicle_rotation = 0
					vehicle_rotation = 180 if vehicle.road.direction == ("W","E")  else vehicle_rotation
					vehicle_rotation = 270 if vehicle.road.direction == ("N","S") else vehicle_rotation
					vehicle_rotation = 90 if vehicle.road.direction == ("S","N") else vehicle_rotation
				


				rotated_sprite = self.pygame.transform.rotate(vehicle._sprite, vehicle_rotation)

				self.screen.blit(rotated_sprite,
					self.pygame.rect.Rect(vehicle_pos[0] - vehicle._sprite_size[0] / 2, vehicle_pos[1] - vehicle._sprite_size[1] / 2,
						vehicle._sprite_size[0], vehicle._sprite_size[1]))
			
		self.screen.blit(self.font.render(str(self.network.signal_system.__class__), True, self.colors['red'], self.bg_color), (100, 10))

		# Flip buffers
		self.pygame.display.flip()

	def pause(self):
		abs_pause_time = time.time()
		pause_text = "[PAUSED] Press any key to continue..."
		self.screen.blit(self.font.render(pause_text, True, self.colors['cyan'], self.bg_color), (100, self.height - 40))
		self.pygame.display.flip()
		print pause_text  # [debug]
		while self.paused:
			for event in self.pygame.event.get():
				if event.type == self.pygame.KEYDOWN:
					self.paused = False
			self.pygame.time.wait(self.frame_delay)
		self.screen.blit(self.font.render(pause_text, True, self.bg_color, self.bg_color), (100, self.height - 40))
		self.start_time += (time.time() - abs_pause_time)






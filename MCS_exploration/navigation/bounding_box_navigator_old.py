from navigation.visibility_road_map import VisibilityRoadMap,ObstaclePolygon,IncrementalVisibilityRoadMap
import random
import math
import matplotlib.pyplot as plt
import constants
#from cover_floor import update_seen,get_visible_points,get_visible_points
from navigation.fov import FieldOfView
from utils import game_util
import cover_floor

SHOW_ANIMATION = True
random.seed(1)

class BoundingBoxNavigator:

	# pose is a triplet x,y,theta (heading)
	def __init__(self, robot_radius=5, maxStep=0.25):
		self.agentX = None
		self.agentY = None
		self.agentH = None
		self.epsilon = None

		self.scene_obstacles_dict = {}
		self.scene_plot = None

		self.radius = robot_radius
		self.maxStep = maxStep

	
	def get_one_step_move(self, goal, roadmap):

		pathX, pathY = roadmap.planning(self.agentX, self.agentY, goal[0], goal[1])
		#pathX, pathY = roadmap.planning(self.agentX, self.agentY, goal[0], goal[1], self.scene_obstacles_dict)

		#print(i)
		# execute a small step along that plan by
		# turning to face the first waypoint
		#print ("From one step move, current_position and goal ", self.agentX, self.agentY, goal)
		#print ("From one step move, path found by path finder ",pathX,pathY)
		if len(pathX) == 1 and len(pathY) == 1:
			i = 0
		else:
			i = 1
		dX = pathX[i]-self.agentX
		dY = pathY[i]-self.agentY
		angleFromAxis = math.atan2(dX, dY)
			
		#taking at most a step of size 0.1
		distToFirstWaypoint = math.sqrt((self.agentX-pathX[i])**2 + (self.agentY-pathY[i])**2)
		stepSize = min(self.maxStep, distToFirstWaypoint)

		#print ("From one step move ",self.agentX,self.agentY, goal, stepSize, angleFromAxis)

		return stepSize, angleFromAxis

	def clear_obstacle_dict(self):
		self.scene_obstacles_dict = {}

	def reset(self):
		self.clear_obstacle_dict()
		self.agentX = None
		self.agentY = None
		self.agentH = None

	def add_obstacle_from_step_output(self, step_output):
		for obj in step_output.object_list:
			if obj.uuid not in self.scene_obstacles_dict and len(obj.dimensions) > 0:
				x_list = []
				y_list = []
				for i in range(4, 8):
					x_list.append(obj.dimensions[i]['x'])
					y_list.append(obj.dimensions[i]['z'])
				self.scene_obstacles_dict[obj.uuid] = ObstaclePolygon(x_list, y_list)
			if obj.held:
				del self.scene_obstacles_dict[obj.uuid]

		for obj in step_output.structural_object_list:
			if obj.uuid not in self.scene_obstacles_dict and len(obj.dimensions) > 0:
				if obj.uuid == "ceiling" or obj.uuid == "floor":
					continue
				x_list = []
				y_list = []
				for i in range(4, 8):
					x_list.append(obj.dimensions[i]['x'])
					y_list.append(obj.dimensions[i]['z'])
				self.scene_obstacles_dict[obj.uuid] = ObstaclePolygon(x_list, y_list)

	def go_to_goal(self,goal_pose,agent,success_distance):
		#print ("current pose in go to goal", current_pose[1])
		#goal_pose[0],goal_pose[1] = goal_pose[0]*constants.AGENT_STEP_SIZE,goal_pose[1]*constants.AGENT_STEP_SIZE
		#goal_pose[0],goal_pose[1] = goal_pose[0]*5,goal_pose[1]*5
		gx, gy = goal_pose[0], goal_pose[1]
		sx, sy = agent.game_state.event.position['x'] ,agent.game_state.event.position['z']
		self.agentX, self.agentY = sx,sy
		self.agentH = agent.game_state.event.rotation / 360 * (2 * math.pi)
		self.epsilon = success_distance
		actions = 0 
		#print ("beginning of go to goal", gx,gy , self.agentX, self.agentY,sx,sy)

		while True:
			dis_to_goal = math.sqrt((self.agentX-gx)**2 + (self.agentY-gy)**2)
			if dis_to_goal < self.epsilon:
				break
			roadmap = IncrementalVisibilityRoadMap(self.radius, do_plot=False)
			#roadmap = VisibilityRoadMap(self.radius, do_plot=False)
			for obstacle_key, obstacle in self.scene_obstacles_dict.items():
				roadmap.addObstacle(obstacle)
				#if not obstacle.contains_goal((gx, gy)):
				#	roadmap.addObstacle(obstacle)
				#if not obstacle.contains_goal((gx, gy)):
				#	roadmap.addObstacle(obstacle)

			#fov = FieldOfView([sx, sy, 0], 42.5 / 180.0 * math.pi, self.scene_obstacles_dict.values())
			fov = FieldOfView([sx,sy, 0], 42.5 / 180.0 * math.pi, self.scene_obstacles_dict.values())
			fov.agentX = self.agentX
			fov.agentY = self.agentY
			fov.agentH = self.agentH
			poly = fov.getFoVPolygon(100)

			SHOW_ANIMATION = False

			if SHOW_ANIMATION:
				plt.cla()
				plt.xlim((-7, 7))
				plt.ylim((-7, 7))
				plt.gca().set_xlim((-7, 7))
				plt.gca().set_ylim((-7, 7))

				plt.plot(self.agentX, self.agentY, "or")
				plt.plot(gx, gy, "ob")
				poly.plot("-r")

				for obstacle in self.scene_obstacles_dict.values():
					obstacle.plot("-g")

				plt.axis("equal")
				plt.pause(0.001)


			stepSize, heading = self.get_one_step_move([gx, gy], roadmap)

			# needs to be replaced with turning the agent to the appropriate heading in the simulator, then stepping.
			# the resulting agent position / heading should be used to set plan.agent* values.

			rotation_degree = heading / (2 * math.pi) * 360 - agent.game_state.event.rotation
			#print("heading , rotation , stepsize",heading,  rotation_degree,stepSize)


			#print("all objects found until now and stored" ,self.scene_obstacles_dict )
			#nav_env.env.step(action="RotateLook", rotation=rotation_degree)
			action={'action':"RotateLook",'rotation':rotation_degree}
			agent.step(action)#={'action':"RotateLook",rotation=rotation_degree}
			#self.add_obstacle_from_step_output(agent.game_state.event)
			if agent.game_state.event.return_status == "SUCCESSFUL":
				actions += 1
				#rotation = agent.game_state.event.rotation / 360 * (2 * math.pi)
				rotation = agent.game_state.event.rotation
				pose = game_util.get_pose(agent.game_state.event)[:3]  
				cover_floor.update_seen(self.agentX,self.agentY, agent.game_state,rotation ,42.5,self.scene_obstacles_dict.values() )
				#print("Visible points",get_visible_points(self.agentX,self.agentY ,rotation ,42.5,self.scene_obstacles_dict.values()))
			else:
				continue


			agentX_exp = self.agentX + stepSize * math.sin(self.agentH)
			agentY_exp = self.agentY + stepSize * math.cos(self.agentH)
			# if abs(agentX_exp - nav_env.step_output.position['x']) > 1e-2:
			# 	print("Collision happened, re-update agent's position")
			# elif abs(agentY_exp - nav_env.step_output.position['z']) > 1e-2:
			# 	print("Collision happened, re-update agent's position")

			self.agentX = agent.game_state.event.position['x']
			self.agentY = agent.game_state.event.position['z']
			self.agentH = agent.game_state.event.rotation / 360 * (2 * math.pi)
			#nav_env.env.step(action="MoveAhead", amount=0.5)

			#if abs(rotation_degree) > 0.01:
			#	if 360 - abs(rotation_degree) > 0.01:
			#		print ("in the continue", abs(rotation_degree), 360 - abs(rotation_degree))
			#		continue
			action={'action':"MoveAhead", 'amount':0.5}
			agent.step(action)#={'action':"RotateLook",rotation=rotation_degree}
			self.agentX = agent.game_state.event.position['x']
			self.agentY = agent.game_state.event.position['z']
			self.agentH = agent.game_state.event.rotation / 360 * (2 * math.pi)
			if agent.game_state.event.return_status == "SUCCESSFUL":
				actions += 1 
				pose = game_util.get_pose(agent.game_state.event)[:3]
				rotation = agent.game_state.event.rotation
				#graph_obj.update_seen(self.agentX,self.agentY,rotation ,100,42.5,self.scene_obstacles_dict )
				cover_floor.update_seen(self.agentX,self.agentY, agent.game_state,rotation ,42.5,self.scene_obstacles_dict.values() )
				#update_seen(visibility_graph,pose[0],pose[1],pose[2] ,agent.game_state.event)
			else:
				continue

			if agent.game_state.goals_found == True:
				return

			#self.add_obstacle_from_step_output(agent.game_state.event)
			#nav_env.env.step(action="MoveAhead", amount=0.5)

			# # any new obstacles that were observed during the step should be added to the planner
			# for i in range(len(obstacles)):
			# 	if not visible[i] and obstacles[i].minDistanceToVertex(self.agentX, self.agentY) < 30:
			# 		self.addObstacle(obstacles[i])
			# 		visible[i] = True

		return actions


from tasks.bonding_box_navigation_mcs.visibility_road_map import IncrementalVisibilityRoadMap, ObstaclePolygon
import random
import math
import matplotlib.pyplot as plt
from tasks.bonding_box_navigation_mcs.fov import FieldOfView
from shapely.geometry import Point, Polygon
import shapely.geometry as sp
from descartes import PolygonPatch

import pickle

SHOW_ANIMATION = True
random.seed(1)

class BoundingBoxNavigator:

	# pose is a triplet x,y,theta (heading)
	def __init__(self, robot_radius=0.1, maxStep=0.25):
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

		#print(i)
		# execute a small step along that plan by
		# turning to face the first waypoint
		if len(pathX) == 1 and len(pathY) == 1:
			i = 0
		else:
			i = 1
		dX = pathX[i]-self.agentX
		dY = pathY[i]-self.agentY
		angleFromAxis = math.atan2(dX, dY)
			
		#taking at most a step of size 0.25
		distToFirstWaypoint = math.sqrt((self.agentX-pathX[i])**2 + (self.agentY-pathY[i])**2)
		stepSize = min(self.maxStep, distToFirstWaypoint)

		return stepSize, angleFromAxis

	def clear_obstacle_dict(self):
		self.scene_obstacles_dict = {}

	def add_obstacle_from_step_output(self, step_output):
		for obj in step_output.object_list:
			if len(obj.dimensions) > 0:
				point_list = []
				for i in range(4, 8):
					point_list.append((obj.dimensions[i]['x'], obj.dimensions[i]['z']))
				self.scene_obstacles_dict[obj.uuid] = ObstaclePolygon(point_list)
			if obj.held:
				del self.scene_obstacles_dict[obj.uuid]

		for obj in step_output.structural_object_list:
			if len(obj.dimensions) > 0:
				if obj.uuid == "ceiling" or obj.uuid == "floor":
					continue
				point_list = []
				for i in range(4, 8):
					point_list.append((obj.dimensions[i]['x'], obj.dimensions[i]['z']))
				self.scene_obstacles_dict[obj.uuid] = ObstaclePolygon(point_list)

	def go_to_goal(self, nav_env, goal, success_distance):
		self.agentX = nav_env.step_output.position['x']
		self.agentY = nav_env.step_output.position['z']
		self.agentH = nav_env.step_output.rotation / 360 * (2 * math.pi)
		self.epsilon = success_distance

		gx, gy = goal[0], goal[2]
		sx, sy = self.agentX, self.agentY

		NAVIGATION_LIMIT_STEP = 100
		SUCCESS_FLAG = False
		for _ in range(NAVIGATION_LIMIT_STEP):
			goal_obj_bonding_box = None
			for id, polygon in self.scene_obstacles_dict.items():
				if Point((gx, gy)).within(polygon):
					goal_obj_bonding_box = polygon
					break
			if not goal_obj_bonding_box:
				dis_to_goal = math.sqrt((self.agentX-gx)**2 + (self.agentY-gy)**2)
				print("Distance to Goal {}".format(dis_to_goal))
			else:
				dis_to_goal = goal_obj_bonding_box.distance(Point(self.agentX, self.agentY))
				print("Distance to Bonding Box {}".format(dis_to_goal))
			if dis_to_goal < self.epsilon:
				SUCCESS_FLAG = True
				break

			roadmap = IncrementalVisibilityRoadMap(self.radius, do_plot=False)
			# parameters = {}
			# all_obstacles = []
			for obstacle_key, obstacle in self.scene_obstacles_dict.items():
				if not Point((gx, gy)).within(polygon):
					roadmap.addObstacle(obstacle)
					# all_obstacles.append(obstacle)
			# print(len(all_obstacles))
			# parameters['obstacles'] = all_obstacles
			# parameters['sx'] = sx
			# parameters['sy'] = sy
			# parameters['gx'] = gx
			# parameters['gy'] = gy
			# parameters['robot_radius'] = 0.1
			# parameters['max_stepsize'] = 0.25
			# with open("parameters.pkl", 'wb') as f:
			# 	pickle.dump(parameters, f)
			# exit(0)

			fov = FieldOfView([self.agentX, self.agentY, self.agentH], 42.5 / 180.0 * math.pi, self.scene_obstacles_dict.values())
			poly = fov.getFoVPolygon(100)
			world = sp.MultiPolygon().union(poly)

			if SHOW_ANIMATION:
				plt.cla()
				plt.xlim((-7, 7))
				plt.ylim((-7, 7))
				plt.gca().set_xlim((-7, 7))
				plt.gca().set_ylim((-7, 7))

				# plt.plot(self.agentX, self.agentY, "or")
				circle = plt.Circle((self.agentX, self.agentY), radius=self.radius, color='b')
				plt.gca().add_artist(circle)
				plt.plot(gx, gy, "x")
				poly.plot("red")

				if world.geom_type == 'MultiPolygon':
					for i in range(len(world)):
						patch1 = PolygonPatch(world[i], fc="blue", ec="blue", alpha=0.2, zorder=1)
						plt.gca().add_patch(patch1)
				else:
					patch1 = PolygonPatch(world, fc="blue", ec="blue", alpha=0.2, zorder=1)
					plt.gca().add_patch(patch1)

				for poly in self.scene_obstacles_dict.values():
					poly.plot("green")

				plt.axis("equal")
				plt.pause(0.1)


			stepSize, heading = self.get_one_step_move([gx, gy], roadmap)

			# needs to be replaced with turning the agent to the appropriate heading in the simulator, then stepping.
			# the resulting agent position / heading should be used to set plan.agent* values.

			rotation_degree = heading / (2 * math.pi) * 360 - nav_env.step_output.rotation
			nav_env.env.step(action="RotateLook", rotation=rotation_degree)
			self.agentX = nav_env.step_output.position['x']
			self.agentY = nav_env.step_output.position['z']
			self.agentH = nav_env.step_output.rotation / 360 * (2 * math.pi)

			if abs(rotation_degree) > 1e-2:
				if 360 - abs(rotation_degree) > 1e-2:
					continue

			nav_env.env.step(action="MoveAhead", amount=0.5)
			self.agentX = nav_env.step_output.position['x']
			self.agentY = nav_env.step_output.position['z']
			self.agentH = nav_env.step_output.rotation / 360 * (2 * math.pi)

		if not SUCCESS_FLAG:
			print("Navigation Fail")
		return SUCCESS_FLAG



def genRandomRectangle():
    width = random.randrange(5,50)
    height = random.randrange(5,50)
    botLeftX = random.randrange(1,100)
    botRightX = random.randrange(1,100)
    theta = random.random()*2*math.pi

    x = [random.randrange(1,50)]
    y = [random.randrange(1,50)]

    x.append(x[-1]+width)
    y.append(y[-1])

    x.append(x[-1])
    y.append(y[-1]+height)

    x.append(x[-1]-width)
    y.append(y[-1])

    for i in range(4):
        tx = x[i]*math.cos(theta) - y[i]*math.sin(theta)
        ty = x[i]*math.sin(theta) + y[i]*math.cos(theta)
        x[i] = tx
        y[i] = ty

    return ObstaclePolygon(x,y)

def main():
	print(__file__ + " start!!")


	for i in range(20):
		# start and goal position
		sx, sy = random.randrange(-100,-80), random.randrange(-100,-80)  # [m]
		gx, gy = random.randrange(80,100), random.randrange(80,100)  # [m]

		robot_radius = 5.0  # [m]

		cnt = 15
		obstacles=[]
		for i in range(cnt):
			obstacles.append(genRandomRectangle())
		visible = [False]*cnt

		if SHOW_ANIMATION:  # pragma: no cover
			plt.xlim((-100, 100))
			plt.ylim((-100, 100))
			plt.plot(sx, sy, "or")
			plt.plot(gx, gy, "ob")
			for ob in obstacles:
				ob.plot()
			plt.axis("equal")
			
			#plt.pause(0.1)

		#create a planner and initalize it with the agent's pose
		plan = BoundingBoxNavigator( [sx,sy,0], [])


		fov = FieldOfView( [sx,sy,0], 60/180.0*math.pi, obstacles)
			
		for stepSize, heading in plan.closedLoopPlannerFast([gx,gy]):
			
			#needs to be replaced with turning the agent to the appropriate heading in the simulator, then stepping.
			#the resulting agent position / heading should be used to set plan.agent* values.
			plan.agentH = heading
			plan.agentX = plan.agentX + stepSize*math.sin(plan.agentH)
			plan.agentY = plan.agentY + stepSize*math.cos(plan.agentH)

			#any new obstacles that were observed during the step should be added to the planner
			for i in range(len(obstacles)):
				if not visible[i] and obstacles[i].minDistanceToVertex(plan.agentX, plan.agentY) < 30:
					plan.addObstacle(obstacles[i])
					visible[i] = True

			fov.agentX = plan.agentX
			fov.agentY = plan.agentY
			fov.agentH = plan.agentH
			poly = fov.getFoVPolygon(100)
			

			if SHOW_ANIMATION:
				plt.cla()
				plt.xlim((-100, 100))
				plt.ylim((-100, 100))
				plt.gca().set_xlim((-100, 100))
				plt.gca().set_ylim((-100, 100))

				plt.plot(plan.agentX, plan.agentY, "or")
				plt.plot(gx, gy, "ob")
				poly.plot("-r")
			
				for i in range(len(obstacles)):
					if visible[i]:
						obstacles[i].plot("-g")
					else:
						obstacles[i].plot("-k")
				
				plt.axis("equal")
				plt.pause(0.1)

    
    #if SHOW_ANIMATION:  # pragma: no cover
    #    plt.plot(rx, ry, "-r")
    #    plt.pause(0.1)
    #    plt.show()


if __name__ == '__main__':
    main()

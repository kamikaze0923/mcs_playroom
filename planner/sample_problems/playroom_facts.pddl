(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		ball_a - object
		ball_b - object
		ball_c - object
		ball_d - object
		box_a - object
		box_b - object
		apple_a - object
		apple_b - object
		bowl_a - object
		bowl_b - object
		cup_a - object
		cup_b - object
		plate_a - object
		plate_b - object
		loc_bar_3_dot_00_bar_0_dot_46_bar_3_dot_00
		loc_bar_0_dot_00_bar_0_dot_03_bar__minus_3_dot_00 - location
		loc_bar__minus_3_dot_00_bar_0_dot_05_bar_2_dot_00 - location
		loc_bar__minus_1_dot_00_bar_0_dot_10_bar_1_dot_00 - location
		loc_bar_1_dot_00_bar_0_dot_25_bar__minus_1_dot_00 - location
		loc_bar_1_dot_00_bar_0_dot_10_bar__minus_3_dot_00 - location
		loc_bar_4_dot_00_bar_0_dot_15_bar_0_dot_00 - location
		loc_bar_2_dot_00_bar_0_dot_03_bar_1_dot_00 - location
		loc_bar_1_dot_00_bar_0_dot_03_bar__minus_4_dot_00 - location
		loc_bar__minus_1_dot_00_bar_0_dot_01_bar__minus_2_dot_00 - location
		loc_bar__minus_4_dot_00_bar_0_dot_01_bar__minus_3_dot_00 - location
		loc_bar__minus_3_dot_00_bar_0_dot_01_bar__minus_3_dot_00 - location
		loc_bar__minus_4_dot_00_bar_0_dot_01_bar__minus_2_dot_00 - location
		loc_bar_4_dot_00_bar_0_dot_01_bar__minus_4_dot_00 - location
		loc_bar_2_dot_00_bar_0_dot_01_bar__minus_4_dot_00 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(agentAtLocation agent1 loc_bar_3_dot_00_bar_0_dot_46_bar_3_dot_00)
		(objectAtLocation ball_a loc_bar_0_dot_00_bar_0_dot_03_bar__minus_3_dot_00)
		(objectAtLocation ball_b loc_bar__minus_3_dot_00_bar_0_dot_05_bar_2_dot_00)
		(objectAtLocation ball_c loc_bar__minus_1_dot_00_bar_0_dot_10_bar_1_dot_00)
		(objectAtLocation ball_d loc_bar_1_dot_00_bar_0_dot_25_bar__minus_1_dot_00)
		(objectAtLocation box_a loc_bar_1_dot_00_bar_0_dot_10_bar__minus_3_dot_00)
		(objectAtLocation box_b loc_bar_4_dot_00_bar_0_dot_15_bar_0_dot_00)
		(objectAtLocation apple_a loc_bar_2_dot_00_bar_0_dot_03_bar_1_dot_00)
		(objectAtLocation apple_b loc_bar_1_dot_00_bar_0_dot_03_bar__minus_4_dot_00)
		(objectAtLocation bowl_a loc_bar__minus_1_dot_00_bar_0_dot_01_bar__minus_2_dot_00)
		(objectAtLocation bowl_b loc_bar__minus_4_dot_00_bar_0_dot_01_bar__minus_3_dot_00)
		(objectAtLocation cup_a loc_bar__minus_3_dot_00_bar_0_dot_01_bar__minus_3_dot_00)
		(objectAtLocation cup_b loc_bar__minus_4_dot_00_bar_0_dot_01_bar__minus_2_dot_00)
		(objectAtLocation plate_a loc_bar_4_dot_00_bar_0_dot_01_bar__minus_4_dot_00)
		(objectAtLocation plate_b loc_bar_2_dot_00_bar_0_dot_01_bar__minus_4_dot_00)
	)
	(:goal
		(held agent1 ball_a)
	)
)
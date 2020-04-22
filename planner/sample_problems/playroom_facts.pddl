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
		loc_bar__minus_1_dot_00_bar_0_dot_01_bar_0_dot_00 - location
		loc_bar__minus_4_dot_00_bar_0_dot_03_bar__minus_2_dot_00 - location
		loc_bar__minus_1_dot_00_bar_0_dot_05_bar_2_dot_00 - location
		loc_bar__minus_3_dot_00_bar_0_dot_10_bar_3_dot_00 - location
		loc_bar_0_dot_00_bar_0_dot_25_bar__minus_2_dot_00 - location
		loc_bar_1_dot_00_bar_0_dot_10_bar__minus_1_dot_00 - location
		loc_bar_3_dot_00_bar_0_dot_15_bar__minus_3_dot_00 - location
		loc_bar_3_dot_00_bar_0_dot_03_bar_3_dot_00 - location
		loc_bar__minus_2_dot_00_bar_0_dot_03_bar__minus_3_dot_00 - location
		loc_bar__minus_4_dot_00_bar_0_dot_01_bar__minus_3_dot_00 - location
		loc_bar__minus_1_dot_00_bar_0_dot_01_bar_0_dot_00 - location
		loc_bar_1_dot_00_bar_0_dot_01_bar__minus_2_dot_00 - location
		loc_bar_1_dot_00_bar_0_dot_01_bar_3_dot_00 - location
		loc_bar_3_dot_00_bar_0_dot_01_bar_0_dot_00 - location
		loc_bar__minus_3_dot_00_bar_0_dot_01_bar_4_dot_00 - location
		ballType - objType
		boxType - objType
		cupType - objType
		appleType - objType
		plateType - objType
		bowlType - objType
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(lookingAtObject agent1 bowl_b)
		(inReceptacle ball_d plate_b)
		(inReceptacle ball_c plate_a)
		(inReceptacle ball_b bowl_b)
		(canNotPutin ball_c bowl_a)
		(canNotPutin ball_b bowl_a)
		(canNotPutin ball_c bowl_b)
		(canNotPutin ball_c plate_b)
		(canNotPutin ball_d bowl_a)
		(canNotPutin ball_d bowl_b)
		(agentAtLocation agent1 loc_bar__minus_1_dot_00_bar_0_dot_01_bar_0_dot_00)
		(objectAtLocation ball_a loc_bar__minus_4_dot_00_bar_0_dot_03_bar__minus_2_dot_00)
		(isType ball_a ballType)
		(objectAtLocation ball_b loc_bar__minus_1_dot_00_bar_0_dot_05_bar_2_dot_00)
		(isType ball_b ballType)
		(objectAtLocation ball_c loc_bar__minus_3_dot_00_bar_0_dot_10_bar_3_dot_00)
		(isType ball_c ballType)
		(objectAtLocation ball_d loc_bar_0_dot_00_bar_0_dot_25_bar__minus_2_dot_00)
		(isType ball_d ballType)
		(objectAtLocation box_a loc_bar_1_dot_00_bar_0_dot_10_bar__minus_1_dot_00)
		(isType box_a boxType)
		(isReceptacle box_a)
		(objectAtLocation box_b loc_bar_3_dot_00_bar_0_dot_15_bar__minus_3_dot_00)
		(isType box_b boxType)
		(isReceptacle box_b)
		(objectAtLocation apple_a loc_bar_3_dot_00_bar_0_dot_03_bar_3_dot_00)
		(isType apple_a appleType)
		(objectAtLocation apple_b loc_bar__minus_2_dot_00_bar_0_dot_03_bar__minus_3_dot_00)
		(isType apple_b appleType)
		(objectAtLocation bowl_a loc_bar__minus_4_dot_00_bar_0_dot_01_bar__minus_3_dot_00)
		(isType bowl_a bowlType)
		(isReceptacle bowl_a)
		(objectAtLocation bowl_b loc_bar__minus_1_dot_00_bar_0_dot_01_bar_0_dot_00)
		(isType bowl_b bowlType)
		(isReceptacle bowl_b)
		(objectAtLocation cup_a loc_bar_1_dot_00_bar_0_dot_01_bar__minus_2_dot_00)
		(isType cup_a cupType)
		(isReceptacle cup_a)
		(objectAtLocation cup_b loc_bar_1_dot_00_bar_0_dot_01_bar_3_dot_00)
		(isType cup_b cupType)
		(isReceptacle cup_b)
		(objectAtLocation plate_a loc_bar_3_dot_00_bar_0_dot_01_bar_0_dot_00)
		(isType plate_a plateType)
		(isReceptacle plate_a)
		(objectAtLocation plate_b loc_bar__minus_3_dot_00_bar_0_dot_01_bar_4_dot_00)
		(isType plate_b plateType)
		(isReceptacle plate_b)
	)
	(:goal
		(exists (?o1 - object ?o2 - object)
		    (and
			    (isType ?o1 ballType)
			    (isType ?o2 bowlType)
			    (inReceptacle ?o1 ?o2)
		    )
		)
	)
)
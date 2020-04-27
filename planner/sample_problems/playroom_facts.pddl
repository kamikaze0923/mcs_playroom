(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_97c5a2a9_1ce3_4b9b_9b97_18583972e984 - object
		legal_wall_06b598b5_91c6_409b_aadd_04e0645c722a - object
		legal_wall_4c48a876_7ce0_4e8e_ad49_040d2e529abd - object
		loc_bar__minus_2_dot_14_bar_0_dot_46_bar__minus_3_dot_32 - location
		loc_bar__minus_0_dot_63_bar_0_dot_00_bar_3_dot_70 - location
		loc_bar__minus_1_dot_66_bar_1_dot_50_bar__minus_3_dot_72 - location
		loc_bar_0_dot_02_bar_1_dot_50_bar__minus_1_dot_99 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(headTiltZero agent1)
		(agentAtLocation agent1 loc_bar__minus_2_dot_14_bar_0_dot_46_bar__minus_3_dot_32)
		(objectAtLocation legal_97c5a2a9_1ce3_4b9b_9b97_18583972e984 loc_bar__minus_0_dot_63_bar_0_dot_00_bar_3_dot_70)
		(objectAtLocation legal_wall_06b598b5_91c6_409b_aadd_04e0645c722a loc_bar__minus_1_dot_66_bar_1_dot_50_bar__minus_3_dot_72)
		(objectAtLocation legal_wall_4c48a876_7ce0_4e8e_ad49_040d2e529abd loc_bar_0_dot_02_bar_1_dot_50_bar__minus_1_dot_99)
	)
	(:goal
		(and
			(held agent1 legal_97c5a2a9_1ce3_4b9b_9b97_18583972e984)
		)
	)
)
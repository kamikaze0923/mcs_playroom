(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_0c5a06fb_b27b_4121_9575_820ce9e6165d - object
		legal_wall_9a7855ed_ac58_4326_8c56_e36e4be36d93 - object
		loc_bar_2_dot_74_bar_0_dot_46_bar_0_dot_14 - location
		loc_bar_3_dot_17_bar_0_dot_01_bar__minus_0_dot_19 - location
		loc_bar__minus_2_dot_18_bar_1_dot_50_bar_1_dot_83 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(headTiltZero agent1)
		(agentAtLocation agent1 loc_bar_2_dot_74_bar_0_dot_46_bar_0_dot_14)
		(objectAtLocation legal_0c5a06fb_b27b_4121_9575_820ce9e6165d loc_bar_3_dot_17_bar_0_dot_01_bar__minus_0_dot_19)
		(objectAtLocation legal_wall_9a7855ed_ac58_4326_8c56_e36e4be36d93 loc_bar__minus_2_dot_18_bar_1_dot_50_bar_1_dot_83)
	)
	(:goal
		(and
			(held agent1 legal_0c5a06fb_b27b_4121_9575_820ce9e6165d)
		)
	)
)
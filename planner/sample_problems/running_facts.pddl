(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_b9abf958_963e_4bda_9fd4_c5d42b4e3e1a - object
		loc_bar__minus_2_dot_00_bar_0_dot_46_bar__minus_2_dot_95 - location
		loc_bar_1_dot_45_bar_0_dot_00_bar__minus_0_dot_09 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(headTiltZero agent1)
		(agentAtLocation agent1 loc_bar__minus_2_dot_00_bar_0_dot_46_bar__minus_2_dot_95)
		(objectAtLocation legal_b9abf958_963e_4bda_9fd4_c5d42b4e3e1a loc_bar_1_dot_45_bar_0_dot_00_bar__minus_0_dot_09)
	)
	(:goal
		(and
			(agentAtLocation agent1 loc_bar_1_dot_45_bar_0_dot_00_bar__minus_0_dot_09)
		)
	)
)
(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_1daab986_cd2b_4825_bea7_9390bb7a291c - object
		legal_wall_259aada8_45cf_45d5_942e_da0a17651188 - object
		loc_bar__minus_3_dot_37_bar_0_dot_46_bar_1_dot_35 - location
		loc_bar__minus_1_dot_60_bar_0_dot_00_bar_3_dot_21 - location
		loc_bar_1_dot_98_bar_1_dot_50_bar__minus_0_dot_57 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(headTiltZero agent1)
		(agentAtLocation agent1 loc_bar__minus_3_dot_37_bar_0_dot_46_bar_1_dot_35)
		(objectAtLocation legal_1daab986_cd2b_4825_bea7_9390bb7a291c loc_bar__minus_1_dot_60_bar_0_dot_00_bar_3_dot_21)
		(objectAtLocation legal_wall_259aada8_45cf_45d5_942e_da0a17651188 loc_bar_1_dot_98_bar_1_dot_50_bar__minus_0_dot_57)
	)
	(:goal
		(and
			(held agent1 legal_1daab986_cd2b_4825_bea7_9390bb7a291c)
		)
	)
)
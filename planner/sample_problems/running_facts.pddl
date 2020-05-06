(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_33fc71f6_f59c_4d59_a417_b61496cfe188 - object
		loc_bar__minus_2_dot_00_bar_0_dot_46_bar__minus_3_dot_42 - location
		loc_bar__minus_4_dot_65_bar_0_dot_05_bar_2_dot_78 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(agentAtLocation agent1 loc_bar__minus_2_dot_00_bar_0_dot_46_bar__minus_3_dot_42)
		(objectAtLocation legal_33fc71f6_f59c_4d59_a417_b61496cfe188 loc_bar__minus_4_dot_65_bar_0_dot_05_bar_2_dot_78)
	)
	(:goal
		(and
			(held agent1 legal_33fc71f6_f59c_4d59_a417_b61496cfe188)
		)
	)
)
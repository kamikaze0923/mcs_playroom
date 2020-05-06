(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_66912396_9f64_4721_a443_bef8e343d759 - object
		legal_3e3431fb_54e1_47b4_a629_668883382eee - object
		loc_bar_0_dot_17_bar_0_dot_47_bar__minus_0_dot_03 - location
		loc_bar__minus_0_dot_11_bar_0_dot_00_bar_3_dot_32 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(agentAtLocation agent1 loc_bar_0_dot_17_bar_0_dot_47_bar__minus_0_dot_03)
		(objectAtLocation legal_3e3431fb_54e1_47b4_a629_668883382eee loc_bar__minus_0_dot_11_bar_0_dot_00_bar_3_dot_32)
	)
	(:goal
		(and
			(held agent1 legal_66912396_9f64_4721_a443_bef8e343d759)
		)
	)
)
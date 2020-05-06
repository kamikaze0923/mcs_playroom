(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_b55eb3b1_de05_4f2d_b489_ab62aa1a7ffd - object
		loc_bar__minus_2_dot_73_bar_0_dot_01_bar__minus_2_dot_76 - location
		loc_bar__minus_2_dot_73_bar_0_dot_01_bar__minus_2_dot_76 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(lookingAtObject agent1 legal_b55eb3b1_de05_4f2d_b489_ab62aa1a7ffd)
		(agentAtLocation agent1 loc_bar__minus_2_dot_73_bar_0_dot_01_bar__minus_2_dot_76)
		(objectAtLocation legal_b55eb3b1_de05_4f2d_b489_ab62aa1a7ffd loc_bar__minus_2_dot_73_bar_0_dot_01_bar__minus_2_dot_76)
	)
	(:goal
		(and
			(held agent1 legal_b55eb3b1_de05_4f2d_b489_ab62aa1a7ffd)
		)
	)
)
(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_ce3a503a_55a8_4977_955e_11f187585556 - object
		loc_bar_0_dot_60_bar_0_dot_46_bar_3_dot_81 - location
		loc_bar__minus_2_dot_14_bar_0_dot_01_bar_3_dot_77 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(headTiltZero agent1)
		(agentAtLocation agent1 loc_bar_0_dot_60_bar_0_dot_46_bar_3_dot_81)
		(objectAtLocation legal_ce3a503a_55a8_4977_955e_11f187585556 loc_bar__minus_2_dot_14_bar_0_dot_01_bar_3_dot_77)
	)
	(:goal
		(and
			(held agent1 legal_ce3a503a_55a8_4977_955e_11f187585556)
		)
	)
)
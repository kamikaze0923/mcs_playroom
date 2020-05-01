(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_973ff858_d79d_4e49_9cee_8cb015b8277e - object
		loc_bar_0_dot_69_bar_0_dot_46_bar__minus_0_dot_72 - location
		loc_bar_4_dot_12_bar_0_dot_12_bar__minus_1_dot_04 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(headTiltZero agent1)
		(agentAtLocation agent1 loc_bar_0_dot_69_bar_0_dot_46_bar__minus_0_dot_72)
		(objectAtLocation legal_973ff858_d79d_4e49_9cee_8cb015b8277e loc_bar_4_dot_12_bar_0_dot_12_bar__minus_1_dot_04)
	)
	(:goal
		(and
			(held agent1 legal_973ff858_d79d_4e49_9cee_8cb015b8277e)
		)
	)
)
(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_1d2492ec_46c1_4dfd_8a8f_23ccb3089598 - object
		loc_bar_3_dot_95_bar_0_dot_01_bar_2_dot_81 - location
		loc_bar_3_dot_95_bar_0_dot_01_bar_2_dot_81 - location
	)
	(:init
		(= (totalCost) 0)
		(held agent1 legal_1d2492ec_46c1_4dfd_8a8f_23ccb3089598)
		(lookingAtObject agent1 legal_1d2492ec_46c1_4dfd_8a8f_23ccb3089598)
		(agentAtLocation agent1 loc_bar_3_dot_95_bar_0_dot_01_bar_2_dot_81)
		(objectAtLocation legal_1d2492ec_46c1_4dfd_8a8f_23ccb3089598 loc_bar_3_dot_95_bar_0_dot_01_bar_2_dot_81)
	)
	(:goal
		(and
			(held agent1 legal_1d2492ec_46c1_4dfd_8a8f_23ccb3089598)
		)
	)
)
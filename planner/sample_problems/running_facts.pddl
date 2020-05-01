(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_224b85ca_3c46_4d7d_8345_bfa80d720d29 - object
		legal_wall_44536f27_24fe_4585_86f6_f1a212328102 - object
		loc_bar__minus_3_dot_77_bar_0_dot_46_bar__minus_4_dot_53 - location
		loc_bar_4_dot_49_bar_0_dot_01_bar_4_dot_50 - location
		loc_bar_1_dot_74_bar_1_dot_50_bar__minus_1_dot_03 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(headTiltZero agent1)
		(agentAtLocation agent1 loc_bar__minus_3_dot_77_bar_0_dot_46_bar__minus_4_dot_53)
		(objectAtLocation legal_224b85ca_3c46_4d7d_8345_bfa80d720d29 loc_bar_4_dot_49_bar_0_dot_01_bar_4_dot_50)
		(objectAtLocation legal_wall_44536f27_24fe_4585_86f6_f1a212328102 loc_bar_1_dot_74_bar_1_dot_50_bar__minus_1_dot_03)
	)
	(:goal
		(and
			(held agent1 legal_224b85ca_3c46_4d7d_8345_bfa80d720d29)
		)
	)
)
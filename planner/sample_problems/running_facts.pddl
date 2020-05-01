(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_525102ed_b3fe_4c5c_b2f0_2c349ae75a10 - object
		legal_b0995b8a_0992_4d13_825d_06c7b7577dad - object
		legal_15850797_6965_4b1c_aa47_1496558e5868 - object
		legal_1c93c57c_3a51_48e1_8f3e_71244be1f816 - object
		loc_bar_4_dot_52_bar_0_dot_46_bar__minus_3_dot_55 - location
		loc_bar_0_dot_17_bar_0_dot_47_bar__minus_0_dot_03 - location
		loc_bar_0_dot_38_bar_0_dot_00_bar__minus_2_dot_58 - location
		loc_bar_0_dot_17_bar_0_dot_47_bar__minus_0_dot_03 - location
		loc_bar__minus_1_dot_33_bar_0_dot_00_bar__minus_0_dot_61 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(inReceptacle legal_525102ed_b3fe_4c5c_b2f0_2c349ae75a10 legal_b0995b8a_0992_4d13_825d_06c7b7577dad)
		(inReceptacle legal_525102ed_b3fe_4c5c_b2f0_2c349ae75a10 legal_1c93c57c_3a51_48e1_8f3e_71244be1f816)
		(agentAtLocation agent1 loc_bar_4_dot_52_bar_0_dot_46_bar__minus_3_dot_55)
		(objectAtLocation legal_525102ed_b3fe_4c5c_b2f0_2c349ae75a10 loc_bar_0_dot_17_bar_0_dot_47_bar__minus_0_dot_03)
		(objectAtLocation legal_b0995b8a_0992_4d13_825d_06c7b7577dad loc_bar_0_dot_38_bar_0_dot_00_bar__minus_2_dot_58)
		(objectAtLocation legal_15850797_6965_4b1c_aa47_1496558e5868 loc_bar_0_dot_17_bar_0_dot_47_bar__minus_0_dot_03)
		(objectAtLocation legal_1c93c57c_3a51_48e1_8f3e_71244be1f816 loc_bar__minus_1_dot_33_bar_0_dot_00_bar__minus_0_dot_61)
		(openable legal_b0995b8a_0992_4d13_825d_06c7b7577dad)
		(openable legal_1c93c57c_3a51_48e1_8f3e_71244be1f816)
	)
	(:goal
		(and
			(held agent1 legal_525102ed_b3fe_4c5c_b2f0_2c349ae75a10)
		)
	)
)
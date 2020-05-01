(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_6939183f_c90f_43d4_a9fa_35210461a4f5 - object
		legal_wall_1542d192_c706_4ba7_a334_c3ec6fb3cc74 - object
		legal_wall_533d8851_3bfc_4104_b59b_f92be04fa14e - object
		legal_wall_16d68ea3_cde0_44c0_bc59_c21ced776ca5 - object
		loc_bar__minus_0_dot_99_bar_0_dot_00_bar_0_dot_69 - location
		loc_bar__minus_0_dot_99_bar_0_dot_00_bar_0_dot_69 - location
		loc_bar__minus_2_dot_56_bar_1_dot_50_bar_1_dot_62 - location
		loc_bar_2_dot_51_bar_1_dot_50_bar__minus_2_dot_99 - location
		loc_bar__minus_2_dot_72_bar_1_dot_50_bar_2_dot_46 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(headTiltZero agent1)
		(agentAtLocation agent1 loc_bar__minus_0_dot_99_bar_0_dot_00_bar_0_dot_69)
		(objectAtLocation legal_6939183f_c90f_43d4_a9fa_35210461a4f5 loc_bar__minus_0_dot_99_bar_0_dot_00_bar_0_dot_69)
		(objectAtLocation legal_wall_1542d192_c706_4ba7_a334_c3ec6fb3cc74 loc_bar__minus_2_dot_56_bar_1_dot_50_bar_1_dot_62)
		(objectAtLocation legal_wall_533d8851_3bfc_4104_b59b_f92be04fa14e loc_bar_2_dot_51_bar_1_dot_50_bar__minus_2_dot_99)
		(objectAtLocation legal_wall_16d68ea3_cde0_44c0_bc59_c21ced776ca5 loc_bar__minus_2_dot_72_bar_1_dot_50_bar_2_dot_46)
	)
	(:goal
		(and
			(held agent1 legal_6939183f_c90f_43d4_a9fa_35210461a4f5)
		)
	)
)
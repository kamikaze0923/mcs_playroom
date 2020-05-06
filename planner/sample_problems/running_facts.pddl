(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_dd2d5768_c319_43e2_8d0a_50ecdf3bd251 - object
		legal_0f985dcd_ba52_4d43_8406_750bb60e5ec2 - object
		legal_wall_5006179f_e0af_4111_8537_c82419bd15e1 - object
		legal_wall_5dbcf004_a148_4e04_91f2_27ff81347444 - object
		legal_wall_26ecd05a_abad_4590_b6be_b061e1d18017 - object
		loc_bar_0_dot_58_bar_0_dot_46_bar__minus_0_dot_17 - location
		loc_bar__minus_1_dot_26_bar_0_dot_12_bar_3_dot_29 - location
		loc_bar_0_dot_45_bar_0_dot_00_bar__minus_1_dot_46 - location
		loc_bar__minus_3_dot_20_bar_1_dot_50_bar__minus_1_dot_64 - location
		loc_bar_3_dot_34_bar_1_dot_50_bar_1_dot_85 - location
		loc_bar_0_dot_66_bar_1_dot_50_bar_0_dot_71 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(headTiltZero agent1)
		(agentAtLocation agent1 loc_bar_0_dot_58_bar_0_dot_46_bar__minus_0_dot_17)
		(objectAtLocation legal_dd2d5768_c319_43e2_8d0a_50ecdf3bd251 loc_bar__minus_1_dot_26_bar_0_dot_12_bar_3_dot_29)
		(objectAtLocation legal_0f985dcd_ba52_4d43_8406_750bb60e5ec2 loc_bar_0_dot_45_bar_0_dot_00_bar__minus_1_dot_46)
		(objectAtLocation legal_wall_5006179f_e0af_4111_8537_c82419bd15e1 loc_bar__minus_3_dot_20_bar_1_dot_50_bar__minus_1_dot_64)
		(objectAtLocation legal_wall_5dbcf004_a148_4e04_91f2_27ff81347444 loc_bar_3_dot_34_bar_1_dot_50_bar_1_dot_85)
		(objectAtLocation legal_wall_26ecd05a_abad_4590_b6be_b061e1d18017 loc_bar_0_dot_66_bar_1_dot_50_bar_0_dot_71)
	)
	(:goal
		(and
			(objectOnTopOf legal_dd2d5768_c319_43e2_8d0a_50ecdf3bd251 legal_0f985dcd_ba52_4d43_8406_750bb60e5ec2)
		)
	)
)
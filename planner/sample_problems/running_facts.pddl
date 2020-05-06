(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_b30f79c6_44e4_4a4e_b7c3_778895a984cf - object
		legal_6d090ddd_99cc_4116_b459_fe68489dab96 - object
		legal_7cdd018c_6ac2_4a4e_87fe_629929ff0a3e - object
		legal_b3ca1f8d_dfe4_435e_ad3f_9c4686f85aac - object
		legal_wall_73e37fbc_c649_44a4_85e0_16a46afd968d - object
		loc_bar__minus_0_dot_62_bar_0_dot_15_bar_3_dot_35 - location
		loc_bar_3_dot_06_bar_0_dot_00_bar__minus_2_dot_74 - location
		loc_bar_2_dot_26_bar_0_dot_00_bar_1_dot_63 - location
		loc_bar__minus_0_dot_62_bar_0_dot_15_bar_3_dot_35 - location
		loc_bar__minus_3_dot_49_bar_1_dot_50_bar__minus_3_dot_36 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(lookingAtObject agent1 legal_b3ca1f8d_dfe4_435e_ad3f_9c4686f85aac)
		(inReceptacle legal_b30f79c6_44e4_4a4e_b7c3_778895a984cf legal_b3ca1f8d_dfe4_435e_ad3f_9c4686f85aac)
		(agentAtLocation agent1 loc_bar__minus_0_dot_62_bar_0_dot_15_bar_3_dot_35)
		(objectAtLocation legal_6d090ddd_99cc_4116_b459_fe68489dab96 loc_bar_3_dot_06_bar_0_dot_00_bar__minus_2_dot_74)
		(objectAtLocation legal_7cdd018c_6ac2_4a4e_87fe_629929ff0a3e loc_bar_2_dot_26_bar_0_dot_00_bar_1_dot_63)
		(objectAtLocation legal_b3ca1f8d_dfe4_435e_ad3f_9c4686f85aac loc_bar__minus_0_dot_62_bar_0_dot_15_bar_3_dot_35)
		(objectAtLocation legal_wall_73e37fbc_c649_44a4_85e0_16a46afd968d loc_bar__minus_3_dot_49_bar_1_dot_50_bar__minus_3_dot_36)
		(openable legal_b3ca1f8d_dfe4_435e_ad3f_9c4686f85aac)
		(isOpened legal_b3ca1f8d_dfe4_435e_ad3f_9c4686f85aac)
	)
	(:goal
		(and
			(held agent1 legal_b30f79c6_44e4_4a4e_b7c3_778895a984cf)
		)
	)
)
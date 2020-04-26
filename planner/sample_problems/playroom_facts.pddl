(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_a897ea51_b8a6_4f3f_8192_b64ef45aa8ef - object
		legal_4c27a8a8_e6e5_4c8e_88aa_b82270ccd251 - object
		legal_5265b49f_ca33_48fa_8788_564e63060dca - object
		legal_b2f02cdc_8d33_4e50_80b4_1292b3d362d3 - object
		legal_wall_4b8138e7_c14e_48bc_ac40_6c7f78248490 - object
		legal_wall_76919205_2ecd_4c75_a2cf_26be375726b4 - object
		loc_bar_1_dot_29_bar_0_dot_46_bar__minus_1_dot_55 - location
		loc_bar_4_dot_71_bar_0_dot_00_bar_1_dot_46 - location
		loc_bar_4_dot_33_bar_0_dot_00_bar_3_dot_15 - location
		loc_bar_0_dot_63_bar_0_dot_00_bar_2_dot_81 - location
		loc_bar__minus_2_dot_29_bar_0_dot_01_bar_2_dot_08 - location
		loc_bar_2_dot_05_bar_1_dot_50_bar__minus_0_dot_86 - location
		loc_bar__minus_3_dot_56_bar_1_dot_50_bar_2_dot_05 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(headTiltZero agent1)
		(agentAtLocation agent1 loc_bar_1_dot_29_bar_0_dot_46_bar__minus_1_dot_55)
		(objectAtLocation legal_a897ea51_b8a6_4f3f_8192_b64ef45aa8ef loc_bar_4_dot_71_bar_0_dot_00_bar_1_dot_46)
		(objectAtLocation legal_4c27a8a8_e6e5_4c8e_88aa_b82270ccd251 loc_bar_4_dot_33_bar_0_dot_00_bar_3_dot_15)
		(objectAtLocation legal_5265b49f_ca33_48fa_8788_564e63060dca loc_bar_0_dot_63_bar_0_dot_00_bar_2_dot_81)
		(objectAtLocation legal_b2f02cdc_8d33_4e50_80b4_1292b3d362d3 loc_bar__minus_2_dot_29_bar_0_dot_01_bar_2_dot_08)
		(objectAtLocation legal_wall_4b8138e7_c14e_48bc_ac40_6c7f78248490 loc_bar_2_dot_05_bar_1_dot_50_bar__minus_0_dot_86)
		(objectAtLocation legal_wall_76919205_2ecd_4c75_a2cf_26be375726b4 loc_bar__minus_3_dot_56_bar_1_dot_50_bar_2_dot_05)
	)
	(:goal
		(and
			(agentAtLocation agent1 loc_bar_4_dot_71_bar_0_dot_00_bar_1_dot_46)
		)
	)
)
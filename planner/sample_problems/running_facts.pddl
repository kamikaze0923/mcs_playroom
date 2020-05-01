(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_c438190b_bddf_4bd3_9cc2_863ca57d3a55 - object
		legal_00fb799f_f4db_4889_a687_6df4eb6b9e09 - object
		legal_18c34e49_e169_46fa_a038_dc3f5fbb9b70 - object
		legal_ecfcc9f7_03fd_431e_bc7d_82e868adae15 - object
		loc_bar__minus_4_dot_15_bar_0_dot_46_bar_0_dot_60 - location
		loc_bar_0_dot_00_bar__minus_0_dot_06_bar__minus_0_dot_18 - location
		loc_bar__minus_0_dot_97_bar_0_dot_15_bar__minus_2_dot_62 - location
		loc_bar_0_dot_00_bar__minus_0_dot_06_bar__minus_0_dot_13 - location
		loc_bar__minus_3_dot_08_bar_0_dot_15_bar_2_dot_08 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(headTiltZero agent1)
		(inReceptacle legal_c438190b_bddf_4bd3_9cc2_863ca57d3a55 legal_00fb799f_f4db_4889_a687_6df4eb6b9e09)
		(inReceptacle legal_c438190b_bddf_4bd3_9cc2_863ca57d3a55 legal_ecfcc9f7_03fd_431e_bc7d_82e868adae15)
		(agentAtLocation agent1 loc_bar__minus_4_dot_15_bar_0_dot_46_bar_0_dot_60)
		(objectAtLocation legal_c438190b_bddf_4bd3_9cc2_863ca57d3a55 loc_bar_0_dot_00_bar__minus_0_dot_06_bar__minus_0_dot_18)
		(objectAtLocation legal_00fb799f_f4db_4889_a687_6df4eb6b9e09 loc_bar__minus_0_dot_97_bar_0_dot_15_bar__minus_2_dot_62)
		(objectAtLocation legal_18c34e49_e169_46fa_a038_dc3f5fbb9b70 loc_bar_0_dot_00_bar__minus_0_dot_06_bar__minus_0_dot_13)
		(objectAtLocation legal_ecfcc9f7_03fd_431e_bc7d_82e868adae15 loc_bar__minus_3_dot_08_bar_0_dot_15_bar_2_dot_08)
		(openable legal_00fb799f_f4db_4889_a687_6df4eb6b9e09)
		(openable legal_ecfcc9f7_03fd_431e_bc7d_82e868adae15)
	)
	(:goal
		(and
			(held agent1 legal_c438190b_bddf_4bd3_9cc2_863ca57d3a55)
		)
	)
)
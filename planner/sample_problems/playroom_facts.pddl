(define (problem ball_and_bowl)
	(:domain playroom)
	(:metric minimize (totalCost))
	(:objects
		agent1 - agent
		legal_96423a7d_10e7_4c26_a88a_428b20696bd2 - object
		legal_wall_2738f33d_170f_4778_9976_5e95eaf5198f - object
		legal_wall_59c863b5_bd1b_4030_8c4e_5083d2be5739 - object
		loc_bar_1_dot_88_bar_0_dot_46_bar__minus_0_dot_39 - location
		loc_bar_1_dot_30_bar_0_dot_05_bar__minus_4_dot_01 - location
		loc_bar_2_dot_00_bar_1_dot_50_bar__minus_0_dot_59 - location
		loc_bar_1_dot_08_bar_1_dot_50_bar_4_dot_62 - location
	)
	(:init
		(= (totalCost) 0)
		(handEmpty agent1)
		(headTiltZero agent1)
		(agentAtLocation agent1 loc_bar_1_dot_88_bar_0_dot_46_bar__minus_0_dot_39)
		(objectAtLocation legal_96423a7d_10e7_4c26_a88a_428b20696bd2 loc_bar_1_dot_30_bar_0_dot_05_bar__minus_4_dot_01)
		(objectAtLocation legal_wall_2738f33d_170f_4778_9976_5e95eaf5198f loc_bar_2_dot_00_bar_1_dot_50_bar__minus_0_dot_59)
		(objectAtLocation legal_wall_59c863b5_bd1b_4030_8c4e_5083d2be5739 loc_bar_1_dot_08_bar_1_dot_50_bar_4_dot_62)
	)
	(:goal
		(and
			(held agent1 legal_96423a7d_10e7_4c26_a88a_428b20696bd2)
		)
	)
)
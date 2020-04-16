
(define (problem ball_and_bowl)
    (:domain playroom)
    (:metric minimize (totalCost))
    (:objects
        agent1 - agent
        BallType - otype
        BowlType - rtype
        PlateType - rtype

        ball_a - object
        ball_b - object
        ball_c - object
        ball_d - object
        cup_a - object
        cup_b - object
        bowl_a - object
        bowl_b - object
        plate_a - object
        plate_b - ojbect
        box_a - object
        box_b - object

        ;loc_bar_0_dot_0_bar_0_dot_04625_bar__minus_1_dot_0                   ;agent1
        loc_bar_1_dot_31_bar_0_dot_04625_bar_0_dot_40                         ;agent1
        loc_bar_0_dot_0_bar_0_dot_0125_bar_1_dot_0 - location                 ;ball_a
        loc_bar_0_dot_0_bar_0_dot_025_bar_1_dot_25 - location                 ;ball_b
        loc_bar_0_dot_0_bar_0_dot_05_bar_1_dot_5 - location                   ;ball_c
        loc_bar_0_dot_0_bar_0_dot_125_bar_1_dot_75 - location                 ;ball_d

        loc_bar__minus_0_dot_5_bar_0_dot_050_bar_1_dot_0 - location           ;bowl_a
        loc_bar__minus_1_dot_0_bar_0_dot_035_bar_1_dot_0 - location           ;bowl_b

        loc_bar__minus_0_dot_5_bar_0_dot_064_bar_1_dot_5 - location           ;cup_a
        loc_bar__minus_1_dot_0_bar_0_dot_049_bar_1_dot_5 - location           ;cup_b

        loc_bar__minus_0_dot_5_bar_0_dot_009_bar_2_dot_0 - location           ;plate_a
        loc_bar__minus_1_dot_0_bar_0_dot_013_bar_2_dot_0 - location           ;plate_b

        loc_bar__minus_0_dot_5_bar_0_dot_054_bar__minus_0_dot_145 - location  ;box_a
        loc_bar_0_dot_5_bar_0_dot_079_bar__minus_0_dot_065 - location         ;box_b
    )

    (:init
        (= (totalCost) 0)

        (canPutin ball_b bowl_a)
        (canPutin ball_d plate_b)

        (canPutin ball_a cup_b)
        (canPutin cup_b plate_a)

        (canPutin ball_a box_a)
        (canPutin cup_b box_a)
        (canPutin plate_a box_a)

        (agentAtLocation agent1 loc_bar_1_dot_31_bar_0_dot_04625_bar_0_dot_40)
        (handEmpty agent1)

        (objectAtLocation ball_a loc_bar_0_dot_0_bar_0_dot_0125_bar_1_dot_0)
        (objectAtLocation ball_b loc_bar_0_dot_0_bar_0_dot_025_bar_1_dot_25)
        (objectAtLocation ball_c loc_bar_0_dot_0_bar_0_dot_05_bar_1_dot_5)
        (objectAtLocation ball_d loc_bar_0_dot_0_bar_0_dot_125_bar_1_dot_75)

        (objectAtLocation cup_a loc_bar__minus_0_dot_5_bar_0_dot_064_bar_1_dot_5)
        (objectAtLocation cup_b loc_bar__minus_1_dot_0_bar_0_dot_049_bar_1_dot_5)

        (objectAtLocation bowl_a loc_bar__minus_0_dot_5_bar_0_dot_050_bar_1_dot_0)
        (objectAtLocation bowl_b loc_bar__minus_1_dot_0_bar_0_dot_035_bar_1_dot_0)

        (objectAtLocation plate_a loc_bar__minus_0_dot_5_bar_0_dot_009_bar_2_dot_0)
        (objectAtLocation plate_b loc_bar__minus_1_dot_0_bar_0_dot_013_bar_2_dot_0)

        (objectAtLocation box_a loc_bar__minus_0_dot_5_bar_0_dot_054_bar__minus_0_dot_145)
        (objectAtLocation box_b loc_bar_0_dot_5_bar_0_dot_079_bar__minus_0_dot_065)

    )

    (:goal
        (and
            (inReceptacle plate_a box_a)
            (inReceptacle cup_b plate_a)
            (inReceptacle ball_a cup_b)

            ;(objectAtLocation box_a loc_bar__minus_0_dot_5_bar_0_dot_054_bar__minus_0_dot_145)
            ;(objectAtLocation plate_a loc_bar__minus_0_dot_5_bar_0_dot_054_bar__minus_0_dot_145)
            ;(objectAtLocation cup_b loc_bar__minus_0_dot_5_bar_0_dot_054_bar__minus_0_dot_145)
            ;(objectAtLocation ball_a loc_bar__minus_0_dot_5_bar_0_dot_054_bar__minus_0_dot_145)
        )

    )

)
        

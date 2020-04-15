
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
        bowl_a - object
        plate_b - ojbect

        loc_bar_0_dot_0_bar_0_dot_04625_bar__minus_1_dot_0                    ;agent1
        loc_bar_0_dot_0_bar_0_dot_0125_bar_1_dot_0 - location                 ;ball_a
        loc_bar_0_dot_0_bar_0_dot_025_bar_1_dot_25 - location                 ;ball_b
        loc_bar_0_dot_0_bar_0_dot_05_bar_1_dot_5 - location                   ;ball_c
        loc_bar_0_dot_0_bar_0_dot_125_bar_1_dot_75 - location                 ;ball_d
        loc_bar__minus_0_dot_5_bar_0_dot_0496_bar_1_dot_0 - location          ;bowl_a
        loc_bar__minus_1_dot_0_bar_0_dot_013_bar_2_dot_0 - location           ;plate_b
    )

    (:init
        (= (totalCost) 0)
        (receptacleType bowl_a BowlType)
        (receptacleType plate_b PlateType)

        (commonObjectType ball_a BallType)
        (commonObjectType ball_b BallType)
        (commonObjectType ball_c BallType)
        (commonObjectType ball_d BallType)

        (canContain BowlType BallType)
        (canContain PlateType BallType)

        (agentAtLocation agent1 loc_bar_0_dot_0_bar_0_dot_04625_bar__minus_1_dot_0)
        (handEmpty agent1)

        (objectAtLocation ball_a loc_bar_0_dot_0_bar_0_dot_0125_bar_1_dot_0)
        (objectAtLocation ball_b loc_bar_0_dot_0_bar_0_dot_025_bar_1_dot_25)
        (objectAtLocation ball_c loc_bar_0_dot_0_bar_0_dot_05_bar_1_dot_5)
        (objectAtLocation ball_d loc_bar_0_dot_0_bar_0_dot_125_bar_1_dot_75)

        (objectAtLocation bowl_a loc_bar__minus_0_dot_5_bar_0_dot_0496_bar_1_dot_0)
        (objectAtLocation plate_b loc_bar__minus_1_dot_0_bar_0_dot_013_bar_2_dot_0)

    )

    (:goal
        (and
            (held agent1 ball_a)
            (inReceptacle ball_b bowl_a)
            (inReceptacle ball_d plate_b)
        )

    )

)
        

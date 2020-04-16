;; Specification in PDDL1 of the Question domain

(define (domain playroom)
 (:requirements
    :adl
 )
 (:types
  agent
  location
  object
 )

 (:predicates
    (agentAtLocation ?a - agent ?l - location)                ; true if the agent is at the location
    (objectAtLocation ?o - object ?l - location)              ; true if the object is at the location

    (lookingAtObject ?a - agent ?o - object)                  ; agent ?a is looking at object ?o
    (held ?a - agent ?o - object)                             ; agent ?a is holding object ?o
    (handEmpty ?a - agent)                                    ; agent ?a not holding anything
    (headTiltZero ?a - agent)                                 ; agent ?a is looking straightly to front

    (inReceptacle ?o1 - object ?o2 - object)                  ; object ?o1 is in receptacle ?o2
    (canPutin ?o1 - object ?o2 - object)                      ; true if ?o1 can be put in ?o2
 )

 (:functions
    (totalCost)
 )

;; All actions are specified such that the final arguments are the ones used
;; for performing actions in Unity.

 (:action FaceToFront
    :parameters (?a - agent)
    :effect (and
                (headTiltZero ?a)
                (forall (?o - object)
                    (not (lookingAtObject ?a ?o))
                )
                (increase (totalCost) 1)
            )
 )


 (:action GotoLocation
    :parameters (?a - agent ?lStart - location ?lEnd - location)
    :precondition (and
                       (agentAtLocation ?a ?lStart)
                       (headTiltZero ?a)
                  )
    :effect (and
                (agentAtLocation ?a ?lEnd)
                (not (agentAtLocation ?a ?lStart))
                (forall (?o - object)
                    (not (lookingAtObject ?a ?o))
                )
                (increase (totalCost) 10)
            )
 )

 (:action FaceToObject
    :parameters (?a - agent ?o - object ?l - location)
    :precondition (and
                      (agentAtLocation ?a ?l)
                      (objectAtLocation ?o ?l)
                  )
    :effect (and
                (lookingAtObject ?a ?o)
                (not (headTiltZero ?a))
                (increase (totalCost) 1)
            )
 )

 (:action PickUpObject
    :parameters (?a - agent ?o - object ?l - location)
    :precondition (and
                      (objectAtLocation ?o ?l)
                      (lookingAtObject ?a ?o)
                      (handEmpty ?a)
                  )
    :effect (and
                (held ?a ?o)
                (not (lookingAtObject ?a ?o))
                (not (objectAtLocation ?o ?l))
                (not (handEmpty ?a))
                (increase (totalCost) 1)
            )
 )

 (:action PutObjectIntoReceptacle
    :parameters (?a - agent ?o1 - object ?o2 - object ?l - location)
    :precondition (and
                    (objectAtLocation ?o2 ?l)
                    (lookingAtObject ?a ?o2)
                    (held ?a ?o1)
                    (not (handEmpty ?a))
                    (and
                        (canPutin ?o1 ?o2)
                    )

                  )
    :effect (and
                (not (held ?a ?o1))
                (inReceptacle ?o1 ?o2)
                (objectAtLocation ?o1 ?l)
                (handEmpty ?a)
                (increase (totalCost) 1)
            )
 )

)
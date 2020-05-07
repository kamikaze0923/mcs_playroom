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

    (handEmpty ?a - agent)                                    ; agent ?a not holding anything
    (headTiltZero ?a - agent)                                 ; agent ?a is looking straightly to front
    (lookingAtObject ?a - agent ?o - object)                  ; agent ?a is looking at object ?o
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
)
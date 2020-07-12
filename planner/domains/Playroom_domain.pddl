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
    (held ?a - agent ?o - object)                             ; agent ?a is holding object ?o
    (headTiltZero ?a - agent)                                 ; agent ?a is looking straightly to front
    (lookingAtObject ?a - agent ?o - object)                  ; agent ?a is looking at object ?o
    (inReceptacle ?o - object ?r - object)                    ; object ?o is in receptacle ?r
    (openable ?o - object)                                    ; true if ?o can be opened
    (isOpened ?o - object)                                    ; true if ?o is opened
    (isReceptacle ?r - object ?o - object)                    ; true if ?r is an receptacle for ?o

    (objectNextTo ?o - object ?g - object)                    ; object ?o is next to object ?g
    (objectOnTopOf ?o - object ?g - object)                   ; object ?o is on top of object ?g
 )

 (:functions
    (distance ?from ?to)
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
                (increase (totalCost) 0.01)
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
                (increase (totalCost) (distance ?lStart ?lEnd))
                ;(increase (totalCost) 0.01)
            )
 )

 (:action FaceToObject
    :parameters (?a - agent ?o - object ?l - location)
    :precondition (and
                      (agentAtLocation ?a ?l)
                      (objectAtLocation ?o ?l)
                      (not (held ?a ?o))
                      (headTiltZero ?a)
                  )
    :effect (and
                (lookingAtObject ?a ?o)
                (not (headTiltZero ?a))
                (increase (totalCost) 0.01)
            )
 )

 (:action PickUpObject
    :parameters (?a - agent ?o - object ?l - location)
    :precondition (and
                      (agentAtLocation ?a ?l)
                      (lookingAtObject ?a ?o)
                      (handEmpty ?a)
                      (or
                        (not (openable ?o))
                        (and
                          (not (isOpened ?o))
                          (openable ?o)
                        )
                      )
                  )
    :effect (and
                (held ?a ?o)
                (not (lookingAtObject ?a ?o))
                (not (objectAtLocation ?o ?l))
                (not (handEmpty ?a))
                (forall (?r1 - object)
                   (when (inReceptacle ?o ?r1)
                       (not (inReceptacle ?o ?r1))
                   )
                )
                (increase (totalCost) 0.01)
            )
 )

 (:action PutObjectIntoReceptacle
    :parameters (?a - agent ?r - object ?o - object ?l - location)
    :precondition (and
                      (agentAtLocation ?a ?l)
                      (objectAtLocation ?r ?l)
                      (lookingAtObject ?a ?r)
                      (held ?a ?o)
                      (isReceptacle ?r ?o)
                      (or
                        (not (openable ?r))
                        (and
                          (isOpened ?r)
                          (openable ?r)
                        )
                      )
                  )
    :effect (and
                (handEmpty ?a)
                (not (held ?a ?o))
                (inReceptacle ?o ?r)
                (forall (?o1 - object)
                    (when (inReceptacle ?o1 ?o)
                        (and
                            (objectAtLocation ?o1 ?l)
                            (inReceptacle ?o1 ?r)
                        )
                    )
                )
                (increase (totalCost) 0.01)
            )
 )

 (:action OpenObject
    :parameters (?a - agent ?r - object ?l - location)
    :precondition (and
                    (agentAtLocation ?a ?l)
                    (objectAtLocation ?r ?l)
                    (lookingAtObject ?a ?r)
                    (openable ?r)
                    (not (isOpened ?r))
                  )
    :effect (and
                (isOpened ?r)
                (increase (totalCost) 0.01)
            )
 )

 (:action CloseObject
    :parameters (?a - agent ?r - object ?l - location)
    :precondition (and
                    (agentAtLocation ?a ?l)
                    (objectAtLocation ?r ?l)
                    (lookingAtObject ?a ?r)
                    (openable ?r)
                    (isOpened ?r)
                  )
    :effect (and
                (not (isOpened ?r))
                (increase (totalCost) 0.01)
            )
 )

 ;(:action DropObjectNextTo
 ;   :parameters (?a - agent ?g - object ?o - object ?l - location)
 ;   :precondition (and
 ;                   (agentAtLocation ?a ?l)
 ;                   (objectAtLocation ?g ?l)
 ;                   (held ?a ?o)
 ;                   (not (handEmpty ?a))
 ;                 )
 ;   :effect (and
 ;               (handEmpty ?a)
 ;               (not (held ?a ?o))
 ;               (objectNextTo ?o ?g)
 ;               (forall (?o1 - object)
 ;                   (when (inReceptacle ?o1 ?o)
 ;                       (and
 ;                           (objectAtLocation ?o1 ?l)
 ;                           (objectNextTo ?o1 ?g)
 ;                       )
 ;                   )
 ;               )
 ;               (increase (totalCost) 0.01)
 ;           )
 ;)

 (:action DropObjectOnTopOf
    :parameters (?a - agent ?g - object ?o - object ?l - location)
    :precondition (and
                    (agentAtLocation ?a ?l)
                    (objectAtLocation ?g ?l)
                    (lookingAtObject ?a ?g)
                    (isReceptacle ?g ?o)
                    (held ?a ?o)
                    (not (handEmpty ?a))
                  )
    :effect (and
                (handEmpty ?a)
                (not (held ?a ?o))
                (objectOnTopOf ?o ?g)
                (inReceptacle ?o ?g)
                (forall (?o1 - object)
                    (when (inReceptacle ?o1 ?o)
                       (and
                            (objectAtLocation ?o1 ?l)
                            (objectOnTopOf ?o1 ?g)
                            ;(inReceptacle ?o1 ?g)
                       )

                    )
                )
                (increase (totalCost) 0.01)
            )
 )

)
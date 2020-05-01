	(:goal
        (exists (?o1 - object ?o2 - object)
            (and
                (isType ?o1 ballType)
                (isType ?o2 bowlType)
                (inReceptacle ?o1 ?o2)
            )
        )
	)

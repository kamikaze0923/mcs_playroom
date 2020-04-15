import time

from planner.ff_planner_handler import PlanParser

parser = PlanParser()

# Playroom Demo Plan
t_start = time.time()
result_plan = parser.get_plan_from_file(
    "planner/domains/Playroom_domain.pddl", "planner/sample_problems/problem_playroom.pddl"
)
print("Playroom Plan")
print("Plan took %.2f seconds" % (time.time() - t_start))
for plan in result_plan:
    print(plan)

from gym_ai2thor.envs.mcs_env import McsEnv


env = McsEnv(task="intphys_scenes", scene_type="gravity")

while True:
    env.reset(random_init=False)
    print(env.current_scene, env.scene_config['answer'], len(env.scene_config['goal']['action_list']))
    for _,x in enumerate(env.scene_config['goal']['action_list']):
        # print(i)
        assert len(x) == 1
        env.step(action=x[0])
    # env.controller.end_scene(None, None)



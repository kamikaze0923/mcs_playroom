class SceneState:
    def __init__(self, object_list):
        self.object_state_dict = {}
        self.static_object_set = set()
        for obj in object_list:
            self.static_object_set.add(obj.uuid)

    def update(self, object_list):
        for obj in object_list:
            if obj.uuid in self.static_object_set:
                continue
            obj_state = ObjectState(obj)
            if obj.uuid not in self.object_state_dict:
                self.object_state_dict[obj.uuid] = obj_state
            else:
                self.object_state_dict[obj.uuid].update(obj_state)
                # print("ID: {}, Velocity: {}".format(obj.uuid, self.object_state_dict[obj.uuid].velocity))


class ObjectState:
    def __init__(self, object_info):
        self.position = (object_info.position['x'], object_info.position['y'], object_info.position['z'])
        self.velocity = None
        self.velocity_history = []

    def update(self, new_object_state):
        v_x = round(new_object_state.position[0] - self.position[0], 3)
        v_y = round(new_object_state.position[1] - self.position[1], 3)
        v_z = round(new_object_state.position[2] - self.position[2], 3)
        if v_z != 0:
            print(v_z)
        if self.velocity is not None:
            self.velocity_history.append(self.velocity)
        self.velocity = (v_x, v_y)
        self.position = (new_object_state.position[0], new_object_state.position[1], new_object_state.position[2])
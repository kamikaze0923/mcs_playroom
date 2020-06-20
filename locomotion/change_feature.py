from int_phy_recollect_position import SHAPE_TYPES, SCENE_TYPES, DATA_SAVE_DIR, ON_GROUND_THRESHOLD
import os
import torch

torch.set_printoptions(profile="full", precision=2, linewidth=10000)


Y_IDX = [4, 7, 10, 13, 16, 19, 22, 25]


n = 0
for t in SHAPE_TYPES:
    shape_dir_no_occluder = os.path.join(DATA_SAVE_DIR, "without_occluder", t)
    shape_dir_occluder = os.path.join(DATA_SAVE_DIR, "with_occluder", t)
    for scene_dir in SCENE_TYPES:
        scene_dir_no_occluder = os.path.join(shape_dir_no_occluder, scene_dir)
        scene_dir_occluder = os.path.join(shape_dir_occluder, scene_dir)

        tensor_files = os.listdir(scene_dir_no_occluder)
        for one_file in sorted(tensor_files):
            no_occluder_file = os.path.join(scene_dir_no_occluder, one_file)
            print(no_occluder_file)
            tensor_no_occluder = torch.load(no_occluder_file)
            print(tensor_no_occluder.size())
            # tensor_no_occluder_min_bond = torch.min(tensor_no_occluder[:, :, Y_IDX], dim=2)[0]
            # tensor_no_occluder_on_ground = torch.logical_and(tensor_no_occluder_min_bond < ON_GROUND_THRESHOLD, tensor_no_occluder[:,:,-2] != 0)
            # tensor_no_occluder_on_ground = tensor_no_occluder_on_ground.unsqueeze(-1).float()
            # tensor_no_occluder = torch.cat([tensor_no_occluder[:,:,:-2], tensor_no_occluder_on_ground, tensor_no_occluder[:,:,-2:]], dim=2)
            # print(tensor_no_occluder.size())
            # print(tensor_no_occluder[0])
            # print("-" * 400)


            occluder_file = os.path.join(scene_dir_occluder, one_file)
            print(occluder_file)
            tensor_occluder = torch.load(occluder_file)
            print(tensor_occluder.size())
            # tensor_occluder_min_bond = torch.min(tensor_occluder[:, :, Y_IDX], dim=2)[0]
            # tensor_occluder_on_ground = torch.logical_and(tensor_occluder_min_bond < ON_GROUND_THRESHOLD, tensor_occluder[:,:,-2] != 0)
            # tensor_occluder_on_ground = tensor_occluder_on_ground.unsqueeze(-1).float()
            # tensor_occluder = torch.cat([tensor_occluder[:,:,:-2], tensor_occluder_on_ground, tensor_occluder[:,:,-2:]], dim=2)
            # print(tensor_occluder.size())
            # print(tensor_occluder[0])

            # torch.save(tensor_no_occluder, no_occluder_file)
            # torch.save(tensor_occluder, occluder_file)

            n += 1


print(n)

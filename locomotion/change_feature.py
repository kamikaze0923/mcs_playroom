from int_phy_recollect_position import SHAPE_TYPES, SCENE_TYPES, DATA_SAVE_DIR
import os
import torch

torch.set_printoptions(profile="full", precision=2, linewidth=10000)
LOWER_BONDING_BOX_IDX = [4,7,16,19]
ON_GROUND_THRESHOLD = 1e-3


SHAPE_TYPES = ["sphere"]
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

            occluder_file = os.path.join(scene_dir_occluder, one_file)
            print(occluder_file)
            tensor_occluder = torch.load(occluder_file)

            print(tensor_no_occluder.size(), tensor_occluder.size())

            tensor_no_occluder_min_bond_front = torch.min(tensor_no_occluder[:, :, [4, 7, 10, 13]], dim=2)[0]
            tensor_no_occluder_min_bond_rear = torch.min(tensor_no_occluder[:, :, [16, 19, 22, 25]], dim=2)[0]
            tensor_no_occluder_on_ground_front = torch.logical_and(torch.min(tensor_no_occluder[:,:,[4,7,10,13]], dim=2)[0] < ON_GROUND_THRESHOLD, tensor_no_occluder[:,:,0] != 0)
            tensor_no_occluder_on_ground_rear = torch.logical_and(torch.min(tensor_no_occluder[:,:,[16,19,22,25]], dim=2)[0] < ON_GROUND_THRESHOLD, tensor_no_occluder[:,:,0] != 0)

            # print(tensor_no_occluder[1])
            # print(tensor_no_occluder[0])
            for i in range(tensor_no_occluder.size()[0]):
                print(tensor_no_occluder_min_bond_front[i])
                print(tensor_no_occluder_min_bond_rear[i])
                print(tensor_no_occluder_on_ground_front[i])
                print(tensor_no_occluder_on_ground_rear[i])
                assert torch.equal(tensor_no_occluder_on_ground_front[i], tensor_no_occluder_on_ground_rear[i])

            # print('-' * 200)
            # print(tensor_occluder[1])
            # print(tensor_occluder[1][:,LOWER_BONDING_BOX_IDX])
            n += 1
            # torch.save(tensor_no_occluder, no_occluder_file)
            # torch.save(tensor_occluder, occluder_file)

print(n)

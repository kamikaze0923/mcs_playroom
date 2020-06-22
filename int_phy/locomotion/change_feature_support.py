from int_phy_recollect_position import SHAPE_TYPES, SCENE_TYPES, DATA_SAVE_DIR, ON_GROUND_THRESHOLD
import os
import torch

torch.set_printoptions(profile="full", precision=2, linewidth=10000)



n = 0
for t in SHAPE_TYPES:
    shape_dir_no_occluder = os.path.join(DATA_SAVE_DIR, "without_occluder", t)
    shape_dir_occluder = os.path.join(DATA_SAVE_DIR, "with_occluder", t)
    ground_dir = os.path.join(DATA_SAVE_DIR, "ground", t)
    for scene_dir in SCENE_TYPES:
        scene_dir_no_occluder = os.path.join(shape_dir_no_occluder, scene_dir)
        scene_dir_occluder = os.path.join(shape_dir_occluder, scene_dir)


        tensor_files = os.listdir(scene_dir_no_occluder)
        for one_file in sorted(tensor_files):
            no_occluder_file = os.path.join(scene_dir_no_occluder, one_file)
            print(no_occluder_file)
            tensor_no_occluder = torch.load(no_occluder_file)

            if scene_dir == "gravity":
                gravity_dir = os.path.join(ground_dir, scene_dir)
                ground_feature = torch.load(os.path.join(gravity_dir, one_file)).unsqueeze(1).repeat_interleave(60, dim=1)
                assert ground_feature.size()[0] == tensor_no_occluder.size()[0]
                object_x_to_idx = torch.round(tensor_no_occluder[:,:,[0]].repeat_interleave(5, dim=2) * 100 + 650).long()
                object_x_to_idx[:,:,0] -= 100 # 100 index = 1 meter
                object_x_to_idx[:,:,1] -= 50
                object_x_to_idx[:,:,3] += 50
                object_x_to_idx[:,:,4] += 100
                ground_feature = torch.gather(ground_feature, dim=2, index=object_x_to_idx)
                ground_dis = torch.zeros(size=(tensor_no_occluder.size()[0], tensor_no_occluder.size()[1], 5))
            else:
                ground_dis = torch.zeros(size=(tensor_no_occluder.size()[0], tensor_no_occluder.size()[1], 5))

            tensor_no_occluder = torch.cat(
                [tensor_no_occluder[:,:,:-3], ground_dis * tensor_no_occluder[:,:,[-2]], tensor_no_occluder[:,:,-2:]], dim=2
            )


            occluder_file = os.path.join(scene_dir_occluder, one_file)
            print(occluder_file)
            tensor_occluder = torch.load(occluder_file)
            tensor_occluder = torch.cat(
                [tensor_occluder[:,:,:-3], ground_dis * tensor_occluder[:,:,[-2]], tensor_occluder[:,:,-2:]], dim=2
            )

            # torch.save(tensor_no_occluder, no_occluder_file)
            # torch.save(tensor_occluder, occluder_file)

            n += 1


print(n)

from int_phy.object_state import get_object_frame_info
from int_phy.object_state import get_bonding_box_polygon


class OccluderState:
    def __init__(self, object_info, depth_frame, object_frame):
        self.id = object_info.uuid
        self.color = object_info.color
        self.depth, self.edge_pixels = get_object_frame_info(object_info, depth_frame, object_frame, depth_aggregation=max)
        self.bonding_box_poly = get_bonding_box_polygon(object_info)









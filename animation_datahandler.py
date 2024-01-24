from typing import List
import csc
import easy_csc

scene = csc.app.get_application().current_scene()


class AnimationDataHandler:
    def __init__(self, object_id: csc.model.ObjectId, interval: list = None):
        # object_id
        # glob_pos
        # loc_pos
        # glob_rot
        # loc_rot
        # scale
        # interval
        pass

    def verify_object(self):
        # Exists?
        # Has transforms?
        pass

    def get_transform_values(transform_type: str) -> List[List[float]]:
        pass

    def set_transform_values(transform_type: str, transform_values: List[List[float]]):
        pass

    @property
    def interval():
        pass

    def bake_interval(set_keyframe=False):
        pass

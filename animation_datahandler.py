from typing import List
import csc
import easy_csc

scene = csc.app.get_application().current_scene()


class AnimationDataHandler:
    behaviour_viewer = scene.behaviour_viewer()
    layer_viewer = scene.layers_viewer()

    def __init__(self, object_id: csc.model.ObjectId, interval: List[int] = None):
        self.object_id = object_id
        self.verify_object()
        self.global_position = self.get_transform_values("global_position")
        self.local_position = self.get_transform_values("local_position")
        self.global_rotation = self.get_transform_values("global_rotation")
        self.local_rotation = self.get_transform_values("local_rotation")
        self.local_scale = self.get_transform_values("local_scale")
        self.interval = interval if interval is not None else self.total_interval

    def verify_object(self):
        if self.object_id not in scene.model_viewer().get_objects():
            raise ValueError(f"Object with ID {self.object_id} does not exist.")
        if self.behaviour_viewer.get_behaviour_by_name(
            self.object_id, "Transform"
        ).is_null():
            raise ValueError(
                f"Object with ID {self.object_id} doesn't have Transform behaviour."
            )

    def get_transform_values(self, transform_type: str) -> List[List[float]]:
        # The tranform behaviour of our Cube
        transform_behaviour = self.behaviour_viewer.get_behaviour_by_name(
            self.object_id, "Transform"
        )
        # ID of the global position data
        transform_id = self.behaviour_viewer.get_behaviour_data(
            transform_behaviour, transform_type
        )
        data_viewer = scene.data_viewer()
        transform_values = [
            data_viewer.get_data_value(transform_id, frame)
            for frame in range(self.interval[0], self.interval[1])
        ]
        return transform_values

    def set_transform_values(transform_type: str, transform_values: List[List[float]]):
        pass

    @property
    def total_interval(self) -> List[int]:
        layer_id = self.layer_viewer.layer_id_by_obj_id(self.object_id)
        layer = self.layer_viewer.layer(layer_id)
        return [layer.key_frame_indices().first(), layer.key_frame_indices().last()]

    def bake_interval(self, set_keyframe=False):
        pass

    def __str__(self):
        message = f"""
        Animation data of object: {self.object_id}
        Global Position:
        {str(self.global_position)}
        Local Position:
        {str(self.local_position)}
        Global Rotation:
        {str(self.global_rotation)}
        Local Rotation:
        {str(self.local_rotation)}
        Scale:
        {str(self.local_scale)}
        """
        return message

from typing import List, Set
import csc

scene = csc.app.get_application().current_scene()

layer_viewer = scene.layers_viewer()
model_viewer = scene.model_viewer()
behaviour_viewer = model_viewer.behaviour_viewer()


######################
# Viewport Selection #
######################
# Get selected objects
def get_selected_objects() -> Set[csc.model.ObjectId]:
    """
    Getting the set of selected objects object ids.

    :return set: Set of ObjectId
    """
    return {
        sid
        for sid in scene.selector().selected().ids
        if isinstance(sid, csc.model.ObjectId)
    }


# Get selected object
def get_selected_object() -> csc.model.ObjectId:
    """
    Return the object id of the selected object

    :raises ValueError: If there is not exactly one object selected
    :return csc.model.ObjectId: Object ID of the selected object
    """
    selected_objects = get_selected_objects()
    if len(selected_objects) == 1:
        return next(iter(selected_objects))
    elif len(selected_objects) == 0:
        raise ValueError("No object selected.")
    else:
        raise ValueError("More than one object selected.")


# Select objects
def select_object(object_id: csc.model.ObjectId, extend: bool = False) -> None:
    if extend:
        current_selection = get_selected_objects()
        scene.selector().select(current_selection | set(object_id))
    else:
        scene.selector().select(set(object_id))


def select_objects(object_ids: Set[csc.model.ObjectId]) -> None:
    scene.selector().select(object_ids)


def select_all() -> None:
    """
    Selecting all object in the scene.
    """
    objects = model_viewer.get_objects()
    if len(objects) == 0:
        return

    def mod(model, update, sc, session):
        session.take_selector().select(set(objects), objects[0])

    scene.modify_with_session("Select all objects", mod)


def clear_selection() -> None:
    """
    Clear the selection of objects.
    """

    def mod(model, update, sc, session):
        session.take_selector().select(set(), csc.model.ObjectId.null())

    scene.modify_with_session("Clear object selection", mod)


def get_objects_by_type(type_name: str):
    objects = model_viewer.get_objects()
    return [
        obj
        for obj in objects
        if not behaviour_viewer.get_behaviour_by_name(obj, type_name).is_null()
    ]


def get_object_by_name(name: str) -> csc.model.ObjectId:
    for obj_id in model_viewer.get_objects():
        obj_name = model_viewer.get_object_name(obj_id)
        if name == obj_name:
            return obj_id
    else:
        raise ValueError(f"No object found with name '{name}'")


# Get behaviors
# Get data
# Move object
# Rotate object
# Scale object
"""
position/rotation/scale
local/global

Position: X, Y, Z
Rotation: euler, quaternion, rotation matrix | radian/angles

additional/total
"""


############
# Timeline #
############
# Set Current Frame
def set_current_frame(frame: int) -> None:
    scene.set_current_frame(frame)


# Get current Frame
def get_current_frame() -> int:
    return scene.get_current_frame()


# Set keyframe
def set_keyframe(frame_number, layer_ids=[]) -> None:
    def mod(model_editor, update_editor, scene_updater):
        layers_editor = model_editor.layers_editor()
        if not layer_ids:
            layer_ids = layer_viewer.all_layer_ids()

        for layer_id in layer_ids:
            layers_editor.set_fixed_interpolation_or_key_if_need(
                layer_id, frame_number, True
            )

    scene.modify("Set keyframe", mod)


# Delete keyframe
def delete_keyframe(frame_number, layer_ids=[]) -> None:
    def mod(model_editor, update_editor, scene_updater):
        layers_editor = model_editor.layers_editor()
        if not layer_ids:
            layer_ids = layer_viewer.all_layer_ids()

        for layer_id in layer_ids:
            layers_editor.unset_section(frame_number, layer_id)

    scene.modify("Delete keyframe", mod)


# Set interpolation
def set_interpolation(frame_number, layer_ids=[], interpolation_type="BEZIER") -> None:
    """
    BEZIER
    LOW_AMPLITUDE_BEZIER
    LINEAR
    STEP
    FIXED
    NONE
    CLAMPED_BEZIER
    """
    interpolation = getattr(csc.layers.layer.Interpolation, interpolation_type.upper())

    def mod(model_editor, update_editor, scene_updater):
        layers_editor = model_editor.layers_editor()
        if not layer_ids:
            layer_ids = layer_viewer.all_layer_ids()

        for layer_id in layer_ids:
            layers_editor.change_section(frame_number, layer_id, mod_section)

    def mod_section(section):
        section.interval.interpolation = interpolation

    scene.modify("Set interpolation", mod)


# Create layer
# Delete layer
# Select layer
# Get selected layers
# Get objects on layer
# Get layer
def get_layer_by_name(name):
    layer_ids = layer_viewer.all_layer_ids()
    for id in layer_ids:
        layer = layer_viewer.find_layer(id)
        if layer.header.name == name:
            return id
    else:
        return False

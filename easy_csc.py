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
    """
    Select an object by it's object id.

    :param csc.model.ObjectId object_id: ID of the object
    :param bool extend: Extend current selection, defaults to False
    """
    if extend:
        current_selection = get_selected_objects()
        scene.selector().select(current_selection | set(object_id))
    else:
        scene.selector().select(set(object_id))


def select_objects(object_ids: Set[csc.model.ObjectId]) -> None:
    """
    Select list of objects by their object id.

    :param Set[csc.model.ObjectId] object_ids: Set of object ids
    """
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


def get_objects_by_type(type_name: str) -> Set[csc.model.ObjectId]:
    """
    Get the list of objects with a given type. (Joint, Point, etc)

    :param str type_name: Type of desired objects
    :return set: Set of the objects with the given type
    """
    objects = model_viewer.get_objects()
    return {
        obj
        for obj in objects
        if not behaviour_viewer.get_behaviour_by_name(obj, type_name).is_null()
    }


def get_object_by_name(name: str) -> csc.model.ObjectId:
    """
    Get the first object with the exact given name. (Case sensitive)

    :param str name: Name of the object
    :raises ValueError: If no object found with the given name
    :return csc.model.ObjectId: ID of the object
    """
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
    """
    Set the playhead to the given frame.

    :param int frame: Desired frame number
    """
    scene.set_current_frame(frame)


# Get current Frame
def get_current_frame() -> int:
    """
    Get the current position of the playhead.

    :return int: Current frame number
    """
    return scene.get_current_frame()


# Set keyframe
def set_keyframe(frame_number: int, layer_ids: List[str] = []) -> None:
    """
    Set keyframe on the given frame and list of layers.
    If no layers are given all layers will be keyed.

    :param int frame_number: Frame number where the key will be set
    :param List[str] layer_ids: List of layer ids, defaults to []
    """

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
def delete_keyframe(frame_number: int, layer_ids: List[str] = []) -> None:
    """
    Delete keyframe on the given frame and list of layers.
    If no layers are given keyframes on all layers will be removed.

    :param int frame_number: Frame number where the key will be deleted
    :param List[str] layer_ids: List of layer ids, defaults to []
    """

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
def get_layer_by_name(name: str) -> csc.Guid:
    """
    Get the id of the layer with the given name.

    :param str name: Name of the layer
    :raises ValueError: Raised when no layer with the given name is found
    :return csc.Guid: ID of the layer
    """
    layers_map = scene.layers_viewer().layers_map()
    for id, layer in layers_map.items():
        if layer.header.name == name:
            return id
    raise ValueError("layer with name '" + name + "' not found")


# Move objects to layer
def move_objects_to_layer(
    obj_ids: list = None,
    layer_id: str = None,
    layer_name: str = None,
):
    """
    Move list of objects to a given layer.
    If no object is given the selected objects will be used.
    You need to give either layer_id or layer_name for the target layer.

    :param list obj_ids: List of object ids, defaults to None
    :param str layer_id: Layer ID of the target layer, defaults to None
    :param str layer_name: Name of the target layer, defaults to None
    :raises ValueError: Raised when neither layer_name or layer_id is given
    """
    if layer_id is None and layer_name is None:
        raise ValueError("Either layer_id or layer_name must be provided.")
    layer_id = get_layer_by_name(layer_name) if layer_name else layer_id

    if obj_ids is None:
        obj_ids = list(get_selected_objects())

    def move_to_layer(model_editor, updateEditor, scene):
        model_editor.move_objects_to_layer(obj_ids, layer_id)

    scene.modify("move objects to layers", move_to_layer)

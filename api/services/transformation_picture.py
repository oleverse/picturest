from typing import List

from api.schemas.transformation import TransformPictureModel


def create_list_transformation(body: TransformPictureModel) -> List[dict]:
    """
    The create_list_transformation function takes a TransformPictureModel object as input and returns a list of
    dictionaries. The dictionaries are used to create the transformation string that is passed to the image processing
    library. The function checks if each field in the TransformPictureModel object has been set, and if so, it adds an
    appropriate dictionary entry to the transform_list list.
    For example, can use the following values for the arguments:
    {'resize': {'width': 200, 'height': 400, 'background': 'pink'},
    'rotate': {'degree': 90},
    'radius': {'all': 50, 'max': True},
    'simple_effect': [{'effect': 'cartoonify', 'strength': 100}]}

    :param body: TransformPictureModel: Pass the body of the request to this function
    :return: A list of dictionaries

    """

    transform_list = []

    if body.resize:
        t_dict = body.resize.model_dump()
        transform_list.append(t_dict)

    if body.rotate:
        transform_list.append({'angle': body.rotate.degree})

    if body.radius:
        if body.radius.max:
            transform_list.append({'radius': 'max'})
        elif body.radius.all > 0:
            transform_list.append({'radius': body.radius.all})
        else:
            transform_list.append({'radius': f'{body.radius.left_top}:{body.radius.right_top}:'
                                             f'{body.radius.right_bottom}:{body.radius.left_bottom}'})

    if body.simple_effect:
        for item in body.simple_effect:
            transform_list.append(({'effect': f'{item.effect.name}:{item.strength}'}))

    return transform_list

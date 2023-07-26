from typing import List

from api.schemas_transformation import TransformPictureModel


def create_list_transformation(body: TransformPictureModel) -> List[dict]:

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




    print(transform_list, "serv_trfsform_list")
    return transform_list

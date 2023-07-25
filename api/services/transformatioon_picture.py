from typing import List

from api.schemas_transformation import TransformPictureModel


def create_list_transformation(body: TransformPictureModel) -> List[dict]:

    transform_list = []

    # if body.resize:
    #     transform_item = {}
    #     t_dict = body.resize.model_dump()
    #     for key in t_dict:
    #         if t_dict[key]:
    #             if type(t_dict[key]) not in (int, str):
    #                 transform_item[key] = t_dict[key].name
    #             else:
    #                 transform_item[key] = t_dict[key]
    #     transform_list.append(transform_item)

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

    return transform_list

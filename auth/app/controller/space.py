from app.utils.db.models.space import Spaces
from bson.objectid import ObjectId
from app.utils.api import APP_ERROR, StatusCode

def create_space(user: dict, name: str):
    user_id = user.get("id")
    existing_space = Spaces.objects(user=ObjectId(user_id), name=name).first()

    if existing_space:
        raise APP_ERROR(code="app/space/name-conflict", message="Name should be unique", status_code=StatusCode.SOMETHING_WENT_WRONG)

    space_obj = Spaces(
        name=name,
        user=ObjectId(user_id)
    )
    space = space_obj.save()
    space_data = space.to_dict()

    return space_data

def get_spaces(user: dict):
    user_id = user.get("id")

    base_query = Spaces.objects(user=ObjectId(user_id))
    total_count = base_query.count()

    spaces = base_query.order_by("-createdAt").select_related(max_depth=1)
    return [space.to_dict() for space in spaces]

def does_user_space_exist(user_id: str):
    user_space = Spaces.objects(user=ObjectId(user_id)).first()
    if user_space:
        return True
    return False
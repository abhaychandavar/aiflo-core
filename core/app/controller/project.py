from app.utils.api import APP_ERROR, StatusCode
from app.utils.db.models.project import Projects
from bson.objectid import ObjectId
from typing import Optional

def update_project(id: Optional[str], user: dict, name: str, status: str, description: str, space_id: str):
    user_id = user.get("id")

    if not id:
        raise APP_ERROR(code="flow/not-found/id", message="id required", status_code=StatusCode.BAD_REQUEST)
    
    update_fields = {}
    
    if user_id:
        update_fields["set__user"] = ObjectId(user_id)
    if name:
        update_fields["set__name"] = name
    if status:
        update_fields["set__status"] = status
    if description:
        update_fields["set__description"] = description

    res = Projects.objects(id=ObjectId(id), spaceID=space_id).modify(
        **update_fields,
        upsert=True,
        new=True
    )
    return res.to_dict()

def create_project(user: dict, name: str, status: str, description: str, space_id: str):
    user_id = user.get("id")
    
    project = Projects.objects(name=name, user=ObjectId(user_id), spaceID=space_id).first()
    if project:
        raise APP_ERROR(code="flow/not-found/project/name-conflict", message="Project name should be unique", status_code=StatusCode.BAD_REQUEST, ui_message="Project name should be unique")
    
    project = Projects(
        name=name,
        user=ObjectId(user_id),
        status=status,
        description=description,
        spaceID=space_id
    )
    res = project.save()

    return res.to_dict()

def get_projects(user: dict, space_id: str, page = 1, minimal = False):
    user_id = user.get("id")
    limit = 10
    if page < 1:
        page = 1
    skip = (page - 1) * limit
    base_query = Projects.objects(user=ObjectId(user_id), spaceID=space_id)
    total_count = base_query.count()

    if minimal:
        base_query = base_query.only("name", "status", "user", "createdAt", "updatedAt")

    projects = base_query.skip(skip).limit(limit).order_by("-createdAt").select_related(max_depth=1)
    return {
        "projects": [project.to_dict() for project in projects],
        "total": total_count,
        "page": page,
        "nextPage": page if total_count > skip + limit else None,
    }

def delete_project(user: dict, project_id: str, space_id: str):
    user_id = user.get("id")

    if not project_id:
        raise APP_ERROR(code="flow/not-found/projects/id", message="Project ID required", status_code=StatusCode.BAD_REQUEST, ui_message="Project ID required")
    
    project = Projects.objects(id=ObjectId(project_id), spaceID=space_id).first()
    if not project:
        raise APP_ERROR(code="flow/not-found/project/not-found", message="Project not found", status_code=StatusCode.BAD_REQUEST, ui_message="Unable to find the project")
    
    delete_res = Projects.objects(id=ObjectId(project_id), user=ObjectId(user_id)).delete()
    return delete_res
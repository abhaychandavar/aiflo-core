from bson import ObjectId
from app.utils.api import APP_ERROR, StatusCode
from app.utils.db.models.flow import Flows


def get_flow_by_id(flow_id: str):
    flow = Flows.objects(id=ObjectId(flow_id)).first()
    if not flow:
        raise APP_ERROR(code="flow/not-found/flow", message="Flow not found", status_code=StatusCode.BAD_REQUEST)
    flow_dict = flow.to_dict()
    return flow_dict
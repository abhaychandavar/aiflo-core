import json
import logging
from app.utils.db.models.flow import Flows
from bson.objectid import ObjectId
from typing import Optional
from app.utils.api import APP_ERROR, StatusCode
from app.services.nodeBuilder import NodeBuilder
from uuid import uuid4

async def save_flow(id: Optional[str], user: dict, flow: Optional[dict], name: str, status: str, description: str):
    user_id = user.get("_id")

    update_fields = {}

    if user:
        update_fields["set__user"] = ObjectId(user_id)
    if flow:
        update_fields["set__flow"] = flow
    if name:
        update_fields["set__name"] = name
    if status:
        update_fields["set__status"] = status
    if description:
        update_fields["set__description"] = description

    res = Flows.objects(id=ObjectId(id)).modify(
        **update_fields,
        upsert=True,
        new=True
    )
    return res.to_dict()

async def get_flow(flowID: str):
    flow_doc = Flows.objects(id=ObjectId(flowID)).first()
    if flow_doc:
        return flow_doc.to_dict()
    return None

async def get_flows(user: dict, page = 1, minimal = False):
    user_id = user.get("_id")
    logging.debug(f"Getting flows for user {user_id}")
    limit = 10
    if page < 1:
        page = 1
    skip = (page - 1) * limit
    base_query = Flows.objects(user=user_id)
    total_count = base_query.count()

    if minimal:
        base_query = base_query.only("name", "status", "user", "createdAt", "updatedAt")

    flows = base_query.skip(skip).limit(limit).order_by("-createdAt").select_related(max_depth=1)
    return {
        "flows": [flow.to_dict() for flow in flows],
        "total": total_count,
        "page": page,
        "nextPage": page if total_count > skip + limit else None,
    }

async def delete_flow(flowID: str):
    delete_res = Flows.objects(id=ObjectId(flowID)).delete()
    return delete_res

async def run_flow(flowID: str, data: dict):
    flow = Flows.objects(id=ObjectId(flowID)).first()

    if not flow:
        raise APP_ERROR(code=StatusCode.NOT_FOUND, message="Flow not found")

    nodes = data["nodes"]
    edges = data["edges"]

    node_tree_builder = NodeBuilder(nodes, edges, flowID)
    node_tree_builder.build()

    run_id = str(uuid4())

    async for val in node_tree_builder.execute():
         if not isinstance(val, dict):
            raise TypeError(f"Expected val to be a dict, got {type(val)}")
         message_id = f"{uuid4()}"
         yield f"id: {message_id}\ndata: {json.dumps({ **val, "eventID": message_id, "runID": run_id})}\n\n"

def get_node_by_id(flow_id: str, node_id: str):
    flow = Flows.objects(id=ObjectId(flow_id)).first()
    if not flow:
        raise APP_ERROR(code="flow/not-found/node", message="Flow not found", status_code=StatusCode.BAD_REQUEST)
    flow_dict = flow.to_dict()
    node = next((n for n in flow_dict.get("flow", {}).get("nodes", []) if n.get("id") == node_id), None)
    return node

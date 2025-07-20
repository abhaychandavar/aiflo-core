import json
import logging
from app.utils.db.models.flow import Flows, FlowTypeEnum
from bson.objectid import ObjectId
from typing import Optional
from app.utils.api import APP_ERROR, StatusCode
from app.services.nodeBuilder import NodeBuilder
from uuid import uuid4
from app.config.llms import SUPPORTED_LLMS
from app.config.nodes import NODES_GROUP_LAYOUT
from app.utils.db.models.project import Projects
from app.utils.flow import get_flow_by_id as get_flow_by_id_util

def create_flow(user: dict, flow: Optional[dict], name: str, status: str, description: str, project_id: str, type: str):
    user_id = user.get("id")

    project = Projects.objects(id=ObjectId(project_id), user=ObjectId(user_id)).first()
    if not project:
        raise APP_ERROR(code="flow/not-found/project", message="Project not found", status_code=StatusCode.BAD_REQUEST)
    
    flow = Flows.objects(name=name, project=ObjectId(project_id)).first()
    if flow:
        raise APP_ERROR(code="flow/not-found/flows/name-conflict", message="Flow name should be unique", status_code=StatusCode.BAD_REQUEST)

    flow_doc = Flows(
        project=ObjectId(project_id),
        name=name,
        description=description,
        flow=flow,
        status=status,
        type=type or FlowTypeEnum.LOGIC
    )
    res = flow_doc.save()

    return res.to_dict()

def update_flow(id: Optional[str], user: dict, flow: Optional[dict], name: str, status: str, description: str, project_id: str):
    user_id = user.get("id")

    project = Projects.objects(id=ObjectId(project_id), user=ObjectId(user_id)).first()
    if not project:
        raise APP_ERROR(code="flow/not-found/project", message="Project not found", status_code=StatusCode.BAD_REQUEST)
    
    update_fields = {}

    if project_id:
        update_fields["set__project"] = ObjectId(project_id)
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

async def get_flows(user: dict, project_id: str, search: str, page = 1, minimal = False):
    user_id = user.get("id")
    logging.debug(f"Getting flows for user {user_id}")
    project = Projects.objects(id=ObjectId(project_id), user=ObjectId(user_id)).first()
    if not project:
        raise APP_ERROR(code="flow/not-found/project", message="Project not found", status_code=StatusCode.BAD_REQUEST)
    
    limit = 10
    if page < 1:
        page = 1
    skip = (page - 1) * limit

    query_params = {"project": ObjectId(project_id)}
    if search:
        query_params["name__icontains"] = search

    logging.debug(f"query params {query_params}")
    
    base_query = Flows.objects(**query_params)
    total_count = base_query.count()

    if minimal:
        base_query = base_query.only("name", "status", "project", "createdAt", "updatedAt")

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

async def run_flow(flowID: str, data: dict, space_id: str):
    flow = Flows.objects(id=ObjectId(flowID)).first()

    if not flow:
        raise APP_ERROR(code=StatusCode.NOT_FOUND, message="Flow not found")

    nodes = data["nodes"]
    edges = data["edges"]

    node_tree_builder = NodeBuilder(nodes, edges, flowID, space_id=space_id)
    node_tree_builder.build()

    run_id = str(uuid4())

    async for val in node_tree_builder.execute():
         if not isinstance(val, dict):
            raise TypeError(f"Expected val to be a dict, got {type(val)}")
         message_id = f"{uuid4()}"
         yield f"id: {message_id}\ndata: {json.dumps({ **val, "eventID": message_id, "runID": run_id})}\n\n"

def get_node_by_id(flow_id: str, node_id: str, unique_node_id: str):
    flow = Flows.objects(id=ObjectId(flow_id)).first()
    if not flow:
        raise APP_ERROR(code="flow/not-found/flow", message="Flow not found", status_code=StatusCode.BAD_REQUEST)
    flow_dict = flow.to_dict()
    node = next((n for n in flow_dict.get("flow", {}).get("nodes", []) if (node_id and n.get("id") == node_id) or (unique_node_id and n.get("data", {}).get("uniqueIdentifier"))), None)
    return node

def get_flow_by_id(flow_id: str):
    flow_dict = get_flow_by_id_util(flow_id)
    return flow_dict

def get_allowed_llm_models():
    llm_objs = SUPPORTED_LLMS.get_models_dict()
    llms = {}
    for key, llm in llm_objs.items():
        llms[llm["id"]] = {
            "name": llm["name"]
        }
    return llms

def get_nodes_layout():
    return NODES_GROUP_LAYOUT
from fastapi import APIRouter, Request
from app.controller.flow import get_node_by_id
from app.utils.api import APP_ERROR, api_helpers

router = APIRouter()

@router.get("/{flowID}/nodes/{nodeID}")
async def get_config(request: Request):
    try:
        flow_id = request.path_params.get("flowID")
        node_id = request.path_params.get("nodeID")
        unique_node_id = request.query_params.get("uniqueNodeId")
        res = get_node_by_id(flow_id=flow_id, node_id=node_id, unique_node_id=unique_node_id)
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(None, e)
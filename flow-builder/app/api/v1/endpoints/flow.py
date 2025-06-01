from fastapi import APIRouter
from fastapi import APIRouter
from fastapi import Request
from app.controller.flow import save_flow, get_flow, get_flows, delete_flow, run_flow, save_knowledge_base, get_node_by_id
from app.utils.api import api_helpers 
from app.utils.api import APP_ERROR
from fastapi.responses import StreamingResponse
router = APIRouter()

@router.post("")
async def save(request: Request):
    try:
        user = request.state.user
        body = await request.json()
        res = await save_flow(body.get("id"), user, body.get("flow"), body.get("name"), body.get("status"), body.get("description"));
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)

@router.get("/{flowID}")
async def get(request: Request):
    try:
        flowID = request.path_params.get("flowID");
        res = await get_flow(flowID);
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(None, e)

@router.get("")
async def get_all_flows(request: Request):
    try:
        user = request.state.user
        res = await get_flows(user, int(request.query_params.get("page", 1) or 1), request.query_params.get("minimal") == "true");
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(None, e)
    
@router.delete("/{flowID}")
async def delete(request: Request):
    try:
        flowID = request.path_params.get("flowID")
        res = await delete_flow(flowID)
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(None, e)
    
@router.post("/{flowID}/run")
async def run(request: Request):
    try:
        flowID = request.path_params.get("flowID")
        body = await request.json()
        return StreamingResponse(run_flow(flowID, body), media_type="text/event-stream")
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(None, e)

@router.post("/{flowID}/nodes/{nodeId}/knowledge-base")
async def get_all_configs_for_flow_id(request: Request):
    try:
        flow_id = request.path_params.get("flowID")
        node_id = request.path_params.get("nodeId")
        body = await request.json()
        path = body.get("path")
        res = await save_knowledge_base(flow_id, node_id, path)
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(None, e)
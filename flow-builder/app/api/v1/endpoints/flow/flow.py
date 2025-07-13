from fastapi import APIRouter, Request
from app.controller.flow import create_flow, update_flow, get_flow, get_flows, delete_flow, run_flow, get_allowed_llm_models, get_nodes_layout
from app.utils.api import api_helpers 
from app.utils.api import APP_ERROR
from fastapi.responses import StreamingResponse

flow_router = APIRouter()

@flow_router.post("")
async def create_flow_router(request: Request):
    try:
        user = request.state.user
        project_id = request.path_params.get("project_id")
        body = await request.json()
        res = create_flow(user, body.get("flow"), body.get("name"), body.get("status"), body.get("description"), project_id, body.get("type"));
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)
    
@flow_router.patch("")
async def update_flow_router(request: Request):
    try:
        user = request.state.user
        project_id = request.path_params.get("project_id")
        body = await request.json()
        res = update_flow(body.get("id"), user, body.get("flow"), body.get("name"), body.get("status"), body.get("description"), project_id);
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)

@flow_router.get("/nodes/layout")
async def get_nodes_layout_route(request: Request):
    try:
        res = get_nodes_layout();
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)
    
@flow_router.get("/{flow_id}")
async def get(request: Request):
    try:
        flow_id = request.path_params.get("flow_id");
        res = await get_flow(flow_id)
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(None, e)

@flow_router.get("")
async def get_all_flows(request: Request):
    try:
        user = request.state.user
        res = await get_flows(user, request.path_params.get("project_id"), int(request.query_params.get("page", 1) or 1), request.query_params.get("minimal") == "true");
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(None, e)
    
@flow_router.delete("/{flow_id}")
async def delete(request: Request):
    try:
        flow_id = request.path_params.get("flow_id")
        res = await delete_flow(flow_id)
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(None, e)
    
@flow_router.get("/llms/models")
async def get_allowed_llm_models_req(request: Request):
    try:
        res = get_allowed_llm_models()
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(None, e)
    
@flow_router.post("/{flow_id}/run")
async def run(request: Request):
    try:
        flow_id = request.path_params.get("flow_id")
        space_id = request.path_params.get("space_id")
        body = await request.json()
        return StreamingResponse(run_flow(flow_id, body, space_id), media_type="text/event-stream")
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(None, e)
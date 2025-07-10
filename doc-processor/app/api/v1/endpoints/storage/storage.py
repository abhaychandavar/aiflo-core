from fastapi import APIRouter
from fastapi import Request
from app.controller.storage import (
    generate_sequential_upload_signed_urls, 
    complete_upload, 
    get_files,
    get_file_ref_id
)
from app.utils.api import api_helpers 
from app.utils.api import APP_ERROR

router = APIRouter()

@router.post("/spaces/{space_id}/generate/sequential/signed-urls")
async def generate_sequential_upload_signed_urls_route(request: Request):
    try:
        space_id = request.path_params.get("space_id")
        body = await request.json();
        res = await generate_sequential_upload_signed_urls(
            count=body.get("count"),
            file_name=body.get("fileName"),
            space_id=space_id
        );
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)

@router.post("/spaces/{space_id}/complete-upload")
async def complete_upload_route(request: Request):
    try:
        space_id = request.path_params.get("space_id")
        body = await request.json();
        res = await complete_upload(
            space_id=space_id,
            file_name=body.get("fileName")
        );
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)
    
@router.get("/spaces/{space_id}/files")
async def get_files_route(request: Request):
    try:
        space_id = request.path_params.get("space_id")
        res = await get_files(
            space_id=space_id
        );
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)
    
@router.post("/spaces/{space_id}/files/ref-id")
async def get_file_ref_id_route(request: Request):
    try:
        space_id = request.path_params.get("space_id")
        body = await request.json();
        res = get_file_ref_id(
            file_name=body.get("fileName"),
            space_id=space_id
        );
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)
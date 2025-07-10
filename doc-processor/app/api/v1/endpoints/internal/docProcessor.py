from fastapi import APIRouter
from fastapi import Request
from app.controller.docProcessor import index_doc, handle_event
from app.utils.api import api_helpers 
from app.utils.api import APP_ERROR

router = APIRouter()

@router.post("/index")
async def index(request: Request):
    try:
        body = await request.json();
        file_path = body.get("filePath")
        mode = body.get("mode")
        max_characters = body.get("maxCharacters")
        res = await index_doc(doc_path=file_path, mode=mode, max_characters=max_characters, metadata=body.get("metadata"));
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)

@router.post("/event")
async def handle_event_request(request: Request):
    try:
        body = await request.json();
        res = await handle_event(body);
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)
from typing import Union, List, Dict, Optional
from fastapi import HTTPException
import logging

Primitive = Union[str, int, float, bool]
ValueType = Union[Primitive, List[Primitive], "DICT"]
DICT = Dict[str, Union[Primitive, List[Primitive], "DICT"]]

class StatusCode():
    BAD_REQUEST=400
    NOT_FOUND=404
    UNAUTHORIZED=401
    NOT_ALLOWED=403
    SOMETHING_WENT_WRONG=500

class APP_ERROR(Exception):
    def __init__(self, *args, code: str, status_code: StatusCode, message: str, ui_message: str = None):
        self.code = code
        self.status_code = status_code
        self.message = message
        self.ui_message = ui_message
        
        super().__init__(*args)

class API_HELPERS:
    @staticmethod
    def response_handler(data: Optional[DICT], error: Optional[APP_ERROR | Exception] = None):
        if error:
            logging.error(f"Error occurred while processing request: {str(error)}")
            if isinstance(error, APP_ERROR):
                raise HTTPException(
                    status_code=error.status_code, 
                    detail={
                        "code": error.code,
                        "data": data if data else {},
                        "message": error.message,
                        "uiMessage": error.ui_message
                    }
                )
            raise HTTPException(
                    status_code=StatusCode.SOMETHING_WENT_WRONG, 
                    detail={
                        "code": "app/something-went-wrong",
                        "data": data if data else {},
                        "message": "Something went wrong"
                    }
                )
        return data

api_helpers = API_HELPERS()
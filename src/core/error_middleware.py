from fastapi import Request, status
from fastapi.responses import JSONResponse
from error import (Missing,Duplicate,FileTooLarge,FileConfigError,InvalidFileName,InvalidJSONError,ServerError)

async def error_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Missing as erro:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "Missing", "detail": erro.msg})
    except Duplicate as erro:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": "Duplicate", "detail": erro.msg})
    except FileTooLarge as erro:
        return JSONResponse(status_code=status.HTTP_413_CONTENT_TOO_LARGE, content={"error": "FileTooLarge", "detail": erro.msg})
    except FileConfigError as erro:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "FileConfigError", "detail": erro.msg})
    except InvalidFileName as erro:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "InvalidFileName", "detail": erro.msg})
    except InvalidJSONError as erro:
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"error": "InvalidJSONError", "detail": erro.msg})
    except ServerError as erro:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "ServerError", "detail": erro.msg})
    
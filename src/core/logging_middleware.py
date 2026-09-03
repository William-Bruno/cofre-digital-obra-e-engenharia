import logging
from fastapi import Request

logger = logging.getLogger("cofre_digital")

async def logging_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        mensagem = (f"{request.method} {request.url.path} status={response.status_code}")

        if response.status_code >= 500:
            logger.error(mensagem)
        elif response.status_code >= 400:
            logger.warning(mensagem)
        else:
            logger.info(mensagem)

        return response
    except Exception as error:
        logger.error(f"{request.method} {request.url.path} erro interno: {error}")
        raise
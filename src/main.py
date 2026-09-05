from fastapi import FastAPI
from core.logging_config import logger
from core.logging_middleware import logging_middleware
from routes import document

app = FastAPI()

app.middleware("http")(logging_middleware)
app.include_router(document.router, tags=["Documentos"])

logger.info("API de Obras e Engenharia funcionando!")








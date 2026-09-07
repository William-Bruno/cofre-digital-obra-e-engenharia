from fastapi import FastAPI
from core.logging_config import logger
from core.logging_middleware import logging_middleware
from core.error_middleware import error_middleware
from routes import document, backup

app = FastAPI()

app.middleware("http")(logging_middleware)
app.middleware("http")(error_middleware)
app.include_router(document.router, tags=["Documentos"])
app.include_router(backup.router, tags=["Backups"])

logger.info("API de Obras e Engenharia funcionando!")








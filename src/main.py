from fastapi import FastAPI
from web import document

app = FastAPI()

app.include_router(document.router, tags=["Documentos"])







from typing import Annotated
from fastapi import APIRouter, UploadFile, status, File, Depends
from fastapi.responses import FileResponse
from model.document import Documents, DocumentCreate, DocumentUpdate, DocumentFilter, Statistics, Integridade
from service.document import (create_document, update_document, delete_document, download_document, export_document_csv, get_document_id, filter_document, statistics_document, verificar_integridade)


router = APIRouter(prefix= "/documents")

@router.post("", status_code=status.HTTP_201_CREATED, response_model=Documents)
async def post_documents(document: Annotated[DocumentCreate, Depends(DocumentCreate.as_form)], arquivo: UploadFile | None = File(None),):
    return await create_document(document, arquivo)

@router.get("", status_code=status.HTTP_200_OK, response_model=list[Documents])
def get_documents(categoria:str | None = None, obra:str | None = None, etapa:str|None=None,):
        filters = DocumentFilter(categoria=categoria, obra=obra,etapa=etapa)
        return filter_document(filters)

@router.get("/statistics", status_code=status.HTTP_200_OK, response_model=Statistics)
def statistics_documents():
     return statistics_document()

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Documents)
def get_documents_id(id: int):
    return get_document_id(id)

@router.patch("/{id}", status_code=status.HTTP_200_OK, response_model=Documents)
async def update_documents(id: int, document: Annotated[DocumentUpdate, Depends(DocumentUpdate.as_form)], arquivo: UploadFile | None = File(None),):
    return await update_document(id, document, arquivo)

@router.delete("/{id}", status_code=status.HTTP_200_OK, response_model=Documents)
def delete_documents(id:int):
    return delete_document(id)

@router.get("/{id}/download", status_code=status.HTTP_200_OK)
def download_documents(id: int) -> FileResponse:
    return download_document(id)

@router.get("/{id}/integridade", status_code=status.HTTP_200_OK, response_model=Integridade)
def verificar_document(id: int) -> Integridade:
     return verificar_integridade(id)

@router.get("/export/csv", status_code=status.HTTP_200_OK)
def export_documents():
    return export_document_csv()



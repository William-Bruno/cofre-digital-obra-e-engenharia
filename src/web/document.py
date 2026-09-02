from typing import Annotated
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from model.document import Documents, DocumentCreate, DocumentUpdate
from service.document import (create_document, update_document, delete_document, download_document, export_document_csv)
from data.document import read_documents

router = APIRouter(prefix= "/documents")

@router.get("")
@router.get("/", status_code=200, response_model=list[Documents])
def get_documents():
    return read_documents()

@router.get("/{id}", status_code=200, response_model=Documents)
def get_document_id(id: int):
    documents = read_documents()
    for document in documents:
        if document.get("id") == id:
            return document
    raise HTTPException(status_code=404, detail="Documento não foi encontrado, verifique!")

@router.get("/{id}/download", status_code=200)
def download_documents(id: int) -> FileResponse:
    return download_document(id)

@router.post("")  
@router.post("/", status_code=201, response_model=Documents)
async def post_documents(document: Annotated[DocumentCreate, Depends(DocumentCreate.as_form)], arquivo: UploadFile | None = File(None),):
    return await create_document(document, arquivo)
    
@router.put("/{id}", status_code=200, response_model=Documents)
async def update_documents(id: int, document: Annotated[DocumentUpdate, Depends(DocumentUpdate.as_form)], arquivo: UploadFile | None = File(None),):
    return await update_document(id, document, arquivo)
    
@router.delete("/{id}", status_code=200, response_model=Documents)
def delete_documents(id:int):
    return delete_document(id)

@router.get("/export/csv", status_code=200)
def export_documents():
    return export_document_csv()


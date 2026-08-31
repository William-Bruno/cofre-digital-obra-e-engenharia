from typing import Annotated
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
import json
import csv
import mimetypes
import hashlib
from datetime import datetime
from pathlib import Path

from model.documents import Documents, DocumentCreate, DocumentUpdate


BD_PATH = Path("storage/metadados/documents.json")
EXPORT_PATH = Path("storage/exports/documents.csv")
FILES_PATH = Path("storage/files")


app = FastAPI()


def read_documents() -> list[dict]:
    BD_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not BD_PATH.exists():
        with open(BD_PATH, "w", encoding="utf-8") as file:
            json.dump([], file, indent=2, ensure_ascii=False)

    try:
        with open(BD_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:    
        return []

def write_documents(document: list[dict]):
    BD_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(BD_PATH, "w", encoding="utf-8") as file:
        json.dump(document, file, indent=2, ensure_ascii=False)

def get_id(documents: list[dict]) -> int:
    if not documents:
        return 1
    ids = [document["id"] for document in documents if document.get("id") is not None]
    if not ids:
        return 1
    return max(ids) + 1

def calculate_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()

async def save_documents(arquivo: UploadFile, document_id: int,) -> dict:

    if not arquivo.filename:
        raise HTTPException(status_code=400, detail="Arquivo sem nome")

    FILES_PATH.mkdir(parents=True, exist_ok=True)
    nome_original = Path(arquivo.filename).name
    extensao = Path(nome_original).suffix.lower().replace(".", "")
    mime_type = arquivo.content_type
    if not mime_type:
        mime_type, _ = mimetypes.guess_type(nome_original)
    mime_type = mime_type or "application/octet-stream"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    nome_armazenado = f"{document_id}_{timestamp}_{nome_original}"
    arquivo_local = FILES_PATH / nome_armazenado
    
    with open(arquivo_local, "wb") as destino:
        while chunk := await arquivo.read(1024 * 1024):
            destino.write(chunk)

    tamanho = arquivo_local.stat().st_size
    sha256 = calculate_sha256(arquivo_local)

    return{
        "nome_original": nome_original,
        "nome_armazenado": nome_armazenado,
        "extensao": extensao,
        "tipo_mime": mime_type,
        "tamanho": tamanho,
        "sha256": sha256,
    }

@app.get("/documents", response_model=list[Documents])
def get_documents():
    return read_documents()

@app.get("/documents/{id}", response_model=Documents)
def get_document_id(id: int):
    documents = read_documents()
    for document in documents:
        if document.get("id") == id:
            return document
    raise HTTPException(status_code=404, detail="Documento não foi encontrado, verifique!")

@app.get("/documents/{id}/download")
def download_cdocument(id: int):
    documents = read_documents()

    for document in documents:
        if document.get("id") == id:
            nome_arquivo = document.get("nome_armazenado")
            if not nome_arquivo:
                raise HTTPException(status_code=404, detail="Nome do arquivo não encontrado no storage")
            arquivo_local = FILES_PATH / nome_arquivo
            if not arquivo_local.exists():
                raise HTTPException(status_code=404, detail="Arquivo fisico não encontrado no storage")
            return FileResponse(
                path=arquivo_local, 
                filename=document.get("nome_original", nome_arquivo),
                media_type=document.get("tipo_mime", "application/octet-stream"),)
    raise HTTPException(status_code=404, detail="Documento não encontrado")

@app.post("/documents", response_model=Documents)
async def post_documents(
    document: Annotated[DocumentCreate, Depends(DocumentCreate.as_form)],         
    arquivo: UploadFile | None = File(None),
):
    documents = read_documents()
    document_id = get_id(documents)

    new_document = Documents(
        id=document_id,
        **document.model_dump(),
        data_upload=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    )

    if arquivo is not None:
        file_data = await save_documents(arquivo=arquivo, document_id=document_id)
        new_document = new_document.model_copy(
            update=file_data
        )
    documents.append(new_document.model_dump())
    write_documents(documents)

    return new_document

@app.put("/documents/{id}", response_model=Documents)
async def update_document(
    id: int,
    document: Annotated[DocumentUpdate, Depends(DocumentUpdate.as_form)],
    arquivo: UploadFile | None = File(None),
):
    documents = read_documents()
    for indice, document_update in enumerate(documents):
        if document_update.get("id") != id:
            continue
        updates = document.model_dump(exclude_unset=True)

        for field, value in updates.items():
            if value is not None:
                document_update[field] = value

        if arquivo is not None:
            nome_arquivo_antigo = document_update.get("nome_armazenado")
            file_data = await save_documents(arquivo=arquivo, document_id=id,)

            document_update(file_data)

            if nome_arquivo_antigo:
                arquivo_antigo = (FILES_PATH / nome_arquivo_antigo)
                if arquivo_antigo.exists():
                    arquivo_antigo.unlink()

        documents[indice] = document_update
        write_documents(documents)
        return Documents(**document_update)
    raise HTTPException(status_code=404, detail="Documento não foi encontrado."
    )

@app.delete("/documents/{id}", response_model=Documents)
def delete_documents(id:int):
    documents = read_documents()
    for indice, document in enumerate(documents):
        if document.get("id") != id:
            continue
        deleted_document = documents.pop(indice)    
        write_documents(documents)
        nome_armazenado = deleted_document.get("nome_armazenado")
        if nome_armazenado:
            arquivo_local = FILES_PATH / nome_armazenado
            if arquivo_local.exists():
                arquivo_local.unlink()
        return deleted_document
    raise HTTPException(status_code=404, detail="Documento não encontrado!")

@app.get("/documents/export/csv")
def export_document_csv():
    documents = read_documents()

    if not documents:
        raise HTTPException(status_code=404, detail="Nenhum documento foi encontrado")

    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    cabecalhos = list(Documents.model_fields.keys())
    with open(EXPORT_PATH, "w", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=cabecalhos)
        writer.writeheader()
        writer.writerows(documents)

    return {"message": "Exportação realizada com sucesso!",
            "arquivo": EXPORT_PATH}

from pathlib import Path
from datetime import datetime
import mimetypes
import hashlib
from fastapi import HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from core.config_loader import config
from data.document import read_documents, write_documents, export_document
from model.document import Documents, DocumentCreate, DocumentUpdate, DocumentFilter, Statistics, Integridade, IntegridadeGeral


FILES_PATH = Path(config["paths"]["files_path"])

CHUNK_SIZE = config["settings"]["upload"]["chunk_size"]
TIMESTAMP_FORMAT = config["settings"]["document"]["timestamp_format"]
UPLOAD_DATE_FORMATE = config["settings"]["document"]["upload_date_format"]
MAX_UPLOAD_SIZE = config["settings"]["upload"]["max_upload_size"]

ALGORITHM_TYPE = config["settings"]["hash"]["algorithm"]


def calculate_hash(file_path: Path) -> str:
    hash_agorithm = hashlib.new(ALGORITHM_TYPE)
    try:
        with open(file_path, "rb") as arquivo:
            while chunk := arquivo.read(CHUNK_SIZE):
                hash_agorithm.update(chunk)
        return hash_agorithm.hexdigest()
    except(OSError, IOError) as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Problema ao calcular o hash {error}")



async def save_documents(arquivo: UploadFile, document_id: int,) -> dict:

    if not arquivo.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo não possui nome")

    FILES_PATH.mkdir(parents=True, exist_ok=True)
    nome_original = Path(arquivo.filename).name
    extensao = Path(nome_original).suffix.lower().replace(".", "")
    mime_type = arquivo.content_type or mimetypes.guess_type(nome_original)[0] or "application/octet-stream"
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    nome_armazenado = f"{document_id}_{timestamp}_{nome_original}"
    arquivo_local = FILES_PATH / nome_armazenado

    tamanho_arquivo = 0
    try:
        with open(arquivo_local, "wb") as destino:
            while chunk := await arquivo.read(CHUNK_SIZE):
                tamanho_arquivo += len(chunk)
                if tamanho_arquivo > MAX_UPLOAD_SIZE:
                    raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail="Arquivo enviado é muito grande: MAX 10Mb")
                destino.write(chunk)
    except HTTPException:
        arquivo_local.unlink(missing_ok=True)
        raise
    sha256 = calculate_hash(arquivo_local)

    return{
        "nome_original": nome_original,
        "nome_armazenado": nome_armazenado,
        "extensao": extensao,
        "tipo_mime": mime_type,
        "tamanho": tamanho_arquivo,
        "sha256": sha256,
    }

async def create_document(document: DocumentCreate, arquivo: UploadFile | None = None) -> Documents:
    documents = read_documents()
    document_id = max([doc["id"] for doc in documents], default=0) + 1

    new_document = Documents(
        id=document_id,
        **document.model_dump(),
        data_upload=datetime.now().strftime(UPLOAD_DATE_FORMATE),
    )

    if arquivo is not None:
        file_data = await save_documents(arquivo=arquivo, document_id=document_id)
        new_document = new_document.model_copy(update=file_data)
    documents.append(new_document.model_dump())
    write_documents(documents)
    return new_document

async def update_document(id: int, document:DocumentUpdate, arquivo: UploadFile | None = None) -> Documents:
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
            document_update.update(file_data)

            if nome_arquivo_antigo:
                arquivo_antigo = (FILES_PATH / nome_arquivo_antigo)
                if arquivo_antigo.exists():
                    arquivo_antigo.unlink()

        documents[indice] = document_update
        write_documents(documents)
        return Documents(**document_update)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documento com identificador {id} não foi encontrado.")

def delete_document(id: int) -> Documents:
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
        return Documents(**deleted_document)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado!")

def get_document_id(id: int) -> Documents:
    documents = read_documents()
    for document in documents:
        if document.get("id") == id:
            return Documents(**document)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não foi encontrado, verifique!")

def download_document(id: int) -> FileResponse:
    documents = read_documents()
    
    for document in documents:
        if document.get("id") == id:
            nome_arquivo = document.get("nome_armazenado")
            if not nome_arquivo:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nome do arquivo não encontrado no storage")
            arquivo_local = FILES_PATH / nome_arquivo
            if not arquivo_local.exists():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo fisico não encontrado no storage")
            return FileResponse(
                path=arquivo_local, 
                filename=document.get("nome_original", nome_arquivo),
                media_type=document.get("tipo_mime", "application/octet-stream"),)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")

def filter_document(filters: DocumentFilter) -> list[Documents]:
    documents = read_documents()

    resultado = []

    for document in documents:
        if filters.categoria is not None:
            if document.get("categoria").strip().lower() != filters.categoria.strip().lower():
                continue
        if filters.obra is not None:
            if document.get("obra").strip().lower() != filters.obra.strip().lower():
                continue
        if filters.etapa is not None:
            if document.get("etapa").strip().lower() != filters.etapa.strip().lower():
                continue
        resultado.append(Documents(**document))
    return resultado

def export_document_csv() -> dict:
    documents = read_documents()
    export_path = export_document(documents)
    return {
        "message": "Exportação realizaca com sucesso!",
        "arquivo": str(export_path)
    }

def statistics_document() -> Statistics:
    documents = read_documents()

    total_documents = len(documents)
    espaco_total_bytes = 0
    por_extensao = {}
    por_categoria = {}
    por_etapa = {}
    por_responsavel_tecnico = {}


    for document in documents:
        espaco_total_bytes += document["tamanho"]
        extensao = document["extensao"]
        por_extensao[extensao] = por_extensao.get(extensao,0) + 1
        categoria = document["categoria"]
        por_categoria[categoria] = por_categoria.get(categoria, 0) + 1
        etapa = document["etapa"]
        por_etapa[etapa] = por_etapa.get(etapa, 0) + 1
        responsavel_tecnico = document["responsavel_tecnico"]
        por_responsavel_tecnico[responsavel_tecnico] = por_responsavel_tecnico.get(responsavel_tecnico, 0) + 1

    estatisticas = {
        "total_documents" : total_documents,
        "espaco_total_bytes" : espaco_total_bytes,
        "por_extensao" : por_extensao,
        "por_categoria": por_categoria,
        "por_etapa": por_etapa,
        "por_responsavel_tecnico": por_responsavel_tecnico
    }

    return Statistics(**estatisticas)

def verificar_integridade(id: int) -> Integridade:
    document = get_document_id(id)
    nome_armazenado = document.nome_armazenado
    arquivo_local = FILES_PATH / nome_armazenado
    hash_original = document.sha256
    hash_atual = calculate_hash(arquivo_local)
    integro = hash_original == hash_atual

    return Integridade(
        id = document.id,
        nome = document.nome_original,
        hash_original = hash_original,
        hash_atual = hash_atual,
        integro = integro
)

def verificar_integridade_geral() -> IntegridadeGeral:
    documents = read_documents()
    verificados = 0
    integros = 0
    alterados = 0
    arquivos_nao_localizados = 0

    for document in documents:
        verificados += 1
        arquivo_local = FILES_PATH / document['nome_armazenado']
        if not arquivo_local.exists():
            arquivos_nao_localizados += 1
            continue
        hash_atual = calculate_hash(arquivo_local)
        if hash_atual == document['sha256']:
            integros += 1
        else:
            alterados += 1

    return IntegridadeGeral(
        documentos_verificados=verificados,
        documentos_integros=integros,
        documentos_alterados=alterados,
        arquivos_nao_localizados=arquivos_nao_localizados
    )




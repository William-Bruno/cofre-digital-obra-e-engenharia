from pathlib import Path
import json
import csv
import datetime
import zipfile
import hashlib
from core.logging_config import config
from model.document import Documents
from error import InvalidJSONError, Missing, FileConfigError, ServerError

BD_PATH = Path(config["paths"]["bd_path"])
EXPORT_PATH = Path(config["paths"]["export_path"])
BACKUP_PATH = Path(config["paths"]["backup_path"])
FILES_PATH = Path(config["paths"]["files_path"])
STORAGE_PATH = Path(config["paths"]["storage_path"])


def read_documents() -> list[dict]:
    BD_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not BD_PATH.exists():
        with open(BD_PATH, "w", encoding="utf-8") as file:
            json.dump([], file, indent=2, ensure_ascii=False)
    try:
        with open(BD_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as erro:
        raise InvalidJSONError(f"Erro ao ler arquivo JSON, arquivo corrompido: {erro}")

def write_documents(document: list[dict]):
    BD_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(BD_PATH, "w", encoding="utf-8") as file:
            json.dump(document, file, indent=2, ensure_ascii=False)
    except(OSError, IOError) as erro:
        raise FileConfigError(f"Problema ao escrever no arquivo {erro}")

def export_document(documents: list[dict]) -> Path:
    if not documents:
        raise Missing("Nenhum documento foi encontrado")
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cabecalhos = list(Documents.model_fields.keys())
    try:
        with open(EXPORT_PATH, "w", newline="", encoding="utf-8") as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=cabecalhos)
            writer.writeheader()
            writer.writerows(documents)
        return EXPORT_PATH.as_posix()
    except(OSError, IOError) as erro:
        raise FileConfigError(f"Problema ao exportar aquivo CSV: {erro}")


def create_backup() -> Path:
    BACKUP_PATH.mkdir(parents=True, exist_ok=True)

    date_format = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    file_backup = BACKUP_PATH / f"BACKUP_{date_format}.zip"

    try:
        with zipfile.ZipFile(file_backup, "w", compression=zipfile.ZIP_DEFLATED) as zip:
            for pasta in STORAGE_PATH.iterdir():
                if pasta.name == "backups":
                    continue
                if pasta.is_dir():
                    for arquivo in pasta.rglob("*"):
                        zip.write(arquivo, arcname=arquivo.relative_to(STORAGE_PATH))
                else:
                    zip.write(pasta, arcname=pasta.name)
        return {
            "message" : "Bakup realizado com sucesso",
            "arquivo" : str(file_backup.as_posix())
        }
    except (OSError, IOError) as erro:
        raise FileConfigError(f"Falha ao criar o backup: {erro}")




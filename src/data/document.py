from pathlib import Path
import json
import csv
from fastapi import HTTPException
from data.config_loader import config
from model.document import Documents

BD_PATH = Path(config["paths"]["bd_path"])
EXPORT_PATH = Path(config["paths"]["export_path"])


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

    try:
        with open(BD_PATH, "w", encoding="utf-8") as file:
            json.dump(document, file, indent=2, ensure_ascii=False)
    except(OSError, IOError) as error:
        raise HTTPException(status_code=500, detail=f"Problema ao escrever no arquivo {error}")

def export_document(documents: list[dict]) -> Path:
    if not documents:
        raise HTTPException(status_code=404, detail="Nenhum documento foi encontrado")

    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    cabecalhos = list(Documents.model_fields.keys())
    with open(EXPORT_PATH, "w", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=cabecalhos)
        writer.writeheader()
        writer.writerows(documents)

    return EXPORT_PATH



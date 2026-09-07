from pathlib import Path
import zipfile
import datetime
from core.logging_config import config
from error import FileConfigError

BACKUP_PATH = Path(config["paths"]["backup_path"])
STORAGE_PATH = Path(config["paths"]["storage_path"])

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


def listar_backup() -> list[dict]:
    backups = []
    for arquivo in BACKUP_PATH.glob("*.zip"):
        backups.append({
            "arquivo" : arquivo.name,
            "tamanho" : arquivo.stat().st_size
        })
    return backups

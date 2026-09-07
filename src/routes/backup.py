from fastapi import APIRouter, status
from service.backup import gerar_backup, listar_backups

router = APIRouter(prefix="/backup")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_backups():
     return gerar_backup()

@router.get("", status_code=status.HTTP_200_OK)
def list_backups():
     return listar_backups()
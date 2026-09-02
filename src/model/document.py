from typing import Annotated
from fastapi import Form
from pydantic import BaseModel

class DocumentCreate(BaseModel):
    categoria: str
    descricao: str

    # ESPECIFICOS
    obra: str
    etapa: str
    responsavel_tecnico:str
    versao: float
    data: str

    @classmethod
    def as_form(
        cls,
        categoria: Annotated[str, Form()],
        descricao: Annotated[str, Form()],
    
        # ESPECIFICOS
        obra: Annotated[str, Form()],
        etapa: Annotated[str, Form()],
        responsavel_tecnico: Annotated[str, Form()],
        versao: Annotated[float, Form()],
        data: Annotated[str, Form()],
    ):
        return cls(
            categoria=categoria,
            descricao=descricao,
            obra=obra,
            etapa=etapa,
            responsavel_tecnico=responsavel_tecnico,
            versao=versao,
            data=data,
        )

class Documents(DocumentCreate):
    # GERAIS
    id: int | None = None

    nome_original: str = ""
    nome_armazenado: str = ""
    extensao: str = ""
    tipo_mime: str = ""
    tamanho: int = 0
    sha256: str = ""
    
    data_upload: str = ""

class DocumentUpdate(BaseModel):
    categoria: str | None = None
    descricao: str | None = None

    # ESPECIFICOS
    obra: str | None = None
    etapa: str | None = None
    responsavel_tecnico:str | None = None
    versao: float | None = None
    data: str | None = None    

    @classmethod
    def as_form(
        cls,
        categoria: Annotated[str | None, Form()] = None,
        descricao: Annotated[str | None, Form()] = None,
    
        # ESPECIFICOS
        obra: Annotated[str | None, Form()] = None,
        etapa: Annotated[str | None, Form()] = None,
        responsavel_tecnico: Annotated[str | None, Form()] = None,
        versao: Annotated[float | None, Form()] = None,
        data: Annotated[str | None, Form()] = None,
    ):
        return cls(
            categoria=categoria,
            descricao=descricao,
            obra=obra,
            etapa=etapa,
            responsavel_tecnico=responsavel_tecnico,
            versao=versao,
            data=data,
        )


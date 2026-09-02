# Cofre Digita de Obras e Engenharia

API desenvolvida em FastAPI

## Estrutura
    src/
    ├── data/          # Persistência (JSON, CSV)
    ├── model/         # Pydantic
    ├── service/       # Lógica
    ├── web/           # Rotas FastAPI
    └── main.py        # Ponto de entrada da aplicação

## Instalação
    Clone o repositório e instale as dependências
    Criar uma venv
    Ativar .\venv\Scripts\activate
    Install FastAPI


## Executando a aplicação
    $env:PYTHONPATH="src" 
    uvicorn main:app --port 3000 --reload

    API
    localhost:3000
    Swagger UI
    localhost:3000/docs

## Rotas
    GET /documents → Lista todos os documentos
    GET /documents/{id} → Busca o documento pelo ID
    POST /documents → Cria um novo documento
    PUT /documents/{id} → Atualiza um documento existente
    DELETE /documents/{id} → Remove um documento
    GET /documents/{id}/download → Baixa arquivo associado ao ID informado
    GET /documents/export/csv → Exporta todos os documentos de JSON para CSV

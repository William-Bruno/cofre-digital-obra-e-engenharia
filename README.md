# Cofre Digital de Documentos de Obras e Engenharia

API desenvolvida em FastAPI

## Estrutura
    src/
    ├── config/        # Configurações Gerais
    ├── core/          # Controle de Logging
    ├── data/          # Persistência (JSON, CSV)
    ├── model/         # Pydantic
    ├── routes/        # Rotas dos documentos
    ├── storage/       # Destino de arquivos físicos gerais
    ├── service/       # Lógica do negócio
    └── main.py        # Ponto de entrada da aplicação

## Instalação
    Clone o repositório e instale as dependências
    Install Python FastAPI Uvicorn PyYaml


## Executando a aplicação
    $env:PYTHONPATH="src" 
    uvicorn main:app --port 3000 --reload

    API
    localhost:3000
    Swagger UI
    localhost:3000/docs

## Rotas
    GET /documents → Lista todos os documentos com filtros específicos
    GET /documents/{id} → Busca o documento pelo ID
    POST /documents → Cria um novo documento
    PATCH /documents/{id} → Atualiza um documento existente
    DELETE /documents/{id} → Remove um documento
    GET /documents/{id}/download → Baixa arquivo associado ao ID informado
    GET /documents/export/csv → Exporta todos os documentos de JSON para CSV
    GET /documents/{id}/integridade → Verificar a integridade do documento
    GET /documents/integridade → Verificar a integridade geral de todos os dados
    GET /documents/statistics → Estatísticas de dados em persistência

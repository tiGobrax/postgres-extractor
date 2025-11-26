# Postgres Extractor

Serviço FastAPI para extrair uma tabela do PostgreSQL e salvar em Parquet utilizando Polars.

Principais endpoints
- POST /extract  -> { "table": "nome_da_tabela" }

Como usar

1. Crie um virtual env e instale dependências:

```bash
python -m venv .venv
source .venv/bin/activate  # no WSL
pip install -r requirements.txt
```

2. Copie `.env.example` para `.env` e configure apenas as credenciais de conexão com o Postgres.

3. Rode o serviço:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

4. Exemplo de requisição:

```json
POST /extract
{ "table": "public.my_table" }
```

Exemplo real (WSL/PowerShell):

```bash
curl -X POST http://localhost:8000/extract \
     -H "Content-Type: application/json" \
     -d '{"table": "public.customers"}'
```

Resposta:

```json
{
  "path": "data/public_customers_1715623456.parquet",
  "rows": 1234
}
```

O arquivo Parquet será salvo em `./data` com um timestamp.

Observações
- Este é um MVP: atualmente carrega a tabela em memória antes de gravar o parquet. Para tabelas grandes, recomenda-se adicionar paginação/batch streaming.

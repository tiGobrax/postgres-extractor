# Postgres Extractor

Servico FastAPI que extrai uma tabela do PostgreSQL, grava em Parquet com Polars e permite salvar localmente ou enviar para o Google Cloud Storage (GCS).

## Requisitos
- Docker e Docker Compose instalados.
- Acesso ao banco PostgreSQL que sera extraido.
- Opcional: Python 3.10+ caso queira rodar fora do Docker.

## Configuracao
1. Copie `.env.example` para `.env` e ajuste as variaveis do Postgres e do GCS:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=seu_db
   DB_USER=seu_user
   DB_PASSWORD=seu_password
   ```
2. O upload para o GCS usa a chave `postgres@gobrax-data.iam.gserviceaccount.com.json` que ja esta na raiz. Se trocar a chave ou o bucket, atualize `GCP_CREDENTIALS_PATH`, `GCP_BUCKET_NAME` e `GCP_BASE_PATH`.

## Como rodar
Execute o docker-compose de desenvolvimento, que monta o codigo local como volume e habilita reload automatico:
```bash
docker compose -f docker-compose.dev.yml up --build
```
O FastAPI ficara acessivel em `http://localhost:8000`.

### Rodar sem Docker (opcional)
Caso precise debugar diretamente no host:
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Garanta que as variaveis de ambiente do `.env` estejam exportadas.

## Endpoints
- `POST /extract` -> salva o Parquet em `./data`
- `POST /extract/gcs` -> salva em `./data` e faz upload para `gs://gobrax-data-lake/data-lake/postgres`

Body padrao:
```json
{ "table": "schema.tabela_ou_apenas_tabela" }
```

## Exemplos de uso
### Salvar localmente
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

### Enviar para o GCS
```bash
curl -X POST http://localhost:8000/extract/gcs \
     -H "Content-Type: application/json" \
     -d '{"table": "public.customers"}'
```
Resposta:
```json
{
  "path": "data/public_customers_1715623456.parquet",
  "rows": 1234,
  "gcs_uri": "gs://gobrax-data-lake/data-lake/postgres/<db>/<schema>/<table>/public_customers_1715623456.parquet"
}
```

O arquivo continua salvo em `./data` e tambem fica disponivel no bucket `gobrax-data-lake` no caminho `data-lake/postgres/<db>/<schema>/<table>/`.

## Observacoes
- O processo carrega a tabela inteira em memoria antes de escrever o Parquet. Para tabelas grandes, considere implementar paginacao ou streaming em batches.
- O nome da tabela e validado para aceitar apenas `schema.tabela` ou `tabela` com letras, numeros e underscore, evitando SQL injection.

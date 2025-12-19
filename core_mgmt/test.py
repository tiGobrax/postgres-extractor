import os
from dotenv import load_dotenv
import psycopg2
import pandas as pd
from datetime import datetime

# ==========================================
# 1️⃣ Carrega variáveis de ambiente (.env)
# ==========================================
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("PG_HOST"),
    "port": os.getenv("PG_PORT"),
    "dbname": os.getenv("PG_DATABASE"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
}

SCHEMA = os.getenv("PG_SCHEMA", "public")
TABLE = os.getenv("PG_TABLE", "audit_vehicle_drivers")
LIMIT = os.getenv("PG_LIMIT")  # pode ser None

# ==========================================
# 2️⃣ Monta query dinamicamente
# ==========================================
QUERY = f"SELECT * FROM {SCHEMA}.{TABLE}"
if LIMIT:
    QUERY += f" LIMIT {LIMIT};"
else:
    QUERY += ";"

# ==========================================
# 3️⃣ Caminho do CSV de saída
# ==========================================
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILENAME = os.getenv("OUTPUT_FILENAME", f"{TABLE}_{TIMESTAMP}.csv")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)


def main():
    print("🔌 Iniciando teste de conexão com o PostgreSQL...")

    try:
        # Conecta ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Conexão estabelecida com sucesso.")

        # Executa a query
        print(f"📥 Extraindo dados: {QUERY}")
        df = pd.read_sql_query(QUERY, conn)

        # Mostra preview
        print(f"📊 Linhas extraídas: {len(df)}")
        print(df.head(5))

        # Salva CSV
        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
        print(f"💾 Arquivo CSV gerado: {OUTPUT_FILE}")

    except Exception as e:
        print("❌ Erro ao conectar ou extrair dados:")
        print(e)

    finally:
        try:
            conn.close()
            print("🔒 Conexão fechada.")
        except:
            pass


if __name__ == "__main__":
    main()

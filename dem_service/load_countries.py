import os
import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

def main():
    # Carrega variáveis do .env
    load_dotenv()

    # Conexão com o banco
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
    cursor = conn.cursor()

    # 1) Buscar dados da API
    resp = requests.get("https://restcountries.com/v3.1/all", timeout=10)
    resp.raise_for_status()
    data = resp.json()

    # 2) Preparar registros
    records = []
    for country in data:
        cca3       = country.get("cca3")
        name       = country.get("name", {}).get("common")
        region     = country.get("region")
        subregion  = country.get("subregion")
        population = country.get("population", 0)
        area       = country.get("area", 0.0)
        capital    = country.get("capital", [])
        records.append((cca3, name, region, subregion, population, area, capital))

    # 3) Inserir/upsert em lote
    sql = """
    INSERT INTO country (cca3, name, region, subregion, population, area, capital)
    VALUES %s
    ON CONFLICT (cca3) DO UPDATE SET
      name       = EXCLUDED.name,
      region     = EXCLUDED.region,
      subregion  = EXCLUDED.subregion,
      population = EXCLUDED.population,
      area       = EXCLUDED.area,
      capital    = EXCLUDED.capital;
    """
    execute_values(cursor, sql, records)
    conn.commit()

    cursor.close()
    conn.close()

    print(f"{len(records)} países carregados/atualizados com sucesso.")

if __name__ == "__main__":
    main()
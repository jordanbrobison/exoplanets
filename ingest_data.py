import requests
import os
import psycopg2
from psycopg2.extras import execute_values

API_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

def get_db_config():
    return {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
    }

def fetch_exoplanet_data():
    params = {
        'query': 'select * from pscomppars',
        'format': 'json'
    }

    response = requests.get(API_URL, params=params)
    response.raise_for_status()

    data = response.json()
    return data

def ingest_data(data):
    if not data:
        print("No data to ingest")
        return

    conn = psycopg2.connect(**get_db_config())
    cur = conn.cursor()

    columns = list(data[0].keys())
    col_names = ', '.join(columns)
    update_set = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'pl_name'])

    upsert_query = f"""
        INSERT INTO pscomppars ({col_names}, updated_at)
        VALUES %s
        ON CONFLICT (pl_name) DO UPDATE SET
            {update_set},
            updated_at = CURRENT_TIMESTAMP
    """

    values = []
    for record in data:
        row = [record.get(col) for col in columns] + [None] 
        values.append(tuple(row))

    execute_values(cur, upsert_query, values)

    conn.commit()

    cur.close()
    conn.close()

if __name__ == "__main__":
    data = fetch_exoplanet_data()
    ingest_data(data)

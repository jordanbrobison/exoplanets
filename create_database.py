import json
import os
import psycopg2

def get_db_config():
    return {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
    }

def map_datatype(nasa_type):
    type_mapping = {
        'char': 'TEXT',
        'double': 'DOUBLE PRECISION',
        'float': 'REAL',
        'int': 'INTEGER',
        'long': 'BIGINT',
        'boolean': 'BOOLEAN'
    }
    return type_mapping.get(nasa_type.lower(), 'TEXT')

def create_table():
    with open('pscomppars_schema.json', 'r') as f:
        columns = json.load(f)

    conn = psycopg2.connect(**get_db_config())
    cur = conn.cursor()

    col_definitions = []
    for col in columns:
        col_name = col['column_name']
        col_type = map_datatype(col['datatype'])
        col_definitions.append(f"{col_name} {col_type}")

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS pscomppars (
        {', '.join(col_definitions)},
        PRIMARY KEY (pl_name),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    cur.execute(create_table_sql)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_updated_at ON pscomppars(updated_at)")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_table()

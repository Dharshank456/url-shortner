import os
import psycopg
from psycopg.rows import dict_row


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "urlshortener")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


def get_connection():

    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        row_factory=dict_row
    )



def init_db():

    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS urls (

                    id SERIAL PRIMARY KEY,

                    short_code VARCHAR(255) UNIQUE NOT NULL,

                    original_url TEXT NOT NULL,

                    clicks INTEGER DEFAULT 0

                )
                """
            )

        conn.commit()

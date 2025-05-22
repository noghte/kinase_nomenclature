import os
import psycopg2
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "5432")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def upsert_user(username: str, plain_password: str):
    hashed_password = pwd_context.hash(plain_password)
    try:
        with psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME,
            port=DB_PORT
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (username, password)
                    VALUES (%s, %s)
                    ON CONFLICT (username)
                    DO UPDATE SET password = EXCLUDED.password
                    """,
                    (username, hashed_password)
                )
                conn.commit()
        print(f"User '{username}' inserted/updated successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Insert or update a user.")
    parser.add_argument("username", help="Username for the user")
    parser.add_argument("password", help="Plain text password for the user")
    args = parser.parse_args()
    upsert_user(args.username, args.password)

    #usage example:
    # python user_helper.py testuser testpassword
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')


def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Las variables de entorno SUPABASE_URL y SUPABASE_KEY deben estar configuradas.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

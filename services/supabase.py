from decouple import config
from supabase import create_client

SUPABASE_URL = config("SUPABASE_URL", default="")
SUPABASE_ANON_KEY = config("SUPABASE_ANON_KEY", default="")

supabase = None
if SUPABASE_URL and SUPABASE_ANON_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

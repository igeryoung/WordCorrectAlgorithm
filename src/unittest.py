import os
from dotenv import load_dotenv
from supabase import create_client
from utils import *

def SupabaseConnect():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL and Key must be set in the .env file.")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase
    
if __name__ == "__main__":

    raw_code = '03310251Z4'
    raw_text = '結構用混凝土，預拌，210kgf/cm2，第1型水泥，含澆置及搗實'

    load_dotenv()
    supabase = SupabaseConnect()

    QueryNthCandidateByParentCode(supabase, 0, '03310', int('03310'))
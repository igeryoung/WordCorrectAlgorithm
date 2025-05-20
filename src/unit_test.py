import os
from dotenv import load_dotenv
from supabase import create_client
from utils import *
import time

def SupabaseConnect():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL and Key must be set in the .env file.")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

def measure_execution_time(test_func, input_params):
    """Measure execution time of a function using a dictionary of inputs."""
    st = time.time()
    
    data = test_func(**input_params)
    print("Result length:", len(data) if hasattr(data, '__len__') else "N/A")
    
    ed = time.time()
    print("Time cost:", round(ed - st, 4))
    return data

    
if __name__ == "__main__":

    raw_code = '03310251Z4'
    raw_text = '結構用混凝土，預拌，210kgf/cm2，第1型水泥，含澆置及搗實'

    load_dotenv()
    supabase = SupabaseConnect()

    input_params = {
        "supabase": supabase, 
        "test_code": raw_code
    }

    data = measure_execution_time(QueryAllChapterItemByChapterCode, input_params)
    print(data[0:5])
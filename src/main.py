import os
from dotenv import load_dotenv
from supabase import create_client
from utils import *
from sentence_transformers import SentenceTransformer


def SupabaseConnect():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL and Key must be set in the .env file.")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

def HasCommaPipeline(supabase, raw_code, raw_text):
    corrected_code = []
    corrected_name = []

    chapter_info, raw_text = TestChapterCodeConsistency(supabase, raw_code, raw_text)
    corrected_code.append(chapter_info['chapter'])
    corrected_name.append(chapter_info['name'])

    chapter = int(chapter_info['chapter'])
    cur_rank = 0
    cur_code = chapter_info['chapter']

    for text in raw_text:

        candidates = QueryNthCandidateByParentCode(supabase, 
            rank = cur_rank, 
            parentCode = cur_code, 
            chapter = chapter, 
            col = ['childcode', 'childname'])
        
        for candidate in candidates:
            if text == candidate['childname']:
                cur_code = candidate['childcode']
                corrected_code.append(candidate['childcode'])
                corrected_name.append(candidate['childname'])
                break
            else:
                pass

        cur_rank += 1





if __name__ == "__main__":

    raw_code = '03310251Z4'
    raw_text = '結構用混凝土，預拌，210kgf/cm2，第1型水泥，含澆置及搗實'

    load_dotenv()
    supabase = SupabaseConnect()
    model = SentenceTransformer(
        "shibing624/text2vec-base-chinese",
        backend="onnx",
        model_kwargs={"file_name": "model_qint8_avx512_vnni.onnx"},
    )


    mode, raw_text = TestCommaExist(raw_text)

    if mode == "comma":
        HasCommaPipeline(supabase, raw_code, raw_text)
        
    

    

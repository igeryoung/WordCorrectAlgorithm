import os
from dotenv import load_dotenv
from supabase import create_client
from utils import *
import torch
from sentence_transformers import SentenceTransformer
import onnxruntime as ort
ort.set_default_logger_severity(3)


def SupabaseConnect():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL and Key must be set in the .env file.")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

def HasCommaPipeline(supabase, model, raw_code, raw_text):
    corrected_code = []
    corrected_name = []

    chapter_info, raw_text = TestChapterCodeConsistency(supabase, raw_code, raw_text)
    corrected_code.append(chapter_info['chapter'])
    corrected_name.append(chapter_info['name'])

    chapter = int(chapter_info['chapter'])
    cur_rank = 0
    cur_code = chapter_info['chapter']

    for text in raw_text[1:]:
        candidates = QueryNthCandidateByParentCode(supabase, 
            rank = cur_rank, 
            parentCode = cur_code, 
            chapter = chapter, 
            col = ['childcode', 'childname'])
        candidates_list = jsonl_to_list(candidates)

        if len(candidates_list) == 0:
            break

        if text in candidates_list['childname']:
            idx = candidates_list['childname'].index(text)
        else:
            embeddings = model.encode([text] + candidates_list['childname'])
            similarities = model.similarity(embeddings, embeddings)
            idx = torch.argmax(similarities[0][1:])
        
        corrected_code.append(candidates[idx]['childcode'])
        corrected_name.append(candidates[idx]['childname'])

        cur_rank += 1
        cur_code = candidates[idx]['childcode']

    print(corrected_code)
    print(corrected_name)
    return corrected_code, corrected_name



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
        HasCommaPipeline(supabase, model, raw_code, raw_text)
        
    

    

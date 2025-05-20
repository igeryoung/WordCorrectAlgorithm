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

    chapter = chapter_info['chapter']
    cur_digit = 5
    cur_code = chapter_info['chapter']

    for text in raw_text[1:]:
        candidates = QueryNthCandidateByParentCode(supabase, 
            digit = cur_digit, 
            parentCode = cur_code, 
            chapter = chapter, 
            col = ['child_code', 'child_name'])
        candidates_list = jsonl_to_list(candidates)

        if len(candidates_list['child_name']) == 0:
            break

        if text in candidates_list['child_name']:
            idx = candidates_list['child_name'].index(text)
        else:
            embeddings = model.encode([text] + candidates_list['child_name'])
            similarities = model.similarity(embeddings, embeddings)
            idx = torch.argmax(similarities[0][1:])
        
        corrected_code.append(candidates_list['child_code'][idx])
        corrected_name.append(candidates_list['child_name'][idx])

        cur_digit += 1
        cur_code = candidates_list['child_code'][idx]

    return corrected_code, corrected_name

def NoCommaPipeline(supabase, model, raw_code, raw_text):
    corrected_code = []
    corrected_name = []

    # determine chapter
    chapter_code = None
    info_from_code = GetChapterInfoByCode(supabase, raw_code)
    if info_from_code['name'] in raw_text:
        chapter_code = info_from_code['chapter']
    else:
        data = QueryAllChapterItemByChapterCode(supabase, raw_code)
        for item in data:
            if item in raw_text:
                chapter_code = info_from_code['chapter']


if __name__ == "__main__":

    # init
    load_dotenv()
    supabase = SupabaseConnect()
    model = SentenceTransformer(
        "shibing624/text2vec-base-chinese",
        backend="onnx",
        model_kwargs={"file_name": "model_qint8_avx512_vnni.onnx"},
    )

    # testing data
    raw_code = '03310251Z4'
    raw_text = '結構用混凝土，預拌，210kgf/cm2，第1型水泥，含澆置及搗實'

    # main function
    raw_code = remove_first_english_char(raw_code)

    mode, raw_text = TestCommaExist(raw_text)
    if mode == "comma":
        corrected_code, corrected_name = HasCommaPipeline(supabase, model, raw_code, raw_text)
        print(corrected_code, corrected_name)
    elif mode == "no_comma":
        pass
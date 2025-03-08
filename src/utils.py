def GetChapterInfoByCode(supabase, test_code):
    try:
        raw_code = test_code[:5]
        response = supabase.table("chapter_name").select("*").eq("chapter", raw_code).execute()
        
        if not response.data:
            raise ValueError(f"No data found for chapter code: {raw_code}")
        
        data = response.data[0]
        return data
    except Exception as e:
        print("An error occurred:", e)
        return None
    
def GetChapterInfoByText(supabase, text):
    try:
        response = supabase.table("chapter_name").select("*").eq("name", text).execute()
        
        if not response.data:
            raise ValueError(f"No data found for chapter text: {text}")
        
        data = response.data[0]
        return data
    except Exception as e:
        print("An error occurred:", e)
        return None
    
def TestCommaExist(raw_text):
    if '，' in raw_text:
        data = raw_text.split('，')
        return "comma", data
    else:
        return "no_comma", raw_text
    
def TestChapterCodeConsistency(supabase, raw_code, raw_text):
    info_from_code = GetChapterInfoByCode(supabase, raw_code)
    info_from_text = GetChapterInfoByText(supabase, raw_text[0])

    if info_from_code != info_from_text:
        raw_text = [info_from_code["chapter"]] + raw_text

    return raw_text

def QueryNthCandidateByParentCode(supabase, n, parentCode, chapter):
    try:
        response = supabase.table("link").select("*").match({
            "chapter": chapter,
            "rank": parentCode,
            "code": parentCode
        }).execute()
        
        if not response.data:
            raise ValueError(f"No data found for parent code: {parentCode}")
        
        return response.data
    except Exception as e:
        print("An error occurred:", e)
        return None
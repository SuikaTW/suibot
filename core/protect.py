import re

class Protect():
    """關鍵字過濾器。"""
    def __init__(self) -> None:
        pass

    def message(content: str = None):
        """輸入需要檢測的變數，會回傳檢測結果訊息，若無問題則直接回傳原始訊息。"""
        if content is None:
            return "沒有輸入任何資料。"
        
        if find_keyword(content):
            return "你不能標註 everyone 或 here！"

        if find_token(content):
            return "你不能輸入 Token！"
        
        if find_public_key(content):
            return "你不能輸入公鑰！"
        
        return content
    
def find_keyword(content):
    for key in ["@everyone", "@here"]:
        if key in content:
            return True
    return None
    
def find_token(content):
    token_regex = re.compile(r'[A-Za-z0-9]{24}\.[A-Za-z0-9]{6}\.[A-Za-z0-9_-]{27}')
    match = re.search(token_regex, content)
    return match.group(0) if match else None

def find_public_key(content):
    public_key_regex = re.compile(r'[A-Fa-f0-9]{64}')
    match = re.search(public_key_regex, content)
    return match.group(0) if match else None
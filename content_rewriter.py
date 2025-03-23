import requests
from config import LLM_API_KEY, LLM_API_ENDPOINT


class ContentRewriter:
    def __init__(self):
        self.api_key = LLM_API_KEY
        self.api_endpoint = LLM_API_ENDPOINT

    def rewrite(self, text):
        if not text:
            return ""

        payload = {
            "text": text,
            "instruction": "请将以下内容改写为自然流畅的中文，保持原意但使用不同的表达方式",
            "api_key": self.api_key
        }

        try:
            response = requests.post(self.api_endpoint, json=payload)
            response.raise_for_status()
            return response.json().get("rewritten_text", text)
        except Exception as e:
            print(f"改写失败: {e}")
            return text
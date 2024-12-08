from .base import LLMClientBase
from typing import List, Dict
from openai import OpenAI

class OpenAIClient(LLMClientBase):
    """
    Implementation of LLMClientBase for interacting with OpenAI's API.
    """

    def __init__(self, _api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = _api_key
        self.model = model

    def evaluate_relevance(self, content: str) -> str:
        messages = [
            {
                "role": "system",
                "content": "你是一個關聯度評估機器人，請評估新聞標題是否與「民生用品的價格變化」相關，並給予'high'、'medium'、'low'評價。(僅需回答'high'、'medium'、'low'三個詞之一)"
            },
            {"role": "user", "content": content}
        ]
        return self._generate_text(messages=messages)

    def generate_summary(self, content: str) -> str:
        messages = [
            {
                "role": "system",
                "content": "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})"
            },
            {"role": "user", "content": content}
        ]
        return self._generate_text(messages=messages)

    def extract_search_keywords(self, content: str) -> str:
        messages = [
            {
                "role": "system",
                "content": "你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，請提取出用戶希望看見的關鍵字，請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)"
            },
            {"role": "user", "content": content}
        ]
        return self._generate_text(messages=messages)

    @staticmethod
    def _generate_text(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate text using OpenAI's API based on the provided messages.

        :param messages: List of dict messages to be sent to the OpenAI API.
        :return: The generated response as a string.
        """
        try:
            # Call OpenAI's ChatCompletion API
            response = OpenAI.ChatCompletion.create(
                model=self.model,
                messages=messages,
                api_key=self.api_key
            )
            # Extract and return the generated content
            return response['choices'][0]['message']['content'].strip()
        except OpenAI.error.OpenAIError as e:
            # Handle API errors gracefully
            return f"Error: {e}"

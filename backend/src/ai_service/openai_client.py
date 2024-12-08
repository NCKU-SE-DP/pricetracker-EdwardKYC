from .base import LLMClientBase
from typing import List, Dict
from .prompts import EXTRACT_KEYWORDS_PROMPT, GENERATE_SUMMARY_PROMPT, RELEVANCE_CHECK_PROMPT
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
                "content": RELEVANCE_CHECK_PROMPT
            },
            {"role": "user", "content": content}
        ]
        return self._generate_text(messages=messages)

    def generate_summary(self, content: str) -> str:
        messages = [
            {
                "role": "system",
                "content": GENERATE_SUMMARY_PROMPT
            },
            {"role": "user", "content": content}
        ]
        return self._generate_text(messages=messages)

    def extract_search_keywords(self, content: str) -> str:
        messages = [
            {
                "role": "system",
                "content": EXTRACT_KEYWORDS_PROMPT
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

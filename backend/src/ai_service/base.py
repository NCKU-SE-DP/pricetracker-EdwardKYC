import abc
from abc import ABC, abstractmethod
from typing import List, Dict
from pydantic import BaseModel, Field
import aisuite as ai
from .prompts import EXTRACT_KEYWORDS_PROMPT, GENERATE_SUMMARY_PROMPT, RELEVANCE_CHECK_PROMPT

class LLMClientBase(metaclass=abc.ABCMeta):
    @staticmethod
    @abc.abstractmethod
    def _generate_text(messages: List[Dict[str, str]]) -> str:
        pass

    @staticmethod
    def validate_message_format(message: Dict[str, str]) -> bool:
        required_keys = {"role", "content"}
        return all(key in message for key in required_keys) and isinstance(message["content"], str)

    def validate_messages(self, messages: List[Dict[str, str]]) -> bool:
        return all(self.validate_message_format(message) for message in messages)
    

class LLMClientTemplate(ABC):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.client = None
        self._initialize_client()  

    @abstractmethod
    def _initialize_client(self):
        pass

    def evaluate_relevance(self, content: str) -> str:
        messages = [
            {"role": "system", "content": RELEVANCE_CHECK_PROMPT},
            {"role": "user", "content": content},
        ]
        return self._generate_text(messages=messages)

    def generate_summary(self, content: str) -> str:
        messages = [
            {"role": "system", "content": GENERATE_SUMMARY_PROMPT},
            {"role": "user", "content": content},
        ]
        return self._generate_text(messages=messages)

    def extract_search_keywords(self, content: str) -> str:
        messages = [
            {"role": "system", "content": EXTRACT_KEYWORDS_PROMPT},
            {"role": "user", "content": content},
        ]
        return self._generate_text(messages=messages)

    def _generate_text(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.75,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"

class MessagePassingInterface(BaseModel):
    """
    Represents the structure of a message sent to the LLM API.
    """
    system_content: str = Field(...)
    user_content: str = Field(...)

    @property
    def to_dict(self):
        value = [
            {"role": "system", "content": f"{self.system_content}"},
            {"role": "user", "content": f"{self.user_content}"},
        ]
        return value
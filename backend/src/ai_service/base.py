import abc
from typing import List, Dict
from pydantic import BaseModel, Field

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
    


class LLMClientBase(metaclass=abc.ABCMeta):
    """
    Abstract base class for an LLM (Large Language Model) client.
    Defines the required interface for any LLM client implementation.
    """

    @abc.abstractmethod
    def evaluate_relevance(self, content: str) -> str:
        """
        Evaluates the relevance of the content.
        :param content: The input text to evaluate.
        :return: A string indicating the relevance ('high', 'medium', 'low').
        """
        pass

    @abc.abstractmethod
    def generate_summary(self, content: str) -> str:
        """
        Generates a summary for the given content.
        :param content: The input text to summarize.
        :return: A string containing the summary in JSON format.
        """
        pass

    @abc.abstractmethod
    def extract_search_keywords(self, content: str) -> str:
        """
        Extracts search keywords from the given content.
        :param content: The input text to analyze.
        :return: A space-separated string of keywords.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def _generate_text(messages: List[Dict[str, str]]) -> str:
        """
        Sends a list of messages to the LLM and retrieves the generated text.
        :param messages: A list of messages to send to the LLM.
        :return: The text response from the LLM.
        """
        pass

    @staticmethod
    def validate_message_format(message: Dict[str, str]) -> bool:
        """
        Validates the format of a single message to ensure it conforms to the required structure.
        :param message: A dictionary representing a single message.
        :return: True if valid, False otherwise.
        """
        required_keys = {"role", "content"}
        return all(key in message for key in required_keys) and isinstance(message["content"], str)

    def validate_messages(self, messages: List[Dict[str, str]]) -> bool:
        """
        Validates a list of messages to ensure all conform to the required structure.
        :param messages: A list of message dictionaries.
        :return: True if all messages are valid, False otherwise.
        """
        return all(self.validate_message_format(message) for message in messages)



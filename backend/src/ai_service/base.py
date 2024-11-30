import abc
from pydantic import BaseModel, Field


class MessagePassingInterfaceExample(BaseModel):
    """
    Example of a message interface for interaction with LLM clients.
    """
    role: str = Field(
        default=...,
        example="user",
        description="The role of the message sender, such as 'user', 'system', or 'assistant'."
    )
    content: str = Field(
        default=...,
        example="Hello, how can I assist you?",
        description="The content of the message to be passed to the LLM."
    )   


class LLMClientBase(metaclass=abc.ABCMeta):
    """
    Abstract base class for an LLM (Large Language Model) client.
    Defines the required interface for any LLM client implementation.
    """

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
    def _generate_text(messages: list[dict]) -> str:
        """
        Sends a list of messages to the LLM and retrieves the generated text.
        :param messages: A list of messages to send to the LLM.
        :return: The text response from the LLM.
        """
        pass

from typing import Protocol
from pydantic import BaseModel


class LLmProvider(Protocol):
    """Generic use case for an LLM"""
    def generate(self, prompt: str) -> LLmOutput:
        """
        Method for generating model output based on a request

        Argument:
            prompt(str): The request

        Return:
            (LLmOutput): The AI ​​output
        """
        ...


class LlmError(Exception):
    """
    Class to handle exceptions when the usage limit is reached
    """
    pass


class LLmOutput(BaseModel):
    """
    Class to manage LLM output

    Args:
        content(str): The LLM output
        response_time(float): The time taken by the LLM to respond
        total_input_tokens(int): The number of tokens taken as input
        total_output_tokens(int): The number of tokens generated
        api_url(str): The URL to use the AI
        model_name(str): The name of the model used
    """
    content: str

    reponse_time: float

    total_input_tokens: int
    total_output_tokens: int

    api_url: str
    model_name: str

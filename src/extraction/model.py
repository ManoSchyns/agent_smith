from abc import abstractmethod, ABC


class ExtractError(Exception):
    """
    Error handling for extraction
    """
    pass


class ExtractStrategy(ABC):
    """
    Extraction model startegy
    """

    @abstractmethod
    def can_extract(self, llm_output: str) -> bool:
        """
        Tell if the code can be extract

        Arg:
            llm_output (str): The output of the llm

        Return
            True / False if the code can be extract
        """
        pass

    @abstractmethod
    def extract(self, llm_output: str) -> str:
        """
        Extract the code present in the llm_output

        Arg:
            llm_output (str): The output of the llm

        Return:
            The extracted code
        """
        pass

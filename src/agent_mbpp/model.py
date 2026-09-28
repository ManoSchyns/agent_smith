from pydantic import BaseModel, Field


class MBPPError(Exception):
    """Classe d'erreur pour l agent MBPP"""
    pass


class MBPPTaskInput(BaseModel):
    """Input for MBPP task evaluation."""
    task_id: int
    task_definition: str
    function_definition: str
    test_imports: list[str] = Field(default_factory=list)
    test_list: list[str] = Field(default_factory=list)

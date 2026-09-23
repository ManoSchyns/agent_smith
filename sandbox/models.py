from pydantic import BaseModel, Field


class SandboxConfig(BaseModel):
    """Sandbox configuration for student solutions.
    Uses allowlist approach: only imports in authorized_imports are allowed.
    Everything else is blocked by default.
    """

    authorized_imports: list[str] = Field(default_factory=lambda: [
        "math", "math.*",
        "collections", "collections.*",
        "itertools", "re", "json",
        "typing", "typing.*",
        "functools", "operator",
        "heapq", "bisect", "copy",
        "string", "random",
        "datetime", "datetime.*",
        "array", "cmath",
    ])

    allowed_directories: list[str] = Field(default_factory=lambda: [
        "/testbed", "/tmp/agent"
    ])

    max_execution_time_seconds: int = Field(default=30, gt=0)
    max_memory_mb: int = Field(default=512, gt=0)

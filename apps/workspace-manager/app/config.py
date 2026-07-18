from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ollama_namespace: str = "ai"
    ollama_deployment: str = "ollama"

    workspace_namespace: str = "jupyter"
    code_server_deployment: str = "code-server"
    jupyter_deployment: str = "jupyter"

    operation_timeout_seconds: int = 180
    polling_interval_seconds: float = 2.0


settings = Settings()

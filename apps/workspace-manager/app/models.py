from enum import StrEnum

from pydantic import BaseModel


class ServiceState(StrEnum):
    RUNNING = "running"
    STARTING = "starting"
    STOPPED = "stopped"
    ERROR = "error"


class WorkspaceMode(StrEnum):
    COPILOT = "copilot"
    TRAIN = "train"
    STOPPED = "stopped"
    TRANSITION = "transition"
    UNKNOWN = "unknown"


class ServicesStatus(BaseModel):
    code_server: ServiceState
    ollama: ServiceState
    jupyter: ServiceState


class WorkspaceStatus(BaseModel):
    mode: WorkspaceMode
    services: ServicesStatus


class WorkspaceActionResponse(BaseModel):
    message: str
    status: WorkspaceStatus

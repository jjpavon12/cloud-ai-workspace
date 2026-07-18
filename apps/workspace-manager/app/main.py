from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.kubernetes_service import (
    KubernetesWorkspaceService,
    WorkspaceOperationError,
)
from app.models import WorkspaceActionResponse, WorkspaceStatus


APP_DIRECTORY = Path(__file__).resolve().parent
STATIC_DIRECTORY = APP_DIRECTORY / "static"
TEMPLATES_DIRECTORY = APP_DIRECTORY / "templates"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.workspace_service = KubernetesWorkspaceService()
    yield


app = FastAPI(
    title="Cloud AI Workspace Manager",
    version="0.2.0",
    description=(
        "API y panel de control para gestionar los modos "
        "Copilot y Train de Cloud AI Workspace."
    ),
    lifespan=lifespan,
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIRECTORY),
    name="static",
)

templates = Jinja2Templates(
    directory=TEMPLATES_DIRECTORY,
)


def get_workspace_service(
    request: Request,
) -> KubernetesWorkspaceService:
    return request.app.state.workspace_service


@app.get(
    "/",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get(
    "/status",
    response_model=WorkspaceStatus,
)
def workspace_status(request: Request) -> WorkspaceStatus:
    service = get_workspace_service(request)

    try:
        return service.get_status()
    except WorkspaceOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@app.post(
    "/copilot",
    response_model=WorkspaceActionResponse,
)
def enable_copilot(request: Request) -> WorkspaceActionResponse:
    service = get_workspace_service(request)

    try:
        workspace_status = service.enable_copilot_mode()
    except WorkspaceOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return WorkspaceActionResponse(
        message="Modo Copilot activado.",
        status=workspace_status,
    )


@app.post(
    "/train",
    response_model=WorkspaceActionResponse,
)
def enable_train(request: Request) -> WorkspaceActionResponse:
    service = get_workspace_service(request)

    try:
        workspace_status = service.enable_train_mode()
    except WorkspaceOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return WorkspaceActionResponse(
        message="Modo Train activado.",
        status=workspace_status,
    )


@app.post(
    "/stop",
    response_model=WorkspaceActionResponse,
)
def stop_gpu_services(
    request: Request,
) -> WorkspaceActionResponse:
    service = get_workspace_service(request)

    try:
        workspace_status = service.stop_gpu_services()
    except WorkspaceOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return WorkspaceActionResponse(
        message="Servicios con GPU detenidos.",
        status=workspace_status,
    )

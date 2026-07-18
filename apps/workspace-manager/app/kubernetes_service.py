import time
from dataclasses import dataclass

from kubernetes import client, config
from kubernetes.client import AppsV1Api
from kubernetes.client.exceptions import ApiException

from app.config import settings
from app.models import (
    ServicesStatus,
    ServiceState,
    WorkspaceMode,
    WorkspaceStatus,
)


class WorkspaceOperationError(RuntimeError):
    """Raised when a workspace transition cannot be completed."""


@dataclass(frozen=True)
class DeploymentReference:
    namespace: str
    name: str


OLLAMA = DeploymentReference(
    namespace=settings.ollama_namespace,
    name=settings.ollama_deployment,
)

CODE_SERVER = DeploymentReference(
    namespace=settings.workspace_namespace,
    name=settings.code_server_deployment,
)

JUPYTER = DeploymentReference(
    namespace=settings.workspace_namespace,
    name=settings.jupyter_deployment,
)


class KubernetesWorkspaceService:
    def __init__(self) -> None:
        config.load_incluster_config()
        self.apps_api: AppsV1Api = client.AppsV1Api()

    def _read_deployment(
        self,
        deployment: DeploymentReference,
    ) -> client.V1Deployment:
        try:
            return self.apps_api.read_namespaced_deployment(
                name=deployment.name,
                namespace=deployment.namespace,
            )
        except ApiException as exc:
            raise WorkspaceOperationError(
                f"No se pudo consultar "
                f"{deployment.namespace}/{deployment.name}: "
                f"{exc.reason}"
            ) from exc

    def _scale_deployment(
        self,
        deployment: DeploymentReference,
        replicas: int,
    ) -> None:
        body = {
            "spec": {
                "replicas": replicas,
            }
        }

        try:
            self.apps_api.patch_namespaced_deployment_scale(
                name=deployment.name,
                namespace=deployment.namespace,
                body=body,
            )
        except ApiException as exc:
            raise WorkspaceOperationError(
                f"No se pudo escalar "
                f"{deployment.namespace}/{deployment.name} "
                f"a {replicas} réplicas: {exc.reason}"
            ) from exc

    def _deployment_state(
        self,
        deployment: DeploymentReference,
    ) -> ServiceState:
        resource = self._read_deployment(deployment)

        desired = resource.spec.replicas or 0
        ready = resource.status.ready_replicas or 0
        available = resource.status.available_replicas or 0

        if desired == 0:
            return ServiceState.STOPPED

        if ready >= desired and available >= desired:
            return ServiceState.RUNNING

        return ServiceState.STARTING

    def _wait_for_state(
        self,
        deployment: DeploymentReference,
        expected_state: ServiceState,
    ) -> None:
        deadline = time.monotonic() + settings.operation_timeout_seconds

        while time.monotonic() < deadline:
            current_state = self._deployment_state(deployment)

            if current_state == expected_state:
                return

            time.sleep(settings.polling_interval_seconds)

        raise WorkspaceOperationError(
            f"Tiempo de espera agotado esperando que "
            f"{deployment.namespace}/{deployment.name} "
            f"alcanzara el estado '{expected_state.value}'."
        )

    def _ensure_code_server(self) -> None:
        self._scale_deployment(CODE_SERVER, 1)
        self._wait_for_state(CODE_SERVER, ServiceState.RUNNING)

    def get_status(self) -> WorkspaceStatus:
        services = ServicesStatus(
            code_server=self._deployment_state(CODE_SERVER),
            ollama=self._deployment_state(OLLAMA),
            jupyter=self._deployment_state(JUPYTER),
        )

        if (
            services.ollama == ServiceState.RUNNING
            and services.jupyter == ServiceState.STOPPED
        ):
            mode = WorkspaceMode.COPILOT

        elif (
            services.ollama == ServiceState.STOPPED
            and services.jupyter == ServiceState.RUNNING
        ):
            mode = WorkspaceMode.TRAIN

        elif (
            services.ollama == ServiceState.STOPPED
            and services.jupyter == ServiceState.STOPPED
        ):
            mode = WorkspaceMode.STOPPED

        elif (
            services.ollama == ServiceState.STARTING
            or services.jupyter == ServiceState.STARTING
            or services.code_server == ServiceState.STARTING
        ):
            mode = WorkspaceMode.TRANSITION

        else:
            mode = WorkspaceMode.UNKNOWN

        return WorkspaceStatus(
            mode=mode,
            services=services,
        )

    def enable_copilot_mode(self) -> WorkspaceStatus:
        self._ensure_code_server()

        self._scale_deployment(JUPYTER, 0)
        self._wait_for_state(JUPYTER, ServiceState.STOPPED)

        self._scale_deployment(OLLAMA, 1)
        self._wait_for_state(OLLAMA, ServiceState.RUNNING)

        return self.get_status()

    def enable_train_mode(self) -> WorkspaceStatus:
        self._ensure_code_server()

        self._scale_deployment(OLLAMA, 0)
        self._wait_for_state(OLLAMA, ServiceState.STOPPED)

        self._scale_deployment(JUPYTER, 1)
        self._wait_for_state(JUPYTER, ServiceState.RUNNING)

        return self.get_status()

    def stop_gpu_services(self) -> WorkspaceStatus:
        self._ensure_code_server()

        self._scale_deployment(OLLAMA, 0)
        self._scale_deployment(JUPYTER, 0)

        self._wait_for_state(OLLAMA, ServiceState.STOPPED)
        self._wait_for_state(JUPYTER, ServiceState.STOPPED)

        return self.get_status()

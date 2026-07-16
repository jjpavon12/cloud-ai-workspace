# Cloud AI Workspace

Plataforma personal de desarrollo de inteligencia artificial desplegada sobre Kubernetes, diseñada para ejecutar cargas de trabajo de forma remota utilizando los recursos de una torre Windows con GPU NVIDIA.

El objetivo principal del proyecto es poder acceder desde un portátil a un entorno JupyterLab ejecutado en la torre, aprovechando su CPU, memoria y GPU sin necesidad de exponer servicios directamente a Internet.

## Arquitectura

```text
Laptop
  │
  │ Tailscale private network
  ▼
Tailscale Serve
  │
  │ HTTPS
  ▼
Windows host
  │
  │ Local port forwarding
  ▼
WSL2 Ubuntu
  │
  ▼
k3s
  │
  ▼
Traefik Ingress
  │
  ▼
JupyterLab
  │
  ├── Persistent workspace
  └── NVIDIA GPU
```

## Características actuales

* Kubernetes ligero mediante k3s.
* Despliegue sobre Ubuntu 24.04 en WSL2.
* Integración de una GPU NVIDIA con Kubernetes.
* NVIDIA Container Toolkit y NVIDIA Device Plugin.
* JupyterLab con soporte CUDA y PyTorch.
* Volumen persistente para conservar notebooks y proyectos.
* Acceso mediante Traefik Ingress.
* Servicio interno de tipo `ClusterIP`.
* Acceso remoto privado y cifrado mediante Tailscale.
* HTTPS proporcionado por Tailscale Serve.
* Sin puertos expuestos directamente a Internet.

## Tecnologías

* Windows 11
* WSL2
* Ubuntu 24.04
* k3s
* Kubernetes
* containerd
* NVIDIA Container Toolkit
* NVIDIA Device Plugin
* Traefik
* JupyterLab
* PyTorch
* Tailscale

## Estructura del repositorio

```text
.
├── apps/
│   └── jupyter/
│       ├── deployment.yaml
│       └── ingress.yaml
│
├── infrastructure/
│   ├── gpu/
│   │   ├── nvidia-device-plugin.yaml
│   │   └── gpu-test.yaml
│   └── k3s/
│       └── install-k3s.sh
│
├── scripts/
├── docs/
├── .gitignore
└── README.md
```

### `apps`

Contiene las aplicaciones desplegadas sobre la plataforma.

Actualmente incluye JupyterLab, pero está previsto añadir nuevos servicios como VS Code Server, Ollama y MLflow.

### `infrastructure`

Contiene la configuración necesaria para preparar la plataforma base:

* instalación de k3s;
* runtime de NVIDIA;
* NVIDIA Device Plugin;
* pruebas de acceso a la GPU.

### `scripts`

Contendrá scripts para automatizar la instalación, actualización, comprobación y eliminación de la plataforma.

### `docs`

Contendrá documentación técnica, diagramas de arquitectura, decisiones de diseño y resolución de problemas.

## Estado actual

La primera versión funcional permite:

1. Acceder desde un portátil a la torre mediante Tailscale.
2. Entrar en JupyterLab desde una URL HTTPS privada.
3. Ejecutar notebooks dentro de Kubernetes.
4. Utilizar la GPU NVIDIA desde PyTorch.
5. Conservar los archivos mediante un volumen persistente.

Ejemplo de comprobación de GPU:

```python
import torch

print("CUDA disponible:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
```

Resultado esperado:

```text
CUDA disponible: True
GPU: NVIDIA GeForce RTX 2070 SUPER
```

## Despliegue actual

### Instalar k3s

```bash
./infrastructure/k3s/install-k3s.sh
```

### Instalar NVIDIA Device Plugin

```bash
kubectl apply \
  -f infrastructure/gpu/nvidia-device-plugin.yaml
```

### Comprobar acceso a la GPU

```bash
kubectl apply \
  -f infrastructure/gpu/gpu-test.yaml

kubectl logs gpu-test
kubectl delete pod gpu-test
```

### Crear el namespace de Jupyter

```bash
kubectl create namespace jupyter
```

### Crear el token de acceso

```bash
JUPYTER_TOKEN=$(openssl rand -hex 16)

kubectl create secret generic jupyter-auth \
  --namespace jupyter \
  --from-literal=token="$JUPYTER_TOKEN"
```

### Desplegar JupyterLab

```bash
kubectl apply -f apps/jupyter/deployment.yaml
kubectl apply -f apps/jupyter/ingress.yaml
```

### Comprobar el despliegue

```bash
kubectl get pods,svc,ingress,pvc -n jupyter
```

## Acceso remoto

El acceso remoto se realiza mediante Tailscale Serve y solo está disponible para los dispositivos autorizados dentro de la red privada de Tailscale.

La URL utilizada actualmente tiene el siguiente formato:

```text
https://jprlab.<tailnet>.ts.net
```

Las credenciales y secretos utilizados para acceder a la plataforma no se almacenan en este repositorio.

## Próximas mejoras

* Automatizar completamente la instalación.
* Eliminar configuraciones manuales de Windows.
* Añadir comprobaciones de estado y recuperación.
* Añadir VS Code Server.
* Desplegar Ollama para ejecutar modelos de lenguaje locales.
* Añadir MLflow para seguimiento de experimentos.
* Incorporar Prometheus y Grafana.
* Añadir CI/CD mediante GitHub Actions.
* Documentar copias de seguridad y recuperación.
* Crear un diagrama visual de arquitectura.

## Seguridad

La plataforma no expone directamente JupyterLab a Internet.

El acceso se realiza mediante una red privada de Tailscale y HTTPS. Los tokens, claves y otros secretos deben crearse localmente y nunca almacenarse en Git.

## Licencia

Este proyecto se desarrolla con fines educativos y como laboratorio personal de Cloud, Kubernetes e inteligencia artificial.


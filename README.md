# Cloud AI Workspace

## Descripción

Cloud AI Workspace es una plataforma personal de desarrollo Cloud e IA desplegada
sobre Kubernetes en un equipo local con GPU NVIDIA.

La plataforma permite acceder remotamente a entornos de desarrollo mediante el
navegador, utilizando la capacidad de procesamiento y la GPU del equipo anfitrión.

Actualmente incluye:

- JupyterLab para experimentación, notebooks y entrenamiento de modelos.
- code-server para desarrollo de proyectos desde una interfaz similar a VS Code.
- Almacenamiento persistente compartido entre ambos entornos.
- Soporte para GPU NVIDIA dentro de Kubernetes.
- Traefik como controlador Ingress.
- Acceso remoto privado y HTTPS mediante Tailscale.

## Arquitectura

```text
                         Portátil
                            │
                     Red Tailscale
                            │
                  HTTPS - Tailscale Serve
                            │
                         Traefik
                 ┌──────────┴──────────┐
                 │                     │
            JupyterLab            code-server
                 │                     │
                 └──────────┬──────────┘
                            │
                 PersistentVolumeClaim
                            │
                       Proyectos
                            │
                    k3s sobre WSL2
                            │
                   GPU NVIDIA del host

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

## Aplicaciones

### JupyterLab

Entorno orientado a experimentación, análisis de datos y entrenamiento de
modelos mediante notebooks.

El directorio de trabajo está montado en:

```text
/home/jovyan/work
```

### Code-server

Entorno de desarrollo accesible desde el navegador, basado en Visual Studio Code.

El workspace compartido está montado en:

```text
/home/coder/work
```

Ambos directorios apuntan al mismo volumen persistente, por lo que los proyectos
creados en JupyterLab pueden abrirse y modificarse desde code-server y viceversa.

## Despliegue

Para desplegar la plataforma completa:

```bash
git clone git@github.com:jjpavon12/cloud-ai-workspace.git
cd cloud-ai-workspace
chmod +x scripts/*.sh
chmod +x infrastructure/k3s/*.sh
chmod +x infrastructure/gpu/*.sh
./scripts/install.sh
```
Para consultar el estado:
```bash
./scripts/status.sh
```

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
6. Entrar en Code-Server desde una URL HTTPS privada.

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

La plataforma se expone únicamente dentro de la red privada de Tailscale.

| Aplicación | Ruta |
|---|---|
| JupyterLab | `/` |
| code-server | `/code/` |

Las credenciales se almacenan como Secrets de Kubernetes y no se incluyen en
el repositorio.

## Próximas mejoras

### Roadmap

- [x] k3s sobre WSL2
- [x] Soporte para GPU NVIDIA
- [x] JupyterLab
- [x] Almacenamiento persistente
- [x] Acceso remoto mediante Tailscale
- [x] code-server
- [ ] Ollama
- [ ] Chatbot web local
- [ ] Copiloto de programación conectado a Ollama
- [ ] MLflow
- [ ] Prometheus y Grafana
- [ ] CI/CD con GitHub Actions

## Seguridad

La plataforma no expone directamente las aplicaciones a Internet.

El acceso se realiza mediante una red privada de Tailscale y HTTPS. Los tokens, claves y otros secretos deben crearse localmente y nunca almacenarse en Git.

## Licencia

Este proyecto se desarrolla con fines educativos y como laboratorio personal de Cloud, Kubernetes e inteligencia artificial.


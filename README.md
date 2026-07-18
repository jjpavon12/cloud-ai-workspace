# Cloud AI Workspace

Cloud AI Workspace es una plataforma personal orientada al desarrollo de aplicaciones de Inteligencia Artificial sobre Kubernetes.

El objetivo del proyecto es disponer de un entorno de trabajo accesible desde cualquier lugar que combine herramientas de desarrollo, entrenamiento de modelos y asistentes de IA locales utilizando la capacidad de cómputo de un equipo personal con GPU NVIDIA.

Actualmente la plataforma integra servicios como JupyterLab, Code Server, Ollama y un Workspace Manager desarrollado en FastAPI para gestionar los distintos modos de trabajo.

---

# Características

- Kubernetes ligero mediante k3s.
- GPU NVIDIA integrada en Kubernetes.
- JupyterLab para entrenamiento y experimentación.
- Code Server accesible desde el navegador.
- Ollama para ejecutar LLMs de forma local.
- Continue como asistente de programación conectado a Ollama.
- Workspace Manager para gestionar los distintos modos de trabajo.
- Dashboard web desarrollado con FastAPI.
- Almacenamiento persistente compartido.
- Acceso remoto privado mediante Tailscale.
- HTTPS mediante Tailscale Serve.
- Toda la infraestructura definida mediante manifiestos de Kubernetes.

---

# Arquitectura

```text
                        ┌─────────────────────────┐
                        │ Cliente (PC / Portátil) │
                        └────────────┬────────────┘
                                     │
                           Red privada Tailscale
                                     │
                          HTTPS (Tailscale Serve)
                                     │
                              Traefik Ingress
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        │                            │                            │
┌───────────────┐          ┌────────────────┐          ┌─────────────────┐
│   JupyterLab  │          │  Code Server   │          │ Workspace Manager│
└───────────────┘          └───────┬────────┘          └─────────────────┘
                                   │
                            Continue Extension
                                   │
                                   ▼
                           ┌────────────────┐
                           │     Ollama     │
                           └────────────────┘

                 ───────────────────────────────────────
                      Kubernetes (k3s sobre WSL2)
                 ───────────────────────────────────────

                      Persistent Volume (PVC)
                               │
                     Workspace compartido
                               │
                       GPU NVIDIA del host
```

---

# Servicios

## Workspace Manager

Aplicación desarrollada en FastAPI que centraliza la gestión de la plataforma.

Actualmente permite:

- visualizar el estado del workspace;
- cambiar entre distintos modos de trabajo;
- iniciar y detener servicios;
- servir el dashboard web.

---

## JupyterLab

Entorno destinado a:

- entrenamiento de modelos;
- notebooks;
- análisis de datos;
- experimentación.

Workspace:

```text
/home/jovyan/work
```

---

## Code Server

Entorno de desarrollo basado en Visual Studio Code accesible desde cualquier navegador.

Incluye soporte para:

- Python
- Git
- Continue
- desarrollo remoto

Workspace:

```text
/home/coder/work
```

---

## Ollama

Servidor de modelos de lenguaje ejecutándose dentro del clúster Kubernetes.

Actualmente utilizado por:

- Continue
- futuras aplicaciones IA de la plataforma

---

## Continue

Asistente de programación integrado en Code Server y conectado a Ollama para disponer de un copiloto completamente local.

---

# Tecnologías

- Windows 11
- WSL2
- Ubuntu 24.04
- Kubernetes
- k3s
- containerd
- NVIDIA Container Toolkit
- NVIDIA Device Plugin
- Traefik
- FastAPI
- JupyterLab
- Code Server
- Ollama
- Continue
- PyTorch
- Tailscale

---

# Estructura del repositorio

```text
.
├── apps/
│   ├── code-server/
│   ├── jupyter/
│   ├── ollama/
│   └── workspace-manager/
│
├── infrastructure/
│   ├── gpu/
│   └── k3s/
│
├── scripts/
│
├── docs/
│
├── .gitignore
└── README.md
```

---

# Acceso remoto

La plataforma únicamente es accesible desde dispositivos pertenecientes a la red privada de Tailscale.

Las aplicaciones se publican mediante HTTPS utilizando Tailscale Serve.

Actualmente se exponen:

| Servicio | Ruta |
|----------|------|
| JupyterLab | `/` |
| Code Server | `/code/` |
| Workspace Manager | `/workspace/` |

No existe ninguna aplicación expuesta directamente a Internet.

---

# Estado actual

Actualmente la plataforma permite:

- Ejecutar Kubernetes con soporte GPU.
- Entrenar modelos desde JupyterLab.
- Desarrollar aplicaciones desde Code Server.
- Utilizar asistentes de programación locales mediante Continue.
- Ejecutar modelos LLM con Ollama.
- Compartir el mismo workspace entre Jupyter y Code Server.
- Gestionar el entorno desde un dashboard web.
- Acceder de forma segura desde cualquier lugar mediante Tailscale.

---

# Roadmap

## Infraestructura

- [x] k3s
- [x] GPU NVIDIA
- [x] Almacenamiento persistente
- [x] Traefik
- [x] Tailscale

## Entornos de trabajo

- [x] JupyterLab
- [x] Code Server
- [x] Continue

## Inteligencia Artificial

- [x] Ollama
- [x] Workspace Manager
- [x] Dashboard web
- [ ] Gestión automática de modelos
- [ ] Integración con MLflow
- [ ] Catálogo de modelos
- [ ] Gestión de experimentos

## Observabilidad

- [ ] Prometheus
- [ ] Grafana
- [ ] Monitorización de GPU

## Automatización

- [ ] GitHub Actions
- [ ] Despliegue automático
- [ ] Configuración automática de Continue

---

# Seguridad

- No existen servicios expuestos directamente a Internet.
- Todo el acceso se realiza mediante la red privada de Tailscale.
- HTTPS proporcionado por Tailscale Serve.
- Los secretos se almacenan mediante Kubernetes Secrets.
- Ninguna credencial se almacena en el repositorio.

---

# Licencia

Proyecto desarrollado con fines educativos y como laboratorio personal para aprender Kubernetes, Cloud Computing e Inteligencia Artificial.

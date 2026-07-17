#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${ROOT_DIR}"

echo "========================================"
echo " Cloud AI Workspace"
echo " Instalación de la plataforma"
echo "========================================"
echo

echo "=== 1/4 Instalando k3s ==="
"${ROOT_DIR}/infrastructure/k3s/install-k3s.sh"

echo
echo "=== 2/4 Configurando GPU NVIDIA ==="
"${ROOT_DIR}/infrastructure/gpu/install-gpu.sh"

echo
echo "=== 3/4 Desplegando JupyterLab ==="
"${ROOT_DIR}/scripts/deploy-jupyter.sh"

echo
echo "=== 4/4 Desplegando code-server ==="
"${ROOT_DIR}/scripts/deploy-code-server.sh"

echo
echo "=== Estado final ==="
"${ROOT_DIR}/scripts/status.sh"

echo
echo "========================================"
echo " Instalación completada"
echo "========================================"

#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo
echo "=========================================="
echo " Cloud AI Workspace installation"
echo "=========================================="
echo

echo "[1/3] Installing k3s..."
"$ROOT_DIR/infrastructure/k3s/install-k3s.sh"

echo
echo "[2/3] Configuring NVIDIA GPU support..."
"$ROOT_DIR/scripts/install-gpu.sh"

echo
echo "[3/3] Deploying JupyterLab..."
"$ROOT_DIR/scripts/deploy-jupyter.sh"

echo
echo "=========================================="
echo " Installation completed successfully"
echo "=========================================="
echo

"$ROOT_DIR/scripts/status.sh"

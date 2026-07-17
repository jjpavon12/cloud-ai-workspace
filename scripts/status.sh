#!/usr/bin/env bash

set -euo pipefail

NAMESPACE="jupyter"

echo "========================================"
echo " Cloud AI Workspace - Estado"
echo "========================================"

echo
echo "=== Nodo Kubernetes ==="
kubectl get nodes -o wide

echo
echo "=== GPU disponible ==="
kubectl get nodes \
  -o custom-columns="NODE:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu"

echo
echo "=== Pods ==="
kubectl get pods -n "${NAMESPACE}" -o wide

echo
echo "=== Servicios ==="
kubectl get services -n "${NAMESPACE}"

echo
echo "=== Ingress ==="
kubectl get ingress -n "${NAMESPACE}"

echo
echo "=== Almacenamiento ==="
kubectl get pvc -n "${NAMESPACE}"

echo
echo "=== Aplicaciones ==="
echo "JupyterLab:"
echo "  https://jprlab.tail1a7a0b.ts.net/"
echo
echo "VS Code:"
echo "  https://jprlab.tail1a7a0b.ts.net/code/"

echo
echo "========================================"

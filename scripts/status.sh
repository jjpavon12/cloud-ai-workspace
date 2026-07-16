#!/bin/bash
set -e

echo "=== Kubernetes node ==="
kubectl get nodes

echo
echo "=== GPU ==="
GPU_COUNT="$(kubectl get node \
  -o jsonpath='{.items[0].status.allocatable.nvidia\.com/gpu}' 2>/dev/null || true)"

echo "Available GPUs: ${GPU_COUNT:-0}"

echo
echo "=== JupyterLab ==="
kubectl get pods,svc,ingress,pvc -n jupyter 2>/dev/null \
  || echo "JupyterLab is not deployed."

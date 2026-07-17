#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_MANIFEST="$ROOT_DIR/infrastructure/gpu/nvidia-device-plugin.yaml"

echo "Adding NVIDIA Container Toolkit repository..."

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | sudo gpg --dearmor --yes \
    -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -sL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list >/dev/null

echo "Installing NVIDIA Container Toolkit..."

sudo apt update
sudo apt install -y nvidia-container-toolkit

echo "Restarting k3s so it detects the NVIDIA runtime..."

sudo systemctl restart k3s

echo "Waiting for Kubernetes..."
kubectl wait --for=condition=Ready node --all --timeout=180s

echo "Checking NVIDIA RuntimeClass..."

if ! kubectl get runtimeclass nvidia >/dev/null 2>&1; then
    echo "Error: NVIDIA RuntimeClass was not detected."
    exit 1
fi

echo "Deploying NVIDIA Device Plugin..."

kubectl apply -f "$PLUGIN_MANIFEST"

echo "Waiting for NVIDIA Device Plugin..."

kubectl rollout status daemonset/nvidia-device-plugin-daemonset \
  --namespace kube-system \
  --timeout=180s

GPU_COUNT="$(
  kubectl get nodes \
    -o jsonpath='{.items[0].status.allocatable.nvidia\.com/gpu}'
)"

if [[ -z "$GPU_COUNT" || "$GPU_COUNT" == "0" ]]; then
    echo "Error: Kubernetes did not detect any NVIDIA GPU."
    exit 1
fi

echo
echo "NVIDIA GPU support configured successfully."
echo "Available GPUs: $GPU_COUNT"

#!/bin/bash
set -e

echo "Installing k3s..."
curl -sfL https://get.k3s.io | sh -

echo "Configuring kubectl..."
mkdir -p "$HOME/.kube"
sudo cp /etc/rancher/k3s/k3s.yaml "$HOME/.kube/config"
sudo chown "$(id -u):$(id -g)" "$HOME/.kube/config"
chmod 600 "$HOME/.kube/config"

echo "Waiting for the Kubernetes node..."
kubectl wait --for=condition=Ready node --all --timeout=120s

echo
kubectl get nodes

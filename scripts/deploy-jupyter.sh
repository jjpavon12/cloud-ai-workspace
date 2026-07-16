#!/bin/bash
set -euo pipefail

NAMESPACE="jupyter"
SECRET_NAME="jupyter-auth"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Creating namespace..."
kubectl create namespace "$NAMESPACE" \
  --dry-run=client \
  -o yaml | kubectl apply -f -

if kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" >/dev/null 2>&1; then
    echo "Jupyter token already exists."
else
    JUPYTER_TOKEN="$(openssl rand -hex 16)"

    kubectl create secret generic "$SECRET_NAME" \
      --namespace "$NAMESPACE" \
      --from-literal=token="$JUPYTER_TOKEN"

    echo
    echo "Jupyter token:"
    echo "$JUPYTER_TOKEN"
    echo
    echo "Store it securely. It will not be shown again automatically."
fi

echo "Deploying JupyterLab..."
kubectl apply -f "$ROOT_DIR/apps/jupyter/deployment.yaml"
kubectl apply -f "$ROOT_DIR/apps/jupyter/ingress.yaml"

echo "Waiting for JupyterLab..."
kubectl rollout status deployment/jupyter \
  --namespace "$NAMESPACE" \
  --timeout=10m

echo
echo "JupyterLab deployed successfully."
echo
kubectl get pods,svc,ingress,pvc -n "$NAMESPACE"

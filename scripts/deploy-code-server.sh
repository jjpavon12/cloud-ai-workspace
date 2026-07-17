#!/usr/bin/env bash

set -euo pipefail

NAMESPACE="jupyter"
SECRET_NAME="code-server-auth"
DEPLOYMENT_NAME="code-server"

echo "=== Desplegando code-server ==="

kubectl create namespace "${NAMESPACE}" \
  --dry-run=client \
  -o yaml | kubectl apply -f -

if ! kubectl get secret "${SECRET_NAME}" \
  -n "${NAMESPACE}" >/dev/null 2>&1; then

  read -rsp "Introduce la contraseña de code-server: " CODE_PASSWORD
  echo

  if [[ -z "${CODE_PASSWORD}" ]]; then
    echo "Error: la contraseña no puede estar vacía."
    exit 1
  fi

  kubectl create secret generic "${SECRET_NAME}" \
    -n "${NAMESPACE}" \
    --from-literal=password="${CODE_PASSWORD}"

  unset CODE_PASSWORD

  echo "Secret creado."
else
  echo "El Secret ${SECRET_NAME} ya existe."
fi

kubectl apply -f apps/code-server/deployment.yaml
kubectl apply -f apps/code-server/ingress.yaml

echo "Esperando a que code-server esté disponible..."

kubectl rollout status \
  deployment/"${DEPLOYMENT_NAME}" \
  -n "${NAMESPACE}" \
  --timeout=180s

echo
echo "=== Estado ==="

kubectl get pods,svc,ingress,pvc \
  -n "${NAMESPACE}" \
  -l app=code-server 2>/dev/null || true

echo
echo "code-server disponible en:"
echo "https://jprlab.tail1a7a0b.ts.net/code/"

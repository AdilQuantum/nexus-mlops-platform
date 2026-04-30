#!/bin/bash

set -e  # stop on error

echo "🚀 Starting MLOps platform deployment..."



# Update kubeconfig
echo "🔗 Connecting to EKS..."
aws eks update-kubeconfig --region ap-south-1 --name nexus-mlops-cluster

cd ../../../..

# -----------------------------
# 2. Install ArgoCD
# -----------------------------
echo "⚙️ Installing ArgoCD..."
kubectl create namespace argocd || true

kubectl apply -n argocd \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo "⏳ Waiting for ArgoCD..."
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=300s

echo "✅ ArgoCD installed"

# -----------------------------
# 3. Deploy App via GitOps
# -----------------------------
echo "📦 Deploying GitOps application..."

kubectl apply -f k8s/argocd-app.yaml

echo "⏳ Waiting for sync..."
sleep 30

# -----------------------------
# 4. Install Monitoring
# -----------------------------
echo "📊 Installing Prometheus + Grafana..."

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

kubectl create namespace monitoring || true

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring

echo "⏳ Waiting for monitoring..."
sleep 60

echo "✅ Monitoring installed"

# -----------------------------
# 5. Deploy MLflow (GitOps already handles if in repo)
# -----------------------------
echo "🧠 MLflow will be deployed via ArgoCD sync..."

# -----------------------------
# 6. Final Status Check
# -----------------------------
echo "📌 Cluster status:"
kubectl get nodes
kubectl get pods -A

echo "🎉 Deployment complete!"
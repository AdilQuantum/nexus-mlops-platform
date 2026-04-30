Write-Host "🚀 Starting MLOps platform deployment..."



Write-Host "🔗 Connecting to EKS..."
aws eks update-kubeconfig --region ap-south-1 --name nexus-mlops-cluster

cd ../../../..

# -----------------------------
# 2. Install ArgoCD
# -----------------------------
Write-Host "⚙️ Installing ArgoCD..."

kubectl create namespace argocd 2>$null

kubectl apply -n argocd `
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=300s

Write-Host "✅ ArgoCD installed"

# -----------------------------
# 3. Deploy GitOps App
# -----------------------------
Write-Host "📦 Deploying ArgoCD App..."

kubectl apply -f k8s/argocd-app.yaml

Start-Sleep -Seconds 20

# -----------------------------
# 4. Monitoring
# -----------------------------
Write-Host "📊 Installing Prometheus + Grafana..."

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

kubectl create namespace monitoring 2>$null

helm install prometheus prometheus-community/kube-prometheus-stack `
  --namespace monitoring

Write-Host "⏳ Waiting for monitoring..."
Start-Sleep -Seconds 60

# -----------------------------
# 5. Status
# -----------------------------
Write-Host "📌 Cluster status:"
kubectl get nodes
kubectl get pods -A

Write-Host "🎉 Deployment complete!"
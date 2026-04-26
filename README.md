# Nexus Secure MLOps Platform

A production-grade, zero-trust ML inference platform on AWS EKS with 
automated drift detection, GitOps-native model deployment, and 
compliance-ready DevSecOps pipeline.

## Architecture

Developer pushes code → GitHub Actions CI/CD → Security Gates 
(Trivy + SonarQube + OWASP) → Docker build + Cosign sign → 
AWS ECR → ArgoCD GitOps → Argo Rollouts canary → EKS cluster → 
FastAPI inference → Prometheus + Grafana → Evidently drift detection → 
Airflow retraining → MLflow registry → Self-healing ML system

## Tech Stack

### Infrastructure
- Terraform (modular IaC)
- AWS EKS (Kubernetes)
- AWS VPC, RDS, S3, ECR
- IRSA (pod-level IAM)

### CI/CD & GitOps
- GitHub Actions
- ArgoCD (GitOps delivery)
- Argo Rollouts (canary deployments)

### ML Layer
- MLflow (experiment tracking + model registry)
- FastAPI (inference serving)
- Apache Airflow (retraining pipeline)
- Evidently AI (drift detection)

### Security
- Trivy (container scanning)
- OWASP dependency check
- OPA Gatekeeper (policy-as-code)
- Falco (runtime threat detection)
- Network Policies (namespace isolation)

### Observability
- Prometheus (custom ML metrics)
- Grafana (platform SLO + model performance)

## Key Engineering Decisions

- **Spot instances over on-demand** — 60-70% cost reduction
  for non-critical workloads
- **NAT instance over NAT Gateway** — $28/month savings
  for dev environment
- **IRSA over node-level IAM** — least privilege at pod level,
  not cluster level
- **Argo Rollouts canary** — automatic rollback if Prometheus
  quality gate breaches threshold
- **Evidently AI drift detection** — KS test + PSI running
  every 6 hours as K8s CronJob
- **Champion-challenger model gate** — new model must beat
  production baseline F1 before promotion

## Project Structure

\`\`\`
nexus-mlops-platform/
├── infrastructure/
│   ├── modules/          # Reusable Terraform modules
│   └── environments/     # Staging + Production configs
├── ml/
│   ├── training/         # Model training + MLflow
│   ├── inference/        # FastAPI serving + Dockerfile
│   └── drift/            # Evidently drift detection
├── gitops/
│   ├── apps/             # ArgoCD applications
│   └── rollouts/         # Argo Rollouts canary config
├── security/
│   ├── opa-policies/     # OPA Gatekeeper policies
│   ├── network-policies/ # Kubernetes network isolation
│   └── falco-rules/      # Runtime threat detection
└── observability/
    ├── dashboards/       # Grafana dashboard configs
    └── alerts/           # Prometheus alert rules
\`\`\`

## Local Setup

\`\`\`bash
# Prerequisites
terraform >= 1.10.0
aws cli configured
kubectl installed

# Deploy staging
cd infrastructure/environments/staging
terraform init
terraform plan
terraform apply
\`\`\`
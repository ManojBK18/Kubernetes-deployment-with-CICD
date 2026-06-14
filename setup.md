# Environment Setup Guide

This document provides step-by-step instructions to deploy the URL Shortener application on Amazon EKS.

---

# Prerequisites

Install the following tools:

| Tool    | Purpose                    |
| ------- | -------------------------- |
| AWS CLI | AWS Management             |
| kubectl | Kubernetes CLI             |
| eksctl  | EKS Cluster Management     |
| Docker  | Containerization           |
| Git     | Source Control             |
| Helm    | Kubernetes Package Manager |

Verify installations:

```bash
aws --version
kubectl version --client
eksctl version
docker --version
helm version
```

---

# AWS Configuration

Configure AWS credentials:

```bash
aws configure
```

Provide:

```text
AWS Access Key ID
AWS Secret Access Key
Region (ap-south-1)
Output Format (json)
```

Verify:

```bash
aws sts get-caller-identity
```

---

# Clone Repository

```bash
git clone https://github.com/<username>/url-shortener.git

cd url-shortener
```

---

# Build Docker Image

Build application image:

```bash
docker build -t url-shortener .
```

Verify:

```bash
docker images
```

Run locally:

```bash
docker run -p 8000:8000 url-shortener
```

Verify application:

```text
http://localhost:8000
```

---

# Push Image to Registry

Login:

```bash
docker login
```

Tag image:

```bash
docker tag url-shortener username/url-shortener:v1
```

Push image:

```bash
docker push username/url-shortener:v1
```

---

# Create EKS Cluster

Create cluster:

```bash
eksctl create cluster \
--name url-shortener-cluster \
--region ap-south-1 \
--nodes 2 \
--node-type t3.medium
```

Cluster creation may take 15-20 minutes.

Verify:

```bash
kubectl get nodes
```

Expected:

```text
STATUS: Ready
```

---

# Verify Storage Class

Check available storage classes:

```bash
kubectl get storageclass
```

Expected:

```text
gp3 (default)
```

This StorageClass uses AWS EBS for persistent storage.

---

# Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

Verify:

```bash
kubectl get ns
```

---

# Create Image Pull Secret

Required when using private container images.

```bash
kubectl create secret docker-registry regcred \
--docker-username=<username> \
--docker-password=<password> \
--docker-email=<email> \
-n url-shortener
```

Verify:

```bash
kubectl get secret -n url-shortener
```

---

# Deploy PostgreSQL

Apply manifests:

```bash
kubectl apply -f k8s/postgres/
```

Verify:

```bash
kubectl get pods -n url-shortener
```

Check PVC:

```bash
kubectl get pvc -n url-shortener
```

Expected:

```text
STATUS: Bound
```

---

# Deploy Application

Apply deployment:

```bash
kubectl apply -f k8s/app/
```

Verify:

```bash
kubectl get deployments -n url-shortener

kubectl get pods -n url-shortener
```

Expected:

```text
READY 1/1
STATUS Running
```

---

# Verify Service

```bash
kubectl get svc -n url-shortener
```

Expected:

```text
ClusterIP
```

---

# Install NGINX Ingress Controller

Install:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```

Verify:

```bash
kubectl get pods -n ingress-nginx
```

Wait until all pods show:

```text
Running
```

---

# Deploy Ingress Resource

Apply:

```bash
kubectl apply -f k8s/ingress/
```

Verify:

```bash
kubectl get ingress -n url-shortener
```

---

# Verify Application

Check:

```bash
kubectl get all -n url-shortener
```

Verify:

* Pod status = Running
* Service created
* Ingress created
* PVC Bound

Access application using:

```text
http://<INGRESS-IP>
```

---

# Install ArgoCD

Create namespace:

```bash
kubectl create namespace argocd
```

Install ArgoCD:

```bash
kubectl apply -n argocd \
-f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Verify:

```bash
kubectl get pods -n argocd
```

All pods should be:

```text
Running
```

---

# Expose ArgoCD UI

Change service type:

```bash
kubectl edit svc argocd-server -n argocd
```

Update:

```yaml
spec:
  type: NodePort
```

Verify:

```bash
kubectl get svc -n argocd
```

Example:

```text
argocd-server NodePort
```

Access:

```text
https://<NODE-IP>:<NODEPORT>
```

---

# Retrieve ArgoCD Admin Password

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
-o jsonpath="{.data.password}" | base64 -d
```

Login:

```text
Username: admin
Password: <generated-password>
```

---

# Configure GitOps Repository

Create ArgoCD Application.

Point ArgoCD to:

```text
https://github.com/<username>/url-shortener-manifests
```

Configure:

* Repository URL
* Target Revision
* Path
* Destination Cluster
* Namespace

Sync application.

---

# GitHub Actions Setup

Create secrets in GitHub:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
SONAR_TOKEN
DOCKER_USERNAME
DOCKER_PASSWORD
```

Create workflow:

```text
.github/workflows/deploy.yml
```

Pipeline stages:

1. Checkout Code
2. Run Tests
3. SonarQube Scan
4. Build Docker Image
5. Push Docker Image

---

# Verification Checklist

Verify the following:

```bash
kubectl get nodes

kubectl get pods -A

kubectl get svc -A

kubectl get ingress -A

kubectl get pvc -A
```

Expected:

* Nodes Ready
* Pods Running
* PVC Bound
* Ingress Available
* Application Accessible
* ArgoCD Accessible

---

# Cleanup

Delete application:

```bash
kubectl delete namespace url-shortener
```

Delete ArgoCD:

```bash
kubectl delete namespace argocd
```

Delete EKS cluster:

```bash
eksctl delete cluster \
--name url-shortener-cluster \
--region ap-south-1
```

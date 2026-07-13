# URL Shortener — Multi-Service Kubernetes Application

[![Build Status](https://img.shields.io/badge/status-production--ready-green)](https://github.com)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 🎯 Project Overview

A complete multi-service URL Shortener application designed for learning Kubernetes networking, CI/CD, and microservices architecture with:

- **Frontend**: React 18 + Vite, served by Nginx
- **API Gateway**: Node.js + Express (single entry point for all API calls)
- **Shortener Service**: Python + FastAPI (generates short codes, reads/writes PostgreSQL, caches in Redis)
- **Analytics Service**: Python + FastAPI (records clicks, serves analytics data)
- **Cache**: Redis
- **Database**: PostgreSQL 15
- **Containerization**: Independent Docker images for all services
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions pipelines for each service

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Services](#-services)
- [Installation](#-installation)
- [Development](#-development)
- [Docker & Images](#-docker--images)
- [Kubernetes Deployment](#-kubernetes-deployment)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Frontend
```bash
cd frontend
npm install
npm run dev
```
- UI: http://localhost:5173

### API Gateway
```bash
cd api-gateway
npm install
npm run dev
```
- API: http://localhost:3000
- Health: http://localhost:3000/health

### Shortener Service
```bash
cd shortener-service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
- API: http://localhost:8000
- Health: http://localhost:8000/health

### Analytics Service
```bash
cd analytics-service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```
- API: http://localhost:8001
- Health: http://localhost:8001/health

### Redis & PostgreSQL (Docker)
```bash
# Redis
docker run -d --name redis -p 6379:6379 redis:alpine

# PostgreSQL
docker run -d \
  --name postgres \
  -e POSTGRES_DB=urlshortener \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15-alpine
```

---

## 🏗️ Architecture

### Service Diagram
```
┌─────────────────────────────────────────────────────────┐
│           Frontend (React + Vite, Port 5173)            │
│         Served by Nginx as static files (Port 80)       │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (via Ingress)
┌────────────────────────┴────────────────────────────────┐
│           API Gateway (Node.js, Port 3000)              │
│     Single entry point — routes to backend services     │
└───────────────┬─────────────────────┬───────────────────┘
                │ HTTP                │ HTTP
┌───────────────┴──────┐  ┌──────────┴──────────────────┐
│  Shortener Service   │  │     Analytics Service        │
│  (FastAPI, Port 8000)│  │     (FastAPI, Port 8001)     │
└───────┬──────┬───────┘  └──────────┬───────────────────┘
        │      │                     │
        │   ┌──┴──────────────────┐  │
        │   │   Redis (Port 6379) │  │
        │   │   URL cache layer   │  │
        │   └─────────────────────┘  │
        │                            │
┌───────┴────────────────────────────┴───────────────────┐
│              PostgreSQL 15 (Port 5432)                  │
│   urls table (shortener) + analytics table (clicks)    │
└────────────────────────────────────────────────────────┘
```

### Request Flow
```
User → Frontend (React)
         ↓  POST /shorten
     API Gateway :3000
         ↓                    ↓
  Shortener :8000       Analytics :8001
  (create code)         (record click)
         ↓
  Redis (cache) → PostgreSQL (persist)
```

### Independent Services
Each service operates independently with:
- ✅ **Separate Dockerfile** — Individual containerization
- ✅ **Dedicated pipeline** — Independent CI/CD
- ✅ **Own Kubernetes Deployment** — Isolated service management
- ✅ **Health endpoint** — Liveness & readiness probes ready

---

## 📦 Services

### Frontend (React + Vite + Nginx)
| Aspect | Details |
|--------|---------|
| **Language** | JavaScript (React 18) |
| **Build Tool** | Vite 5 |
| **Server** | Nginx (serves static build output) |
| **Port** | 5173 (dev) / 80 (nginx/production) |
| **Location** | `/frontend` |
| **Dockerfile** | `frontend/Dockerfile` |

### API Gateway (Node.js + Express)
| Aspect | Details |
|--------|---------|
| **Language** | Node.js 18 |
| **Framework** | Express 4 |
| **Role** | Routes `/shorten`, `/r/:code`, `/analytics/:code` to backend services |
| **Port** | 3000 |
| **Location** | `/api-gateway` |
| **Dockerfile** | `api-gateway/Dockerfile` |

### Shortener Service (Python + FastAPI)
| Aspect | Details |
|--------|---------|
| **Language** | Python 3.11 |
| **Framework** | FastAPI |
| **Storage** | PostgreSQL (persistent) + Redis (cache) |
| **Port** | 8000 |
| **Location** | `/shortener-service` |
| **Dockerfile** | `shortener-service/Dockerfile` |

### Analytics Service (Python + FastAPI)
| Aspect | Details |
|--------|---------|
| **Language** | Python 3.11 |
| **Framework** | FastAPI |
| **Storage** | PostgreSQL |
| **Port** | 8001 |
| **Location** | `/analytics-service` |
| **Dockerfile** | `analytics-service/Dockerfile` |

### Redis
| Aspect | Details |
|--------|---------|
| **Image** | redis:alpine |
| **Role** | Cache short URL codes (TTL: 1 hour) |
| **Port** | 6379 |

### PostgreSQL 15
| Aspect | Details |
|--------|---------|
| **Image** | postgres:15-alpine |
| **Database** | urlshortener |
| **Tables** | `urls` (shortener), `analytics` (clicks) |
| **Port** | 5432 |
| **Storage** | PersistentVolumeClaim (K8s) |

---

## 🛠️ Installation

### Prerequisites

**System Requirements:**
- Docker 20.10+
- kubectl 1.24+
- Git 2.30+

**Frontend Requirements:**
- Node.js 18+
- npm 9+

**Backend Requirements:**
- Python 3.11+
- pip 23+

### Clone Repository
```bash
git clone <your-repo-url>
cd url-shortener
```

### Verify Project Structure
```bash
tree -L 2
```

---

## 💻 Development

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### API Gateway Development
```bash
cd api-gateway

# Install dependencies
npm install

# Start with nodemon (hot reload)
npm run dev

# Start production
npm start
```

### Shortener Service Development
```bash
cd shortener-service

# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Analytics Service Development
```bash
cd analytics-service

# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### API Endpoints

**Shorten a URL:**
```bash
curl -X POST http://localhost:3000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com/search?q=kubernetes"}'
```

**Redirect via short code:**
```bash
curl -L http://localhost:3000/r/abc123
```

**Get analytics:**
```bash
curl http://localhost:3000/analytics/abc123
```

**Health checks:**
```bash
curl http://localhost:3000/health    # API Gateway
curl http://localhost:8000/health   # Shortener Service
curl http://localhost:8001/health   # Analytics Service
```

---

## 🐳 Docker & Images

### Building Docker Images

**Frontend:**
```bash
docker build -t url-shortener-frontend:v1.0 ./frontend
```

**API Gateway:**
```bash
docker build -t url-shortener-api-gateway:v1.0 ./api-gateway
```

**Shortener Service:**
```bash
docker build -t url-shortener-shortener:v1.0 ./shortener-service
```

**Analytics Service:**
```bash
docker build -t url-shortener-analytics:v1.0 ./analytics-service
```

### Push to Docker Hub
```bash
REGISTRY=your-dockerhub-username

docker tag url-shortener-frontend:v1.0     $REGISTRY/url-shortener-frontend:v1.0
docker tag url-shortener-api-gateway:v1.0  $REGISTRY/url-shortener-api-gateway:v1.0
docker tag url-shortener-shortener:v1.0    $REGISTRY/url-shortener-shortener:v1.0
docker tag url-shortener-analytics:v1.0    $REGISTRY/url-shortener-analytics:v1.0

docker push $REGISTRY/url-shortener-frontend:v1.0
docker push $REGISTRY/url-shortener-api-gateway:v1.0
docker push $REGISTRY/url-shortener-shortener:v1.0
docker push $REGISTRY/url-shortener-analytics:v1.0
```

---

## ☸️ Kubernetes Deployment

### Prerequisites
- Kubernetes cluster running (Minikube / EKS / AKS / GKE)
- NGINX Ingress Controller installed
- Docker registry credentials configured

### Deploy All Services
```bash
# Create namespace
kubectl apply -f k8s/01-namespace.yml

# Secrets & ConfigMaps
kubectl apply -f k8s/02-configmap.yml
kubectl apply -f k8s/03-secrets.yml

# PostgreSQL
kubectl apply -f k8s/04-postgres-pvc.yml
kubectl apply -f k8s/05-postgres-deployment.yml

# Redis
kubectl apply -f k8s/06-redis-deployment.yml

# Backend services
kubectl apply -f k8s/07-shortener-deployment.yml
kubectl apply -f k8s/08-analytics-deployment.yml
kubectl apply -f k8s/09-api-gateway-deployment.yml

# Frontend
kubectl apply -f k8s/10-frontend-deployment.yml

# Ingress
kubectl apply -f k8s/11-ingress.yml
```

### Environment Variables (K8s)

#### API Gateway
| Variable | K8s Value |
|----------|-----------|
| `SHORTENER_SERVICE_URL` | `http://shortener-service:8000` |
| `ANALYTICS_SERVICE_URL` | `http://analytics-service:8001` |

#### Shortener & Analytics Services
| Variable | Source |
|----------|--------|
| `POSTGRES_HOST` | ConfigMap → `postgres-service` |
| `POSTGRES_DB` | ConfigMap → `urlshortener` |
| `POSTGRES_USER` | Secret |
| `POSTGRES_PASSWORD` | Secret |
| `REDIS_HOST` | ConfigMap → `redis-service` |
| `PGDATA` | `/var/lib/postgresql/data/pgdata` |

> **Note:** `PGDATA` must point to a subdirectory of the PVC mount to avoid the `lost+found` initdb error.

### Verify Deployment
```bash
# Check all pods
kubectl get pods -n url-shortener

# Check services
kubectl get svc -n url-shortener

# Check ingress
kubectl get ingress -n url-shortener

# Check endpoints
kubectl get endpoints -n url-shortener

# Pod resource usage
kubectl top pods -n url-shortener

# View events
kubectl get events -n url-shortener --sort-by='.lastTimestamp'
```

### Kubernetes Concepts Covered
- **Namespace** — isolate all resources under `url-shortener`
- **Deployments** — one per service, with replica management
- **ClusterIP Services** — internal service-to-service DNS resolution
- **Ingress** — external traffic routing to frontend and api-gateway
- **ConfigMaps** — non-sensitive config (hosts, ports, DB name)
- **Secrets** — DB credentials, Docker registry credentials
- **PersistentVolumeClaim** — PostgreSQL data persistence
- **Liveness & Readiness Probes** — health checks via `/health` endpoints
- **HPA** — auto-scaling based on CPU/memory

### Cleanup
```bash
kubectl delete namespace url-shortener
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions — Independent Pipelines

Each service has its own pipeline triggered on push to `main`:

#### Frontend Pipeline
**Stages:** Checkout → Install → Build → Docker Build → Push → Deploy

#### API Gateway Pipeline
**Stages:** Checkout → Install → Docker Build → Push → Deploy

#### Shortener Service Pipeline
**Stages:** Checkout → Install → Docker Build → Push → Deploy

#### Analytics Service Pipeline
**Stages:** Checkout → Install → Docker Build → Push → Deploy

### Required GitHub Secrets
```
DOCKER_USERNAME       — Docker Hub username
DOCKER_PASSWORD       — Docker Hub password
KUBECONFIG            — Kubernetes cluster config
```

---

## 📁 Project Structure

```
url-shortener/
├── frontend/                       # React + Vite app
│   ├── src/
│   │   ├── App.jsx                 # Main component
│   │   └── main.jsx                # Entry point
│   ├── index.html
│   ├── vite.config.js
│   ├── nginx.conf                  # Nginx static file server
│   ├── Dockerfile
│   └── package.json
│
├── api-gateway/                    # Node.js Express gateway
│   ├── index.js                    # Route definitions
│   ├── Dockerfile
│   └── package.json
│
├── shortener-service/              # Python FastAPI
│   ├── main.py                     # Shorten + resolve endpoints
│   ├── Dockerfile
│   └── requirements.txt
│
├── analytics-service/              # Python FastAPI
│   ├── main.py                     # Click recording + analytics
│   ├── Dockerfile
│   └── requirements.txt
│
├── k8s/                            # Kubernetes manifests
│   ├── 01-namespace.yml
│   ├── 02-configmap.yml
│   ├── 03-secrets.yml
│   ├── 04-postgres-pvc.yml
│   ├── 05-postgres-deployment.yml
│   ├── 06-redis-deployment.yml
│   ├── 07-shortener-deployment.yml
│   ├── 08-analytics-deployment.yml
│   ├── 09-api-gateway-deployment.yml
│   ├── 10-frontend-deployment.yml
│   └── 11-ingress.yml
│
├── .github/
│   └── workflows/                  # GitHub Actions pipelines
│       ├── frontend.yml
│       ├── api-gateway.yml
│       ├── shortener.yml
│       └── analytics.yml
│
└── README.md
```

---

## 🐛 Troubleshooting

### Frontend Issues
```bash
# Port in use
lsof -i :5173
kill -9 <PID>

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### PostgreSQL initdb Error (lost+found)
```yaml
# Set PGDATA to a subdirectory of the PVC mount
- name: PGDATA
  value: "/var/lib/postgresql/data/pgdata"
```

### 503 Service Unavailable (Ingress)
```bash
# Check pod status
kubectl get pods -n url-shortener

# Check if service selectors match pod labels
kubectl get endpoints -n url-shortener

# Check pod logs
kubectl logs <pod-name> -n url-shortener
```

### 405 Method Not Allowed on /shorten
- Ingress is not routing `/shorten` to the api-gateway service
- Check your Ingress manifest paths and backend service names

### Pod Probes Not Working
```bash
# Confirm probes are correctly indented under the container spec
kubectl describe pod <pod-name> -n url-shortener
# Look for "Liveness" and "Readiness" — if <none>, indentation is wrong in YAML
```

### Kubernetes Pod Issues
```bash
# Full pod details
kubectl describe pod <pod-name> -n url-shortener

# Live logs
kubectl logs -f <pod-name> -n url-shortener

# Recent events
kubectl get events -n url-shortener --sort-by='.lastTimestamp'

# Delete and let Deployment recreate
kubectl delete pod <pod-name> -n url-shortener
```

---

## 🔐 Security

✅ **Health Checks** — Liveness & readiness probes on all services  
✅ **Secret Management** — Kubernetes Secrets for DB credentials  
✅ **Non-root ready** — Dockerfile best practices  
✅ **Redis TTL** — Short URL cache expires after 1 hour  
✅ **Input passed through FastAPI Pydantic** — Request validation  

---

## 📈 Performance & Scaling

### Resource Limits (recommended)
```
Frontend:          Memory: 128Mi–256Mi,  CPU: 100m–250m
API Gateway:       Memory: 256Mi–512Mi,  CPU: 100m–250m
Shortener Service: Memory: 256Mi–512Mi,  CPU: 100m–250m
Analytics Service: Memory: 256Mi–512Mi,  CPU: 100m–250m
Redis:             Memory: 128Mi–256Mi,  CPU: 100m–200m
PostgreSQL:        Memory: 512Mi–1Gi,    CPU: 250m–500m
```

### HPA (Auto-scaling)
- **Frontend**: 1–5 replicas (CPU > 70%)
- **API Gateway**: 1–5 replicas (CPU > 70%)
- **Shortener**: 1–5 replicas (CPU > 70%)
- **Analytics**: 1–5 replicas (CPU > 70%)
- **PostgreSQL**: 1 replica (stateful)
- **Redis**: 1 replica (stateful)

---

## 🚀 Production Deployment Checklist

- [ ] Kubernetes cluster operational
- [ ] NGINX Ingress Controller installed
- [ ] Docker registry credentials configured as K8s Secret
- [ ] GitHub Actions secrets configured
- [ ] Namespace created (`url-shortener`)
- [ ] ConfigMaps and Secrets applied
- [ ] PersistentVolumeClaim provisioned for PostgreSQL
- [ ] `PGDATA` set to subdirectory of PVC mount
- [ ] All Deployments running and pods `Ready`
- [ ] Ingress routes verified (`/` → frontend, `/shorten` → api-gateway)
- [ ] Liveness & readiness probes confirmed in `kubectl describe pod`
- [ ] HPA configured for stateless services

---

## 📄 License

MIT License — see LICENSE file

---

## 🎯 Version

**v1.0.0** (Current)
- ✅ Frontend Service (React + Vite + Nginx)
- ✅ API Gateway (Node.js + Express)
- ✅ Shortener Service (Python + FastAPI)
- ✅ Analytics Service (Python + FastAPI)
- ✅ Redis Cache Layer
- ✅ PostgreSQL Persistent Storage
- ✅ Independent Docker Images
- ✅ Kubernetes Manifests
- ✅ GitHub Actions CI/CD Pipelines

**Status:** Production Ready ✅

---

**Last Updated:** 2026  
**Environment:** Kubernetes 1.24+ | Docker 20.10+ | Node.js 18+ | Python 3.11+

---

## 🎉 Thank You!

This project is built for hands-on Kubernetes and CI/CD learning. Every service, manifest, and pipeline is intentionally kept simple and readable so you can understand each moving part clearly. Happy shipping! 🚀

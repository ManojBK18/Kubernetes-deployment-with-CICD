# URL Shortener — Kubernetes Learning Project

A multi-service URL shortener app designed for learning Kubernetes networking, deployments, and CI/CD.

## Services

| Service            | Tech                  | Port  | Purpose                                      |
|--------------------|-----------------------|-------|----------------------------------------------|
| frontend           | React + Vite          | 5173  | User interface                               |
| api-gateway        | Node.js + Express     | 3000  | Single entry point, routes to backend        |
| shortener-service  | Python + FastAPI      | 8000  | Generates short codes, reads/writes Postgres |
| analytics-service  | Python + FastAPI      | 8001  | Records clicks, serves analytics data        |
| Redis              | Redis                 | 6379  | Cache layer for fast URL resolution          |
| PostgreSQL         | PostgreSQL            | 5432  | Persistent storage for URLs and clicks       |

## Project Structure

```
url-shortener/
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── api-gateway/
│   ├── index.js
│   └── package.json
├── shortener-service/
│   ├── main.py
│   └── requirements.txt
├── analytics-service/
│   ├── main.py
│   └── requirements.txt
└── README.md
```

## Request Flow

```
User → Frontend (React)
         ↓
     API Gateway (Node.js) :3000
         ↓               ↓
  Shortener Service   Analytics Service
   (FastAPI) :8000      (FastAPI) :8001
         ↓                   ↓
       Redis              PostgreSQL
   (cache) :6379        (storage) :5432
```

## Environment Variables

### api-gateway
| Variable                | Default               | K8s Value (example)                        |
|-------------------------|-----------------------|--------------------------------------------|
| SHORTENER_SERVICE_URL   | http://localhost:8000 | http://shortener-service:8000              |
| ANALYTICS_SERVICE_URL   | http://localhost:8001 | http://analytics-service:8001              |

### shortener-service & analytics-service
| Variable          | Default     | Description              |
|-------------------|-------------|--------------------------|
| POSTGRES_HOST     | localhost   | K8s: postgres-service    |
| POSTGRES_PORT     | 5432        |                          |
| POSTGRES_DB       | urlshortener|                          |
| POSTGRES_USER     | admin       | Use K8s Secret           |
| POSTGRES_PASSWORD | password    | Use K8s Secret           |
| REDIS_HOST        | localhost   | K8s: redis-service       |
| REDIS_PORT        | 6379        |                          |

## K8s Concepts You'll Practice

- **Deployments** — one per service
- **ClusterIP Services** — internal service-to-service communication
- **Ingress** — expose frontend and api-gateway externally
- **ConfigMaps** — non-sensitive env vars (hosts, ports, DB name)
- **Secrets** — DB credentials
- **PersistentVolumeClaims** — PostgreSQL data persistence
- **Liveness & Readiness Probes** — every service has a `/health` endpoint
- **Inter-pod DNS** — e.g. `http://shortener-service.default.svc.cluster.local:8000`

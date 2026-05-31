# GitOps Platform con IA

Pipeline GitOps de nivel producción con Policy-as-Code, Security Scanning automatizado y arquitectura lista para un Agente de IA autónomo.

## ¿Qué hace este proyecto?
git push → GitHub Actions construye imagen Docker
→ Trivy escanea CVEs
→ OPA/Conftest valida políticas de seguridad
→ ArgoCD despliega automáticamente en Kubernetes
→ selfHeal: cualquier cambio manual se revierte
## Stack

| Capa | Tecnología |
|---|---|
| GitOps | ArgoCD |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry (GHCR) |
| Seguridad | Trivy + OPA/Conftest |
| Orquestación | Kubernetes (kind) |
| IaC | Terraform (Fase siguiente) |
| Agente IA | AWS Lambda + Groq (Fase siguiente) |

## Fases completadas

- [x] Fase 1 — Fundación GitOps: app Flask + Docker + manifiestos K8s
- [x] Fase 2 — Escaneo de seguridad con Trivy
- [x] Fase 3 — Policy as Code con OPA/Conftest
- [x] Fase 4 — Despliegue automático con ArgoCD
- [ ] Fase 5 — Agente IA con AWS Lambda + Groq

## Arrancar el proyecto

```bash
# 1. Crear cluster
kind create cluster --name gitops-platform

# 2. Instalar ArgoCD
helm install argocd argo/argo-cd --namespace default

# 3. Desplegar la aplicación
kubectl apply -f argocd-app.yaml

# 4. Acceder a ArgoCD
kubectl port-forward service/argocd-server -n default 8080:443
```

## Pipeline de seguridad

Cada PR pasa por estas puertas automáticamente:
PR abierto
├── Trivy scan      → CVEs en código y dependencias
├── OPA/Conftest    → valida manifiestos K8s contra políticas
└── Si falla CRITICAL → merge bloqueado

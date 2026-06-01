# 🚀 GitOps Platform con IA

Pipeline GitOps de nivel producción con Policy-as-Code, Security Scanning automatizado y un Agente de IA autónomo que detecta vulnerabilidades y abre Pull Requests de remediación sin intervención humana.

## ¿Qué hace este proyecto?
git push
→ GitHub Actions construye imagen Docker → GHCR
→ Trivy escanea CVEs automáticamente
→ OPA/Conftest valida políticas de seguridad
→ ArgoCD despliega en Kubernetes (selfHeal)
→ AI Agent analiza CVEs con Groq y abre PR con reporte
Todo en menos de 2 minutos
## 🏗️ Arquitectura
Developer
└── git push → GitHub
├── CI Pipeline
│     └── Build imagen Docker → GHCR
└── Security Pipeline
├── Trivy → escaneo CVEs → GitHub Security Tab
├── OPA/Conftest → valida manifiestos K8s
└── AI Agent → Groq Llama 3.3 70B → PR automático
↓
ArgoCD
└── Despliega en kind (Kubernetes)
## 🛠️ Stack Tecnológico

| Capa | Tecnología | Propósito |
|---|---|---|
| GitOps | ArgoCD | Sincronización Git → Cluster |
| CI/CD | GitHub Actions | Pipeline automatizado |
| Registry | GHCR | Imágenes Docker |
| Seguridad | Trivy + OPA/Conftest | CVEs + Policy as Code |
| Orquestación | Kubernetes (kind) | Despliegue local |
| Agente IA | Python + Groq | Análisis autónomo de CVEs |
| Modelo IA | Llama 3.3 70B | Análisis y recomendaciones |

## 🔒 Pipeline de Seguridad

Cada push pasa por estas puertas automáticamente:
PR abierto
├── Trivy Scan       → CVEs en código y dependencias
├── OPA/Conftest     → valida manifiestos K8s contra políticas
│     ├── No imagen con tag latest
│     ├── Resource limits obligatorios
│     ├── runAsNonRoot requerido
│     └── No LoadBalancer en local
└── Si falla CRITICAL → pipeline bloqueado
## 🤖 Agente de Seguridad IATrivy detecta CVEs
└── GitHub Actions ejecuta agent/ai_security_agent.py
└── Python llama a Groq API (Llama 3.3 70B)
└── IA analiza riesgo y genera recomendaciones
└── Se abre PR automáticamente con:
├── Análisis en lenguaje natural (español)
├── Nivel de riesgo (CRÍTICO/ALTO/MEDIO)
└── Fix recomendado paso a paso
Tiempo desde detección hasta PR: < 30 segundos

cat > README.md << 'EOF'
# 🚀 GitOps Platform con IA

Pipeline GitOps de nivel producción con Policy-as-Code, Security Scanning automatizado y un Agente de IA autónomo que detecta vulnerabilidades y abre Pull Requests de remediación sin intervención humana.

## ¿Qué hace este proyecto?
git push
→ GitHub Actions construye imagen Docker → GHCR
→ Trivy escanea CVEs automáticamente
→ OPA/Conftest valida políticas de seguridad
→ ArgoCD despliega en Kubernetes (selfHeal)
→ AI Agent analiza CVEs con Groq y abre PR con reporte
Todo en menos de 2 minutos
## 🏗️ Arquitectura
Developer
└── git push → GitHub
├── CI Pipeline
│     └── Build imagen Docker → GHCR
└── Security Pipeline
├── Trivy → escaneo CVEs → GitHub Security Tab
├── OPA/Conftest → valida manifiestos K8s
└── AI Agent → Groq Llama 3.3 70B → PR automático
↓
ArgoCD
└── Despliega en kind (Kubernetes)
## 🛠️ Stack Tecnológico

| Capa | Tecnología | Propósito |
|---|---|---|
| GitOps | ArgoCD | Sincronización Git → Cluster |
| CI/CD | GitHub Actions | Pipeline automatizado |
| Registry | GHCR | Imágenes Docker |
| Seguridad | Trivy + OPA/Conftest | CVEs + Policy as Code |
| Orquestación | Kubernetes (kind) | Despliegue local |
| Agente IA | Python + Groq | Análisis autónomo de CVEs |
| Modelo IA | Llama 3.3 70B | Análisis y recomendaciones |

## 🔒 Pipeline de Seguridad

Cada push pasa por estas puertas automáticamente:
PR abierto
├── Trivy Scan       → CVEs en código y dependencias
├── OPA/Conftest     → valida manifiestos K8s contra políticas
│     ├── No imagen con tag latest
│     ├── Resource limits obligatorios
│     ├── runAsNonRoot requerido
│     └── No LoadBalancer en local
└── Si falla CRITICAL → pipeline bloqueado
## 🤖 Agente de Seguridad IATrivy detecta CVEs
└── GitHub Actions ejecuta agent/ai_security_agent.py
└── Python llama a Groq API (Llama 3.3 70B)
└── IA analiza riesgo y genera recomendaciones
└── Se abre PR automáticamente con:
├── Análisis en lenguaje natural (español)
├── Nivel de riesgo (CRÍTICO/ALTO/MEDIO)
└── Fix recomendado paso a paso
Tiempo desde detección hasta PR: < 30 segundos


## 🚀 Arrancar el proyecto

### Requisitos
- Docker
- kind
- kubectl
- helm

### Levantar el entorno

```bash
# 1. Clonar el repo
git clone https://github.com/javisanz23/gitops-platform.git
cd gitops-platform

# 2. Crear cluster Kubernetes local
kind create cluster --name gitops-platform --config kind-config.yaml

# 3. Instalar ArgoCD
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm install argocd argo/argo-cd --namespace default --timeout 10m

# 4. Desplegar la aplicación
kubectl apply -f argocd-app.yaml

# 5. Acceder a ArgoCD
kubectl port-forward service/argocd-server -n default 8080:443
# Usuario: admin
# Contraseña: kubectl -n default get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

## 📁 Estructura del Repositorio
gitops-platform/
├── apps/demo-web/          # App Flask + Dockerfile
├── k8s/
│   ├── base/               # Manifiestos Kubernetes
│   └── overlays/dev/       # Configuración por entorno
├── policies/
│   ├── kubernetes/         # Políticas OPA para K8s (Rego)
│   └── terraform/          # Políticas OPA para Terraform
├── agent/                  # AI Security Agent (Python + Groq)
├── security-reports/       # Reportes generados por la IA
├── .github/workflows/
│   ├── ci.yaml             # Build y push Docker
│   └── security.yaml       # Trivy + OPA + AI Agent
├── argocd-app.yaml         # Application de ArgoCD
├── kind-config.yaml        # Configuración del cluster local
└── README.md
## ✅ Fases completadas

- [x] Fase 1 — Fundación GitOps: app Flask + Docker + manifiestos K8s
- [x] Fase 2 — Escaneo de seguridad con Trivy
- [x] Fase 3 — Policy as Code con OPA/Conftest
- [x] Fase 4 — Despliegue automático con ArgoCD + selfHeal
- [x] Fase 5 — Documentación
- [x] Fase 6 — AI Security Agent con Groq Llama 3.3 70B

## 📊 Resultados

| Métrica | Valor |
|---|---|
| Tiempo push → despliegue | < 2 minutos |
| Tiempo detección CVE → PR | < 30 segundos |
| Políticas de seguridad | 4 activas |
| Cobertura de escaneo | Código + IaC + manifiestos |
| Disponibilidad | 2 réplicas, selfHeal activo |

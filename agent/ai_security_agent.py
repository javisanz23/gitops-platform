import os
import json
import urllib.request
import urllib.error

def analyze_cve_with_groq(cve_data: str) -> str:
    """Llama a Groq API para analizar CVEs y generar fix."""
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY no configurada")

    prompt = f"""Eres un experto en seguridad DevOps. Analiza estos CVEs encontrados en una imagen Docker y proporciona:

1. Resumen del riesgo (1-2 frases)
2. Fix recomendado (comando exacto o cambio de versión)
3. Urgencia (CRÍTICA/ALTA/MEDIA)

CVEs encontrados:
{cve_data}

Responde en español, de forma concisa y accionable."""

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.1
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]


def create_github_pr(analysis: str, cve_summary: str) -> None:
    """Abre un PR en GitHub con el análisis de seguridad."""
    
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    
    if not token or not repo:
        print("GITHUB_TOKEN o GITHUB_REPOSITORY no configurados")
        return

    # Obtener el SHA del branch main
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/git/ref/heads/main",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    )
    
    with urllib.request.urlopen(req) as r:
        sha = json.loads(r.read())["object"]["sha"]

    # Crear branch nuevo
    branch_name = f"security/ai-fix-{os.environ.get('GITHUB_RUN_ID', 'manual')}"
    
    payload = json.dumps({
        "ref": f"refs/heads/{branch_name}",
        "sha": sha
    }).encode()
    
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/git/refs",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
    )
    
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        print(f"Branch ya existe o error: {e}")

    # Crear el PR
    pr_body = f"""## 🤖 Security Fix — Generado por AI Agent

### CVEs Detectados
{cve_summary}

### Análisis de la IA (Groq Llama 3.3 70B)
{analysis}

---
*Este PR fue generado automáticamente por el AI Security Agent.*
*Revisa los cambios antes de mergear.*
"""

    payload = json.dumps({
        "title": "🔒 [AI Security] Fix vulnerabilidades detectadas por Trivy",
        "body": pr_body,
        "head": branch_name,
        "base": "main",
        "labels": ["security", "automated", "ai-generated"]
    }).encode()

    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/pulls",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req) as r:
            pr = json.loads(r.read())
            print(f"✅ PR creado: {pr['html_url']}")
    except urllib.error.HTTPError as e:
        print(f"PR ya existe o error: {e.read().decode()}")


def main():
    # Leer el reporte de Trivy
    trivy_report = os.environ.get("TRIVY_REPORT", "")
    
    if not trivy_report:
        # Intentar leer del archivo
        try:
            with open("trivy-report.txt", "r") as f:
                trivy_report = f.read()
        except FileNotFoundError:
            trivy_report = "No se encontró reporte de Trivy"

    print("🔍 Analizando CVEs con Groq AI...")
    
    try:
        analysis = analyze_cve_with_groq(trivy_report)
        print(f"📋 Análisis completado:\n{analysis}")
        
        print("\n🔀 Creando PR con el fix...")
        create_github_pr(analysis, trivy_report[:500])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()

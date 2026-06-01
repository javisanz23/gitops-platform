import os
import json
import sys

def analyze_cve_with_groq(cve_data: str) -> str:
    try:
        import urllib.request
        
        api_key = os.environ.get("GROQ_API_KEY", "").strip()
        
        if not api_key:
            return "No se pudo obtener la API key de Groq"

        prompt = f"""Eres un experto en seguridad DevOps. Analiza estos CVEs y proporciona:
1. Resumen del riesgo
2. Fix recomendado
3. Urgencia (CRÍTICA/ALTA/MEDIA)

CVEs:
{cve_data[:1000]}

Responde en español de forma concisa."""

        payload = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            method="POST"
        )
        req.add_header("Authorization", f"Bearer {api_key}")
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
            
    except Exception as e:
        return f"Error llamando a Groq: {e}"


def create_security_report(analysis: str, cve_summary: str) -> None:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    
    if not token or not repo:
        print("Variables de entorno de GitHub no configuradas")
        return

    import urllib.request
    import urllib.error

    try:
        # Obtener SHA del branch main
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/git/ref/heads/main",
            method="GET"
        )
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/vnd.github.v3+json")

        with urllib.request.urlopen(req) as r:
            sha = json.loads(r.read())["object"]["sha"]

        branch_name = f"security/ai-fix-{os.environ.get('GITHUB_RUN_ID', 'manual')}"

        # Crear branch
        payload = json.dumps({"ref": f"refs/heads/{branch_name}", "sha": sha}).encode()
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/git/refs",
            data=payload,
            method="POST"
        )
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/vnd.github.v3+json")
        req.add_header("Content-Type", "application/json")

        try:
            urllib.request.urlopen(req)
        except urllib.error.HTTPError:
            pass

        # Crear PR
        pr_body = f"""## 🤖 Security Report — AI Agent

### Análisis de Seguridad (Groq Llama 3.3 70B)
{analysis}

### CVEs Detectados
---
*Generado automáticamente por el AI Security Agent*
"""
        payload = json.dumps({
            "title": "🔒 [AI Security] Reporte de vulnerabilidades",
            "body": pr_body,
            "head": branch_name,
            "base": "main"
        }).encode()

        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/pulls",
            data=payload,
            method="POST"
        )
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/vnd.github.v3+json")
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req) as r:
            pr = json.loads(r.read())
            print(f"✅ PR creado: {pr['html_url']}")

    except Exception as e:
        print(f"Error creando PR: {e}")


def main():
    trivy_report = ""
    try:
        with open("trivy-report.txt", "r") as f:
            trivy_report = f.read()
    except FileNotFoundError:
        trivy_report = "No se encontró reporte de Trivy - análisis general de seguridad"

    print("🔍 Analizando con Groq AI...")
    analysis = analyze_cve_with_groq(trivy_report)
    print(f"📋 Análisis:\n{analysis}")

    print("\n🔀 Creando reporte en GitHub...")
    create_security_report(analysis, trivy_report)


if __name__ == "__main__":
    main()

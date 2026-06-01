import os
import json
import subprocess
from datetime import datetime

def analyze_cve_with_groq(cve_data: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        return "No se pudo obtener la API key"

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": f"Analiza estos CVEs de seguridad y da un resumen del riesgo y fix recomendado en español:\n{cve_data[:500]}"}],
        "max_tokens": 300
    })

    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://api.groq.com/openai/v1/chat/completions",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", payload
    ], capture_output=True, text=True, timeout=30)

    try:
        data = json.loads(result.stdout)
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        return f"Respuesta inesperada: {result.stdout[:200]}"
    except json.JSONDecodeError:
        return f"Error parseando respuesta: {result.stdout[:200]}"


def create_pr_with_report(analysis: str, cve_data: str, token: str, repo: str, run_id: str) -> None:
    # Obtener SHA de main
    result = subprocess.run([
        "curl", "-s",
        f"https://api.github.com/repos/{repo}/git/ref/heads/main",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Accept: application/vnd.github.v3+json"
    ], capture_output=True, text=True)

    sha = json.loads(result.stdout)["object"]["sha"]
    branch = f"security/ai-report-{run_id}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Crear branch
    subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.github.com/repos/{repo}/git/refs",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Accept: application/vnd.github.v3+json",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"ref": f"refs/heads/{branch}", "sha": sha})
    ], capture_output=True)

    # Crear archivo de reporte en el branch
    report_content = f"""# Security Report — {timestamp}

## Análisis de IA (Groq Llama 3.3 70B)

{analysis}

## Datos del escaneo Trivy
---
*Generado automáticamente por el AI Security Agent*
*Run ID: {run_id}*
"""
    import base64
    content_b64 = base64.b64encode(report_content.encode()).decode()

    result = subprocess.run([
        "curl", "-s", "-X", "PUT",
        f"https://api.github.com/repos/{repo}/contents/security-reports/report-{run_id}.md",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Accept: application/vnd.github.v3+json",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "message": f"security: añadir reporte AI [{run_id}]",
            "content": content_b64,
            "branch": branch
        })
    ], capture_output=True, text=True)

    # Crear PR
    pr_body = f"""## 🤖 AI Security Report — {timestamp}

### Análisis (Groq Llama 3.3 70B)
{analysis}

---
*Generado automáticamente por el AI Security Agent*
"""
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.github.com/repos/{repo}/pulls",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Accept: application/vnd.github.v3+json",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "title": f"🔒 [AI Security] Reporte {timestamp}",
            "body": pr_body,
            "head": branch,
            "base": "main"
        })
    ], capture_output=True, text=True)

    try:
        pr = json.loads(result.stdout)
        if "html_url" in pr:
            print(f"✅ PR creado: {pr['html_url']}")
        else:
            print(f"Respuesta: {result.stdout[:300]}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    trivy_report = ""
    try:
        with open("trivy-report.txt", "r") as f:
            trivy_report = f.read()
    except FileNotFoundError:
        trivy_report = "Análisis general de seguridad"

    print("🔍 Analizando con Groq AI...")
    analysis = analyze_cve_with_groq(trivy_report)
    print(f"📋 Análisis:\n{analysis}")

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    run_id = os.environ.get("GITHUB_RUN_ID", "manual")

    if token and repo:
        print("\n🔀 Creando PR con reporte...")
        create_pr_with_report(analysis, trivy_report, token, repo, run_id)


if __name__ == "__main__":
    main()

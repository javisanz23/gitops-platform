import os
import json
import subprocess
import sys

def analyze_cve_with_groq(cve_data: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    
    if not api_key:
        return "No se pudo obtener la API key"

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [{
            "role": "user",
            "content": f"Analiza estos CVEs de seguridad y da un resumen del riesgo y fix recomendado en español:\n{cve_data[:500]}"
        }],
        "max_tokens": 300
    })

    # Usar curl en lugar de urllib para evitar problemas con headers
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://api.groq.com/openai/v1/chat/completions",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", payload
    ], capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        return f"Error en curl: {result.stderr}"

    try:
        data = json.loads(result.stdout)
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return f"Respuesta inesperada: {result.stdout[:200]}"
    except json.JSONDecodeError:
        return f"Error parseando respuesta: {result.stdout[:200]}"


def create_pr(analysis: str, token: str, repo: str, run_id: str) -> None:
    # Obtener SHA
    result = subprocess.run([
        "curl", "-s",
        f"https://api.github.com/repos/{repo}/git/ref/heads/main",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Accept: application/vnd.github.v3+json"
    ], capture_output=True, text=True)

    sha = json.loads(result.stdout)["object"]["sha"]
    branch = f"security/ai-fix-{run_id}"

    # Crear branch
    subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.github.com/repos/{repo}/git/refs",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Accept: application/vnd.github.v3+json",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"ref": f"refs/heads/{branch}", "sha": sha})
    ], capture_output=True)

    # Crear PR
    pr_body = f"""## 🤖 AI Security Report

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
            "title": "🔒 [AI Security] Reporte de vulnerabilidades",
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
        trivy_report = "Análisis general de seguridad del repositorio"

    print("🔍 Analizando con Groq AI...")
    analysis = analyze_cve_with_groq(trivy_report)
    print(f"📋 Análisis:\n{analysis}")

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    run_id = os.environ.get("GITHUB_RUN_ID", "manual")

    if token and repo:
        print("\n🔀 Creando PR...")
        create_pr(analysis, token, repo, run_id)


if __name__ == "__main__":
    main()

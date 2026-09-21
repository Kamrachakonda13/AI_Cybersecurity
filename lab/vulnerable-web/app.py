"""AegisX lab target: intentionally misconfigured Flask app (TRAINING ONLY).

Help: routes (/, /admin exposed, /robots.txt, /api/users reflected input,
/ai/chat naive echo + injection logger) mirror exactly what the AegisX passive
assessment checks (headers/TLS/banner/robots). Runs as `nobody` in Docker
(see `lab/vulnerable-web/Dockerfile` + `docker-compose.lab.yml` guardrails).
Never expose to the internet; red team scans THIS host only.
"""
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# Intentionally misconfigured lab app — DO NOT expose to internet.
# Mirrors the exact issues AegisX passive checks look for.

@app.route("/")
def index():
    # Missing HSTS/CSP/X-Frame etc. on purpose; verbose Server banner set below.
    return jsonify({
        "app": "AegisX Lab — Vulnerable Web (intentional)",
        "routes": ["/", "/admin (exposed)", "/robots.txt", "/api/users?name=", "/ai/chat"],
        "note": "Local training target only. Scan only this host."
    })

@app.route("/admin")
def admin():
    # Intentional: exposed admin path without auth (for blue-team detection demo)
    return jsonify({"admin": True, "message": "Lab: exposed admin panel (no auth) — red should flag, blue should detect"}), 200

@app.route("/robots.txt")
def robots():
    return Response("User-agent: *\nDisallow: /admin\nDisallow: /backup.zip\n", mimetype="text/plain")

@app.route("/api/users")
def users():
    # Intentional: reflected input + verbose error (for safe manual review, no exploitation in AegisX)
    name = request.args.get("name", "guest")
    return jsonify({"hello": name, "role": "user", "debug": "Lab: reflects input; test with safe strings only"})

@app.route("/ai/chat", methods=["POST"])
def ai_chat():
    # Intentional: naive prompt passthrough (for Garak-style prompt-injection discussion, lab only)
    data = request.get_json(force=True, silent=True) or {}
    prompt = data.get("prompt", "")
    if "ignore previous instructions" in prompt.lower():
        return jsonify({"output": "Lab: prompt-injection pattern observed (logged, not executed)",
                        "logged": True})
    return jsonify({"output": f"Lab echo: {prompt[:200]}"})

@app.after_request
def banner(resp):
    # Intentional verbose banner for blue-team banner-grab demo
    resp.headers["Server"] = "AegisX-Lab/1.0 (Apache/2.4.1 Ubuntu)"
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4101)

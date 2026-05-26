from flask import Flask, request, jsonify, render_template_string
import sqlite3, secrets

app = Flask(__name__)

SECRET_TOKEN = "hacooscrapercle"

def init_db():
    conn = sqlite3.connect("keys.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS keys (
        key TEXT PRIMARY KEY,
        used INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()

init_db()

@app.route("/generate")
def generate():
    token = request.args.get("token", "")
    if token != SECRET_TOKEN:
        return "❌ Accès refusé.", 403

    key = "-".join([secrets.token_hex(2).upper() for _ in range(4)])
    conn = sqlite3.connect("keys.db")
    conn.execute("INSERT INTO keys (key) VALUES (?)", (key,))
    conn.commit()
    conn.close()
    return render_template_string(PAGE, key=key)

@app.route("/validate", methods=["POST"])
def validate():
    key = request.json.get("key", "").upper()
    conn = sqlite3.connect("keys.db")
    row = conn.execute("SELECT used FROM keys WHERE key=?", (key,)).fetchone()
    if not row:
        return jsonify({"valid": False, "reason": "Clé introuvable"})
    if row[0] == 1:
        return jsonify({"valid": False, "reason": "Clé déjà utilisée"})
    conn.execute("UPDATE keys SET used=1 WHERE key=?", (key,))
    conn.commit()
    conn.close()
    return jsonify({"valid": True})

PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Accès Discord</title>
  <style>
    body { font-family: 'Segoe UI', sans-serif; background: #0f0f0f;
           color: #fff; min-height: 100vh; display: flex;
           align-items: center; justify-content: center; }
    .card { background: #1a1a2e; border: 1px solid #5865F2;
            border-radius: 16px; padding: 40px 32px;
            text-align: center; max-width: 420px; width: 90%; }
    h1 { color: #5865F2; margin-bottom: 8px; }
    .key-box { background: #0d0d1a; border: 1px solid #57F287;
               border-radius: 10px; padding: 20px; margin: 24px 0; }
    .key-value { font-size: 22px; font-weight: bold;
                 letter-spacing: 3px; color: #57F287; }
    .copy-btn { background: #5865F2; color: white; border: none;
                padding: 12px 28px; border-radius: 8px;
                cursor: pointer; font-size: 15px; font-weight: bold; }
    code { background: #2b2b2b; padding: 2px 6px;
           border-radius: 4px; color: #57F287; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🔐 Accès Discord</h1>
    <p>Ta clé valable <strong>8 heures</strong> :</p>
    <div class="key-box">
      <div class="key-value">{{ key }}</div>
    </div>
    <button class="copy-btn" onclick="navigator.clipboard.writeText('{{ key }}');this.textContent='✅ Copié !'">
      📋 Copier
    </button>
    <p style="margin-top:20px;color:#666;font-size:13px">
      Utilise <code>/redeem</code> sur le Discord
    </p>
  </div>
</body>
</html>
"""

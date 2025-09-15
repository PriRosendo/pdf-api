# app.py
import os
import base64
import io
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader

API_KEY = os.environ.get("API_KEY", "troque_para_producao")

app = Flask(__name__)

def extrair_texto(pdf_bytes: bytes) -> str:
    texto = ""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            texto += page_text + "\n"
    return texto.strip()

@app.route("/ler-pdf", methods=["POST"])
def ler_pdf():
    # segurança simples
    if request.headers.get("x-api-key") != API_KEY:
        return jsonify({"erro": "não autorizado"}), 401

    data = request.get_json(silent=True)
    if not data or "content" not in data:
        return jsonify({"erro": "JSON inválido. Envie {'filename': '...','content':'<base64>'}"}), 400

    try:
        pdf_bytes = base64.b64decode(data["content"])
    except Exception:
        return jsonify({"erro": "content não é base64 válido"}), 400

    try:
        texto = extrair_texto(pdf_bytes)
        return jsonify({"texto": texto})
    except Exception as e:
        return jsonify({"erro": "Erro ao processar PDF", "detalhes": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


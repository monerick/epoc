import json
import logging

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from config import Config
from crypto import SecurePayload
from security import (
    limiter, require_api_key, security_headers,
    audit, InputValidator
)
from grapher import DataStore, Grapher

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = InputValidator.MAX_CONTENT_LENGTH
CORS(app, resources={r"/api/*": {"origins": "*"}})

limiter.init_app(app)

secure = SecurePayload()
data_store = DataStore()
grapher = Grapher()


@app.route("/health", methods=["GET"])
@security_headers
def health():
    return jsonify({
        "status": "ok",
        "encrypted": secure.cipher.encrypt("sistema_operativo"),
    })


@app.route("/api/v1/data", methods=["POST"])
@limiter.limit(Config.RATE_LIMIT)
@require_api_key
@security_headers
def receive_data():
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "")

    audit.log_request(client_ip, "POST", "/api/v1/data", 200, user_agent)

    try:
        raw = request.get_data(as_text=True)
    except Exception as e:
        audit.log_attack_attempt(client_ip, f"Error leyendo body: {e}")
        return jsonify({"error": "Error leyendo request"}), 400

    if not raw:
        return jsonify({"error": "Body vacio"}), 400

    try:
        data = secure.decode(raw)
    except ValueError:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return jsonify({"error": "Formato invalido: use SecurePayload.encode() o JSON"}), 400

    validated, err = InputValidator.validate_payload(data)
    if err:
        return jsonify({"error": err}), 400

    if isinstance(validated, list):
        for item in validated:
            if isinstance(item, dict):
                data_store.add_point(item.get("x", len(data_store.get_all())), item.get("value", item.get("y", 0)))
            else:
                data_store.add_point(len(data_store.get_all()), item)
    elif isinstance(validated, dict):
        x = validated.get("x", len(data_store.get_all()))
        y = validated.get("value", validated.get("y", 0))
        data_store.add_point(x, y)
    else:
        data_store.add_point(len(data_store.get_all()), validated)

    graph_path = grapher.plot(data_store)
    encrypted_count = secure.cipher.encrypt(str(len(data_store.get_all())))

    return jsonify({
        "status": "ok",
        "data_points": len(data_store.get_all()),
        "encrypted_count": encrypted_count,
        "graph": graph_path,
    })


@app.route("/api/v1/graph", methods=["GET"])
@security_headers
def get_graph():
    try:
        return send_file(grapher.output_path, mimetype="image/png")
    except FileNotFoundError:
        return jsonify({"error": "No hay grafico disponible"}), 404


@app.route("/api/v1/data", methods=["GET"])
@require_api_key
@security_headers
def get_data():
    points = data_store.get_all()
    encrypted_points = [
        {"x": secure.cipher.encrypt(str(p[0])), "y": secure.cipher.encrypt(str(p[1]))}
        for p in points
    ]
    return jsonify({
        "count": len(points),
        "encrypted": True,
        "data": encrypted_points,
    })


@app.route("/api/v1/data/clear", methods=["POST"])
@require_api_key
@security_headers
def clear_data():
    data_store.clear()
    return jsonify({"status": "ok", "message": "Datos eliminados"})


@app.errorhandler(429)
def ratelimit_handler(e):
    audit.log_attack_attempt(request.remote_addr, "Rate limit excedido")
    return jsonify({"error": "Demasiadas solicitudes", "message": str(e)}), 429


@app.errorhandler(413)
def payload_too_large(e):
    return jsonify({"error": "Payload demasiado grande"}), 413

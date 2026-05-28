import re
import hmac
import logging
import ipaddress
from functools import wraps
from datetime import datetime, timezone

from flask import request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config

logger = logging.getLogger(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[Config.RATE_LIMIT],
    storage_uri="memory://",
)


class IPSecurity:
    BLOCKED_RANGES = [
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "127.0.0.0/8",
    ]

    @classmethod
    def is_internal(cls, ip_str):
        try:
            addr = ipaddress.ip_address(ip_str)
            for rng in cls.BLOCKED_RANGES:
                if addr in ipaddress.ip_network(rng, strict=False):
                    return True
            return addr.is_private or addr.is_loopback
        except ValueError:
            return False


class InputValidator:
    MAX_CONTENT_LENGTH = 1024 * 100
    ALLOWED_TYPES = (int, float, str, list, dict)
    STRING_MAX_LEN = 512

    @classmethod
    def sanitize_string(cls, s):
        s = re.sub(r"[<>\";'()]|--|\bOR\b|\bAND\b|\bUNION\b|\bDROP\b|\bDELETE\b", "", s, flags=re.IGNORECASE)
        return s[: cls.STRING_MAX_LEN]

    @classmethod
    def validate_data_point(cls, value):
        if isinstance(value, (int, float)):
            return value, None
        if isinstance(value, str):
            try:
                return float(value), None
            except ValueError:
                return None, "El valor debe ser numerico"
        return None, "Tipo de dato no soportado"

    @classmethod
    def validate_payload(cls, data):
        if not data:
            return None, "Payload vacio"
        if isinstance(data, dict):
            if "x" not in data and "value" not in data:
                return None, "Falta campo 'x' o 'value'"
            return data, None
        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    if "x" not in item and "value" not in item:
                        return None, f"Elemento {i}: falta 'x' o 'value'"
                elif not isinstance(item, (int, float)):
                    return None, f"Elemento {i}: debe ser numerico"
            return data, None
        return data, None


class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("audit")
        handler = logging.FileHandler("logs/audit.log", encoding="utf-8")
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_request(self, ip, method, path, status, user_agent=""):
        self.logger.info(
            f"REQ | {ip} | {method} {path} | {status} | {user_agent[:100]}"
        )

    def log_auth_failure(self, ip, reason):
        self.logger.warning(f"AUTH_FAIL | {ip} | {reason}")

    def log_attack_attempt(self, ip, reason):
        self.logger.error(f"ATTACK | {ip} | {reason}")


audit = AuditLogger()


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key") or request.args.get("api_key")
        if not api_key:
            audit.log_auth_failure(request.remote_addr, "API key faltante")
            return jsonify({"error": "API key requerida"}), 401
        if not hmac.compare_digest(api_key, Config.API_KEY):
            audit.log_auth_failure(request.remote_addr, "API key invalida")
            return jsonify({"error": "API key invalida"}), 403
        return f(*args, **kwargs)
    return decorated


def enforce_tls(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_secure and not request.headers.get("X-Forwarded-Proto", "").startswith("https"):
            if Config.ENV == "production":
                return jsonify({"error": "HTTPS requerido"}), 426
        return f(*args, **kwargs)
    return decorated


def security_headers(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        resp = f(*args, **kwargs)
        if isinstance(resp, tuple):
            response_obj = resp[0]
        else:
            response_obj = resp
        if hasattr(response_obj, "headers"):
            response_obj.headers["X-Content-Type-Options"] = "nosniff"
            response_obj.headers["X-Frame-Options"] = "DENY"
            response_obj.headers["X-XSS-Protection"] = "1; mode=block"
            response_obj.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        return resp
    return decorated

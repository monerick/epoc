#!/usr/bin/env python3
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config, IS_PI, PI_MODEL
from server import app

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def print_banner():
    lines = [
        "  ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ",
        " | S e c u r e   D a t a   G r a p h e r |",
        " |___ ___ ___ ___ ___ ___ ___ ___ ___ ___ __|",
    ]
    for line in lines:
        print(line)


def start_ngrok():
    try:
        from pyngrok import ngrok, conf
        conf.get_default().auth_token = Config.NGROK_AUTHTOKEN
        public_url = ngrok.connect(Config.NGROK_PORT, bind_tls=True)
        logger.info(f"Tunel ngrok establecido: {public_url}")
        logger.info(f"URL del webhook: {public_url}/api/v1/data")
        return public_url
    except Exception as e:
        logger.warning(f"No se pudo iniciar ngrok: {e}")
        return None


def main():
    print_banner()

    if IS_PI:
        logger.info("Plataforma: Raspberry Pi detectada")
        logger.info(f"Modelo: {PI_MODEL}")
        logger.info("Modo optimizado para recursos limitados activado")
    else:
        logger.info(f"Plataforma: {sys.platform}")

    use_ngrok = "--ngrok" in sys.argv or os.environ.get("USE_NGROK", "").lower() in ("1", "true", "yes")

    if use_ngrok:
        start_ngrok()

    logger.info(f"Servidor en http://0.0.0.0:{Config.NGROK_PORT}")

    app.run(host="0.0.0.0", port=Config.NGROK_PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()

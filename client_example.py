#!/usr/bin/env python3
"""
Ejemplo de como enviar datos al bot desde otro script o dispositivo.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from crypto import SecurePayload

API_URL = "http://localhost:5000/api/v1/data"
API_KEY = "c4mb14r_3st0_3n_pr0ducc10n"

secure = SecurePayload()


def send_data_point(x, y):
    payload = {"x": x, "value": y}
    encrypted = secure.encode(payload)
    resp = requests.post(
        API_URL,
        data=encrypted,
        headers={
            "Content-Type": "text/plain",
            "X-API-Key": API_KEY,
        },
    )
    return resp.json()


def send_bulk(points):
    encrypted = secure.encode(points)
    resp = requests.post(
        API_URL,
        data=encrypted,
        headers={
            "Content-Type": "text/plain",
            "X-API-Key": API_KEY,
        },
    )
    return resp.json()


if __name__ == "__main__":
    import random
    import math
    import time

    print("Enviando datos de ejemplo...")
    for i in range(20):
        y = math.sin(i * 0.5) * 10 + random.uniform(-2, 2)
        result = send_data_point(i, y)
        print(f"  Punto {i}: {result}")
        time.sleep(0.2)

    print("\nEnviando bulk de 10 puntos...")
    bulk = [{"x": i + 20, "value": random.uniform(0, 50)} for i in range(10)]
    result = send_bulk(bulk)
    print(f"  Bulk: {result}")

    print(f"\nGrafico disponible en: http://localhost:5000/api/v1/graph")
    print(f"Datos en crudo: http://localhost:5000/api/v1/data (con API key)")

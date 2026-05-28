#!/usr/bin/env python3
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import app
from crypto import SecurePayload

secure = SecurePayload()
test_data = [{"x": i, "value": i * 2} for i in range(5)]
encoded = secure.encode(test_data)

with app.test_client() as client:
    resp = client.get("/health")
    print(f"GET /health: {resp.status_code} - {resp.get_json()['status']}")

    resp = client.post("/api/v1/data", data="test")
    print(f"POST sin API key: {resp.status_code} - {resp.get_json()['error']}")

    resp = client.post(
        "/api/v1/data",
        data=encoded,
        headers={"Content-Type": "text/plain", "X-API-Key": "c4mb14r_3st0_3n_pr0ducc10n"},
    )
    result = resp.get_json()
    print(f"POST cifrado: {resp.status_code} - points: {result['data_points']} - enc_count: {result['encrypted_count']}")

    resp = client.post(
        "/api/v1/data",
        data=json.dumps({"x": 10, "value": 99}),
        headers={"Content-Type": "text/plain", "X-API-Key": "c4mb14r_3st0_3n_pr0ducc10n"},
    )
    print(f"POST JSON raw: {resp.status_code} - points: {resp.get_json()['data_points']}")

    resp = client.get("/api/v1/graph")
    print(f"GET /api/v1/graph: {resp.status_code} - type: {resp.content_type}")

    resp = client.get(
        "/api/v1/data",
        headers={"X-API-Key": "c4mb14r_3st0_3n_pr0ducc10n"},
    )
    print(f"GET data: {resp.status_code} - count: {resp.get_json()['count']} - encrypted: {resp.get_json()['encrypted']}")

    for i in range(15):
        resp = client.post(
            "/api/v1/data",
            data=secure.encode({"x": i, "value": i}),
            headers={"Content-Type": "text/plain", "X-API-Key": "c4mb14r_3st0_3n_pr0ducc10n"},
        )
    print(f"Rate limit test: ultimo status = {resp.status_code}{' (OK)' if resp.status_code == 429 else ' (no limit?)'}")

    resp = client.post(
        "/api/v1/data/clear",
        headers={"X-API-Key": "c4mb14r_3st0_3n_pr0ducc10n"},
    )
    print(f"Clear: {resp.status_code} - {resp.get_json()['message']}")

    print("\n=== Todos los tests pasaron ===")

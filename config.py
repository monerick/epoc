import os
import platform
import subprocess


def _is_raspberry_pi():
    try:
        if platform.machine() in ("armv7l", "aarch64"):
            with open("/proc/cpuinfo") as f:
                return "Raspberry Pi" in f.read() or "BCM" in f.read()
    except Exception:
        pass
    return False


IS_PI = _is_raspberry_pi()


def _pi_version():
    if not IS_PI:
        return None
    try:
        out = subprocess.check_output(
            ["cat", "/proc/device-tree/model"], stderr=subprocess.DEVNULL, timeout=2
        ).decode("utf-8", errors="ignore").strip("\x00").strip()
        return out
    except Exception:
        return "Raspberry Pi detectada"


PI_MODEL = _pi_version()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "c4mb14r_3st0_3n_pr0ducc10n")
    API_KEY = os.environ.get("API_KEY", "c4mb14r_3st0_3n_pr0ducc10n")
    CAESAR_SHIFT = int(os.environ.get("CAESAR_SHIFT", "7"))
    NGROK_AUTHTOKEN = os.environ.get("NGROK_AUTHTOKEN", "")
    NGROK_PORT = int(os.environ.get("NGROK_PORT", "5000"))
    MAX_DATA_POINTS = int(os.environ.get("MAX_DATA_POINTS", "200" if IS_PI else "100"))
    RATE_LIMIT = os.environ.get("RATE_LIMIT", "10 per minute")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    GRAPH_OUTPUT = os.environ.get("GRAPH_OUTPUT", "graphs/last_graph.png")

    GRAPH_DPI = int(os.environ.get("GRAPH_DPI", "80" if IS_PI else "150"))
    GRAPH_FIGSIZE = eval(os.environ.get("GRAPH_FIGSIZE", "(8, 4)" if IS_PI else "(12, 6)"))

    READ_SENSOR = False

    PI_OPTIMIZED = IS_PI
    PI_MODEL = PI_MODEL if IS_PI else None

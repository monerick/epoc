#!/usr/bin/env bash
set -euo pipefail

BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="secure-grapher"
INSTALL_DIR="/opt/secure-grapher"

echo "============================================"
echo "  Secure Data Grapher - Instalacion Raspbian"
echo "============================================"
echo ""

# --- Detectar Pi ---
if grep -qi "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "[OK] Raspberry Pi detectada"
else
    echo "[!] No se detecto Raspberry Pi. Continuando igual..."
fi

# --- Actualizar sistema ---
echo ""
echo "[1/6] Actualizando paquetes del sistema..."
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

# --- Dependencias del sistema ---
echo ""
echo "[2/6] Instalando dependencias del sistema..."
sudo apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    libatlas-base-dev \
    libopenjp2-7 \
    libtiff6 \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-tk \
    git \
    curl

# --- Instalar ngrok si no existe ---
echo ""
echo "[3/6] Verificando ngrok..."
if ! command -v ngrok &>/dev/null; then
    echo "  Instalando ngrok..."
    cd /tmp
    curl -s https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz -o ngrok.tgz
    sudo tar xzf ngrok.tgz -C /usr/local/bin/
    rm ngrok.tgz
    echo "  ngrok instalado"
else
    echo "  ngrok ya esta instalado"
fi

# --- Crear entorno virtual e instalar dependencias Python ---
echo ""
echo "[4/6] Instalando dependencias Python..."
sudo mkdir -p "$INSTALL_DIR"
sudo cp -r "$BOT_DIR"/* "$INSTALL_DIR/"
sudo chown -R "$USER:$USER" "$INSTALL_DIR"

cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip setuptools wheel

# Instalar dependencias base
pip install flask flask-cors flask-limiter matplotlib requests

# Instalar ngrok Python
pip install pyngrok

# --- Crear archivo de configuracion .env ---
echo ""
echo "[5/6] Creando archivo .env..."
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cat > "$INSTALL_DIR/.env" << 'ENVEOF'
SECRET_KEY=c4mb14r_3st0_3n_pr0ducc10n
API_KEY=c4mb14r_3st0_3n_pr0ducc10n
CAESAR_SHIFT=7
NGROK_AUTHTOKEN=
NGROK_PORT=5000
MAX_DATA_POINTS=200
RATE_LIMIT=10 per minute
LOG_LEVEL=INFO
GRAPH_DPI=80
GRAPH_FIGSIZE=(8, 4)
ENVEOF
    echo "  .env creado en $INSTALL_DIR/.env"
    echo "  ! IMPORTANTE: Edite API_KEY y NGROK_AUTHTOKEN en .env"
fi

# --- Instalar servicio systemd ---
echo ""
echo "[6/6] Instalando servicio systemd..."
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
sudo tee "$SERVICE_FILE" > /dev/null << SERVICEOF
[Unit]
Description=Secure Data Grapher Bot
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/run.py
Restart=always
RestartSec=10
StartLimitIntervalSec=60
StartLimitBurst=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICEOF

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}.service"
sudo systemctl restart "${SERVICE_NAME}.service"

echo ""
echo "============================================"
echo "  Instalacion completada!"
echo "============================================"
echo ""
echo "  Servicio: ${SERVICE_NAME}"
echo "  Directorio: ${INSTALL_DIR}"
echo "  Logs: sudo journalctl -u ${SERVICE_NAME} -f"
echo "  Estado: sudo systemctl status ${SERVICE_NAME}"
echo "  API: http://$(hostname -I | awk '{print $1}'):${NGROK_PORT:-5000}/api/v1/data"
echo ""
echo "  ! Edite API_KEY y NGROK_AUTHTOKEN en:"
echo "    sudo nano ${INSTALL_DIR}/.env"
echo "  Luego reinicie: sudo systemctl restart ${SERVICE_NAME}"
echo ""

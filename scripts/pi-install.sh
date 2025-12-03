#!/usr/bin/env bash
set -euo pipefail

# CitySafeSense Raspberry Pi 4 automated installer
# Usage:
#   sudo bash scripts/pi-install.sh \
#     --repo https://github.com/<OWNER>/citysafesense-demo.git \
#     --branch main \
#     --model models/model_quant.tflite \
#     --mqtt mqtt.example.local \
#     --device-id pi4-edge-001 \
#     --install-docker no
#
# The script will:
#  - update the OS packages
#  - install system dependencies
#  - clone or pull repo to /home/pi/citysafesense (uses current user 'pi' or $SUDO_USER)
#  - create a python venv and install requirements
#  - attempt to install tflite-runtime; fallback to tensorflow if unavailable
#  - create a systemd service to run infer_edge.py
#  - optionally install Docker and run the Docker image

LOG="/var/log/citysafesense-installer.log"
exec > >(tee -a "$LOG") 2>&1

# Defaults
REPO="${REPO:-https://github.com/meltedtuna/citysafesense-demo.git}"
BRANCH="${BRANCH:-main}"
MODEL_PATH="${MODEL_PATH:-models/model_quant.tflite}"
MQTT_HOST="${MQTT_HOST:-mqtt.example.local}"
DEVICE_ID="${DEVICE_ID:-pi4-edge-001}"
INSTALL_DOCKER="${INSTALL_DOCKER:-no}"   # "yes" to use Docker runtime
INSTALL_USER="${INSTALL_USER:-pi}"
INSTALL_DIR="/home/${INSTALL_USER}/citysafesense"
VENV_DIR="${INSTALL_DIR}/venv"
PYTHON_BIN="python3"

# parse CLI args (simple)
while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="$2"; shift 2;;
    --branch) BRANCH="$2"; shift 2;;
    --model) MODEL_PATH="$2"; shift 2;;
    --mqtt) MQTT_HOST="$2"; shift 2;;
    --device-id) DEVICE_ID="$2"; shift 2;;
    --install-docker) INSTALL_DOCKER="$2"; shift 2;;
    --user) INSTALL_USER="$2"; shift 2;;
    --help) echo "Usage: $0 [--repo URL] [--branch BRANCH] [--model PATH] [--mqtt HOST] [--device-id ID] [--install-docker yes|no]"; exit 0;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

echo "=== CitySafeSense Pi installer ==="
echo "Repo: $REPO"
echo "Branch: $BRANCH"
echo "Install dir: $INSTALL_DIR"
echo "Model path: $MODEL_PATH"
echo "MQTT host: $MQTT_HOST"
echo "Device ID: $DEVICE_ID"
echo "Docker runtime: $INSTALL_DOCKER"
echo "User: $INSTALL_USER"
echo "Log: $LOG"
echo "---------------------------------"

# ensure running as root
if [ "$(id -u)" -ne 0 ]; then
  echo "ERROR: this script must be run as root (sudo)." >&2
  exit 2
fi

# Ensure install user exists
if ! id -u "$INSTALL_USER" >/dev/null 2>&1; then
  echo "User $INSTALL_USER does not exist. Creating..."
  useradd -m -s /bin/bash "$INSTALL_USER"
fi

# Update / install core packages
echo "[1/8] apt update & install packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y --no-install-recommends \
  git curl wget ca-certificates build-essential python3 python3-venv python3-pip \
  libatlas-base-dev libatlas3-base libblas-dev liblapack-dev libffi-dev libssl-dev \
  mosquitto-clients jq unzip zip

# On Pi OS 64-bit apt may not include tflite wheels; we will attempt pip install
# Ensure pip is up-to-date for the system python
python3 -m pip install --upgrade pip setuptools wheel

# Clone or update repo
echo "[2/8] clone or update repository..."
if [ -d "${INSTALL_DIR}/.git" ]; then
  echo "Repository already exists; pulling latest from ${BRANCH}..."
  sudo -u "$INSTALL_USER" git -C "$INSTALL_DIR" fetch --all --prune
  sudo -u "$INSTALL_USER" git -C "$INSTALL_DIR" checkout "$BRANCH"
  sudo -u "$INSTALL_USER" git -C "$INSTALL_DIR" pull origin "$BRANCH"
else
  echo "Cloning ${REPO} into ${INSTALL_DIR}..."
  sudo -u "$INSTALL_USER" git clone --depth 1 --branch "$BRANCH" "$REPO" "$INSTALL_DIR"
fi

# Create venv and install requirements
echo "[3/8] Creating Python venv and installing requirements..."
if [ ! -d "$VENV_DIR" ]; then
  sudo -u "$INSTALL_USER" "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# Activate venv and install
# Use pip in venv
PIP="${VENV_DIR}/bin/pip"
PY="${VENV_DIR}/bin/python"
"$PIP" install --upgrade pip setuptools wheel

# Install project requirements if present
if [ -f "${INSTALL_DIR}/requirements.txt" ]; then
  echo "Installing Python requirements from requirements.txt..."
  "$PIP" install -r "${INSTALL_DIR}/requirements.txt" || echo "pip install -r requirements failed (continuing)"
else
  echo "No requirements.txt found - continuing."
fi

# Try to install tflite-runtime; try generic pip first, then fallback to tensorflow
echo "[4/8] Installing TensorFlow Lite runtime (or fallback)..."
TFLITE_OK=0
echo "Attempting to pip install tflite-runtime..."
if "$PIP" install tflite-runtime; then
  TFLITE_OK=1
  echo "tflite-runtime installed via pip."
else
  echo "pip install tflite-runtime failed. Attempting to install via wheel heuristics..."
  # Attempt simple wheel heuristics for common Pi variants (best-effort)
  ARCH=$(uname -m)
  PYVER=$($PY -c "import sys;print('cp{}{}'.format(sys.version_info.major, sys.version_info.minor))")
  # A few heuristics (may not match your installation); warn user if not found
  if [ "$ARCH" = "aarch64" ]; then
    # attempt common pycoral wheel from GitHub - NOTE: these may change over time
    WHEEL_URL="https://github.com/google-coral/pycoral/releases/latest/download/tflite_runtime-${PYVER}-linux_aarch64.whl"
    echo "Trying wheel: $WHEEL_URL"
    if "$PIP" install "$WHEEL_URL"; then
      TFLITE_OK=1
    fi
  else
    # armv7l (32-bit)
    WHEEL_URL="https://github.com/google-coral/pycoral/releases/latest/download/tflite_runtime-${PYVER}-linux_armv7l.whl"
    echo "Trying wheel: $WHEEL_URL"
    if "$PIP" install "$WHEEL_URL"; then
      TFLITE_OK=1
    fi
  fi

  if [ "$TFLITE_OK" -ne 1 ]; then
    echo "tflite-runtime wheel installation failed. Installing full tensorflow as fallback (large)."
    echo "WARNING: Installing tensorflow on Pi may be large and slow; prefer installing tflite-runtime wheel matching your Python & arch."
    if "$PIP" install tensorflow; then
      echo "tensorflow installed as fallback."
      TFLITE_OK=1
    else
      echo "ERROR: Could not install tflite-runtime nor tensorflow. Please install tflite-runtime manually for your Python/arch and re-run." >&2
      # continue: user may still want Docker path
    fi
  fi
fi

# Copy example config or create placeholders if missing
echo "[5/8] Ensuring config & certs directories..."
CONFIG_DIR="${INSTALL_DIR}/config"
CERTS_DIR="${INSTALL_DIR}/certs"
mkdir -p "$CONFIG_DIR" "$CERTS_DIR"
chown -R "${INSTALL_USER}:${INSTALL_USER}" "$INSTALL_DIR"

# Ensure model exists (if provided path is inside repo, else leave to user)
if [ -f "${INSTALL_DIR}/${MODEL_PATH}" ]; then
  echo "Model found at ${INSTALL_DIR}/${MODEL_PATH}"
else
  echo "WARNING: Model not found at ${INSTALL_DIR}/${MODEL_PATH}"
  echo "Please copy or place your TFLite quantized model at: ${INSTALL_DIR}/${MODEL_PATH}"
fi

# Create a small wrapper script to run inference (if infer_edge.py exists, use it)
SERVICE_SCRIPT="${INSTALL_DIR}/run_infer.sh"
cat > "$SERVICE_SCRIPT" <<EOF
#!/usr/bin/env bash
source "${VENV_DIR}/bin/activate"
cd "${INSTALL_DIR}"
# Ensure environment variables are available
export MQTT_HOST="${MQTT_HOST}"
export DEVICE_ID="${DEVICE_ID}"
# run the main inference script (change if your main file is different)
if [ -f "${INSTALL_DIR}/infer_edge.py" ]; then
  exec "${VENV_DIR}/bin/python" "${INSTALL_DIR}/infer_edge.py" --model "${MODEL_PATH}" --mqtt "${MQTT_HOST}" --device-id "${DEVICE_ID}"
else
  echo "infer_edge.py not found. Please ensure your inference script exists at ${INSTALL_DIR}/infer_edge.py"
  exit 1
fi
EOF
chmod +x "$SERVICE_SCRIPT"
chown "${INSTALL_USER}:${INSTALL_USER}" "$SERVICE_SCRIPT"

# Create systemd service
echo "[6/8] Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/citysafesense.service"
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=CitySafeSense Edge Inference Service
After=network-online.target

[Service]
User=${INSTALL_USER}
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${VENV_DIR}/bin"
ExecStart=${SERVICE_SCRIPT}
Restart=on-failure
RestartSec=5
StartLimitIntervalSec=60
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable citysafesense.service

# If user chose Docker runtime, install docker and docker-compose and create container
if [ "${INSTALL_DOCKER}" = "yes" ]; then
  echo "[7/8] Installing Docker & docker-compose..."
  # Install Docker using convenience script
  if ! command -v docker >/dev/null 2>&1; then
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker "$INSTALL_USER" || true
  else
    echo "Docker already installed."
  fi
  # Build or pull docker image
  echo "Building Docker image using Dockerfile.prod (may take a while) ..."
  docker -v
  docker build -f "${INSTALL_DIR}/Dockerfile.prod" -t citysafesense-edge:latest "${INSTALL_DIR}" || echo "Docker build failed (you can pull from GHCR instead)"
  # Create a basic docker-compose if not present
  if [ ! -f "${INSTALL_DIR}/docker-compose.yml" ]; then
    cat > "${INSTALL_DIR}/docker-compose.yml" <<EOD
version: '3.8'
services:
  citysafesense:
    image: citysafesense-edge:latest
    restart: unless-stopped
    volumes:
      - ./models:/app/models:ro
      - ./certs:/app/certs:ro
    environment:
      - MQTT_HOST=${MQTT_HOST}
      - DEVICE_ID=${DEVICE_ID}
EOD
  fi

  # create systemd service that runs docker-compose
  cat > "/etc/systemd/system/citysafesense-docker.service" <<EOF
[Unit]
Description=CitySafeSense (Docker)
After=docker.service
Requires=docker.service

[Service]
Restart=always
WorkingDirectory=${INSTALL_DIR}
ExecStart=/usr/bin/docker-compose -f ${INSTALL_DIR}/docker-compose.yml up
ExecStop=/usr/bin/docker-compose -f ${INSTALL_DIR}/docker-compose.yml down
User=${INSTALL_USER}
Group=${INSTALL_USER}

[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  systemctl enable citysafesense-docker.service
  echo "Docker service prepared. Start it with: sudo systemctl start citysafesense-docker"
fi

# Start the service (systemd) unless user chose Docker-only and didn't want both
if [ "${INSTALL_DOCKER}" != "yes" ]; then
  echo "[8/8] Starting citysafesense service..."
  systemctl start citysafesense.service
  sleep 2
  systemctl status citysafesense.service --no-pager || true
else
  echo "[8/8] Docker runtime configured. To start: sudo systemctl start citysafesense-docker"
fi

echo "Installation complete. Logs: $LOG"
echo "If the service failed to start, check: sudo journalctl -u citysafesense -n 200 -f"
echo "If you selected Docker runtime, check: sudo journalctl -u citysafesense-docker -n 200 -f"

exit 0

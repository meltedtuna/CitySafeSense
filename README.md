CitySafeSense — Edge AI for Urban Safety | PROOF OF CONCEPT

A privacy-preserving, real-time sensor analytics platform for detecting risky mobility patterns in urban hotspots.

CitySafeSense is an end-to-end system that uses edge devices, MQTT pipelines, and temporal deep learning models (TCNs) to detect unusual sensor patterns associated with risky events such as muggings, forced movement, and abrupt phone displacement, while preserving user privacy through anonymized hotspot sensing.

This project includes:

Edge ML models (TensorFlow TCN optimised for microcontrollers)

Sensor simulator for synthetic IMU × GNSS × acoustic data

Training pipeline with augmentation (jitter, noise, time-warp, rotation)

Real-time MQTT ingestion stack (Mosquitto + TLS + password auth)

Dashboard-ready APIs (FastAPI)

Hotspot mapping logic for cities like São Paulo

PDF whitepaper generator (automatic figure export)

Deployment checklists and installation guide

Containerized toolchain + future CI/CD support

🚀 Features
🔎 1. Edge Temporal Convolutional Network (TCN)

A lightweight TCN architecture optimised for low-latency classification on microcontrollers.
Detects patterns such as:

Walking → entering a vehicle

Stationary → forced movement

Free walking → sudden displacement (mugging signature)

🏙 2. Privacy-Preserving Hotspot Coverage

A non-identifying sensor network that monitors:

Movement vectors

Velocity discontinuities

Population-level flow anomalies

No personal data, MAC addresses, IDs, or biometrics are collected.

🛰 3. Synthetic Sensor Dataset Generator

Generates realistic IMU + GNSS + acoustic signals:

Normal walking

Slow walking

Entering a car

Riding in vehicle

Mugging profiles (sudden displacement + direction change)

Includes augmentation templates for robust training.

📊 4. Visualization Tools

Matplotlib tools for:

Sequence plots

Overlays (walking vs car vs mugging)

Vector flow field visualizations

Auto-export of all charts to PDF

📦 5. Full DevOps Support

Docker container for inference + API

GitHub Actions templates (PyTest, coverage, lint, build)

Sphinx/MkDocs documentation scaffolding

CLI tool wrapping all scripts (training, simulation, export)

🛠 6. Installer-Friendly Deployment

A printable checklist including:

Wiring

Hardware torque specs

Safety guidelines

Troubleshooting steps


💡 Why This Exists

Urban theft patterns often follow detectable kinetic signatures. With modern low-cost sensors + edge ML, we can build anonymous early-warning systems that help authorities understand where muggings occur, how movement patterns change, and when a stolen device moves differently from a person.

This project provides an end-to-end reference implementation.

📄 License

MIT License (modifiable based on your preference).

## Quick start

```bash
# create virtualenv
python -m venv .venv
source .venv/bin/activate

# install
pip install -r requirements.txt

# run synthetic data generator
python -m src.tools.generate_synthetic --out data/synthetic_sample.npy --duration 60

# start broker (docker-compose)
docker compose up -d

# train a tiny model (demo)
python -m src.train.train_demo --epochs 2

# export TFLite
python -m src.model.export_tflite --checkpoint ./checkpoints/demo.ckpt --out model.tflite
```

## Project layout
```
CitySafeSense/
├─ src/
│  ├─ data/
│  ├─ model/
│  ├─ train/
│  ├─ ingest/
│  ├─ tools/
│  └─ cli.py
├─ docker-compose.yml
├─ Dockerfile
├─ requirements.txt
├─ README.md
└─ LICENSE
```

## License
MIT. See `LICENSE` in repo.



## Training & export examples

Run a short demo training (1 epoch), save a full `.keras` model and export a quantized TFLite model:

```bash
python -m src.train.train_demo --epochs 1 --save_full_model --export_tflite --tflite_quantize
```

This will produce artifacts under `checkpoints/`:

- `full_model_best.keras` (full model saved by the FullModelSaver callback)
- `best_model.h5` (ModelCheckpoint file)
- `citysafesense_model.json` and `citysafesense_model_summary.txt` (architecture)
- `model.tflite` (exported TFLite; quantized if `--tflite_quantize` was used)

For better quantization results, customize `src/tools/representative_dataset.py` to yield representative samples from your real dataset.


## Manually trigger the CI smoke job (Actions -> Run workflow)

The repository includes a manual smoke workflow to run a short training + export. To invoke it:

1. Go to the **Actions** tab in your GitHub repository.
2. Select the workflow named **Smoke training & export**.
3. Click **Run workflow** (the manual dispatch button) and choose branch `main` (or another branch).
4. Click the green **Run workflow** button to start the job.

The workflow will perform a 1-epoch training, export a TFLite model, and upload artifacts under *Artifacts* in the workflow run (look for `smoke-model-artifacts`).


## CI smoke workflow badge (optional)

You can add a workflow status badge that points to the repository Actions workflow. Replace `<OWNER>` and `<REPO>` with your GitHub owner and repository name.

```
[![Smoke workflow](https://github.com/<OWNER>/<REPO>/actions/workflows/.github/workflows/ci.yml/badge.svg?event=workflow_dispatch)](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml)
```

To manually run the smoke workflow:
1. Go to **Actions → Smoke training & export** in the GitHub UI.
2. Click **Run workflow** (choose branch and inputs) and run.

Note: The smoke job builds the `infra/Dockerfile.tf` image in CI and runs a 1-epoch training inside that container, then uploads artifacts from `checkpoints/` and `data/sample.npy`.


**Note about producing real model artifacts in this environment**

I updated the CI to build and run the Docker image in GitHub Actions so the full E2E can run in CI. I cannot run Docker builds inside this assistant execution environment to produce real `checkpoints/` artifacts here. To produce real artifacts locally, run:

```bash
# build image locally and run E2E
docker build -f infra/Dockerfile.tf -t citysafesense:local .
docker run --rm -v "$(pwd)":/app citysafesense:local \
  python -m src.train.train_demo --epochs 1 --save_full_model --export_tflite --tflite_quantize
```

After that, `checkpoints/` will contain real model artifacts and `data/sample.npy` will be updated.


## Docker image build workflow

There is a dedicated GitHub Actions workflow `.github/workflows/docker-build.yml` that builds the
runtime Docker image (`infra/Dockerfile.tf`) and caches intermediate layers to speed up future builds.
You can trigger it manually under Actions -> Docker Image Build (cached) or let it run on pushes to `main`.



## Container image (GHCR)

You can pull the prebuilt image from GitHub Container Registry (GHCR) once published:

```bash
docker pull ghcr.io/<OWNER>/citysafesense:latest
# or a specific commit
docker pull ghcr.io/<OWNER>/citysafesense:<COMMIT_SHA>
```

Badge (replace `<OWNER>` with your org/user):

```
[![GHCR image](https://img.shields.io/badge/ghcr.io%2F<OWNER>%2Fcitysafesense-blue)](https://ghcr.io/packages)
```



🚀 CitySafeSense — Raspberry Pi 4 Edge Deployment Guide

This guide walks you through preparing a Raspberry Pi 4 to run the CitySafeSense Edge AI Inference Runtime, including:

OS setup

Installing dependencies

Installing the model + inference service

Secure MQTT configuration

Running as a systemd service or as a Docker container

Everything is optimized for Raspberry Pi 4 (ARM64 or ARMv7).

1. 🔧 Raspberry Pi 4 — System Preparation
✔️ Recommended OS

Use Raspberry Pi OS (64-bit):

Raspberry Pi OS Lite 64-bit (preferred)

Raspberry Pi OS Desktop 64-bit

✔️ Update the system
sudo apt update && sudo apt full-upgrade -y
sudo reboot

✔️ Essential packages
sudo apt install -y python3 python3-pip python3-venv git wget unzip mosquitto-clients

2. 🔐 Install TFLite Runtime (optimized for Pi 4)

TensorFlow Lite full is too heavy; Raspberry Pi uses tflite-runtime.

Determine your Python version:
python3 --version

Install TFLite Runtime wheel

For Python 3.9+ on Raspberry Pi 4 (ARM64):

# Example wheel (replace with the latest ARM64 wheel matching your version):
pip3 install https://github.com/google-coral/pycoral/releases/download/release-frogfish/tflite_runtime-2.14.0-cp39-cp39-linux_aarch64.whl


If you're running ARMv7 (32-bit), install the ARMv7 wheel instead.

3. 📁 Deploy CitySafeSense Files to Pi

On your local machine, copy the release bundle:

scp -r citysafesense-release-bundle/ pi@<YOUR_PI_IP>:/home/pi/citysafesense/


or clone your repo directly on the Pi:

cd ~
git clone https://github.com/<your-org>/citysafesense.git
cd citysafesense


Ensure the folder contains:

models/model_quant.tflite
infer_edge.py
client_mqtt.py
certs/
release-dist/  (optional for debugging)

4. ⚙️ Create Python Virtual Environment
cd ~/citysafesense
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt


If tflite_runtime was not inside requirements, install manually:

pip install tflite-runtime

5. 🔧 Configure MQTT Secure Connection (Recommended)
Create directory:
mkdir -p ~/citysafesense/certs


Add files:

certs/ca.pem
certs/client.crt       (optional — if using mutual TLS)
certs/client.key       (optional)

Test connection:
mosquitto_sub --cafile certs/ca.pem \
  -h mqtt.example.local \
  -t "citysafesense/events/#" \
  -u device1 -P "<password>"

6. 🤖 Running the Model — Manual Test
source venv/bin/activate
python infer_edge.py \
  --model models/model_quant.tflite \
  --mqtt mqtt.example.local \
  --tls-cert certs/ca.pem \
  --topic citysafesense/events \
  --device-id pi4-edge-001


If everything works, you’ll see logs like:

[INFO] Window processed — anomaly_prob=0.87
[MQTT] Published event to citysafesense/events

7. 🔁 Running as a Persistent systemd Service (recommended)

Create file:

sudo nano /etc/systemd/system/citysafesense.service


Paste:

[Unit]
Description=CitySafeSense Edge AI Inference (Raspberry Pi 4)
After=network-online.target

[Service]
User=pi
WorkingDirectory=/home/pi/citysafesense
Environment="PATH=/home/pi/citysafesense/venv/bin"
ExecStart=/home/pi/citysafesense/venv/bin/python infer_edge.py \
    --model models/model_quant.tflite \
    --mqtt mqtt.example.local \
    --tls-cert certs/ca.pem \
    --topic citysafesense/events \
    --device-id pi4-edge-001
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target


Run:

sudo systemctl daemon-reload
sudo systemctl enable citysafesense
sudo systemctl start citysafesense
sudo journalctl -u citysafesense -f

8. 🐳 Running with Docker (optional but excellent)
Install Docker:
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker pi


Logout & login.

Build or pull image

Using your published GHCR image:

docker pull ghcr.io/<OWNER>/citysafesense-demo:latest


If you need to build on the Pi:

docker build -f Dockerfile.prod -t citysafesense-edge:latest .

Run container
docker run -d \
  --name citysafesense \
  --restart unless-stopped \
  -v $(pwd)/models:/app/models:ro \
  -v $(pwd)/certs:/app/certs:ro \
  -e MQTT_HOST=mqtt.example.local \
  -e MQTT_TOPIC=citysafesense/events \
  -e DEVICE_ID=pi4-edge-001 \
  -p 8080:80 \
  ghcr.io/<OWNER>/citysafesense-demo:latest


View logs:

docker logs -f citysafesense

9. 📊 Validate Data Flow
Check MQTT messages arriving:
mosquitto_sub --cafile certs/ca.pem -h mqtt.example.local \
  -t "citysafesense/events" -v -u user -P pass

Common telemetry JSON:
{
  "device": "pi4-edge-001",
  "timestamp": 1715982012,
  "event": "forced_displacement",
  "probability": 0.92,
  "vector": [0.12, -1.09, 3.88]
}

10. ✔️ Performance Tips for Raspberry Pi 4
Enable 64-bit mode

Use Raspberry Pi OS 64-bit for fastest TFLite inference.

Disable CPU throttling during testing:
vcgencmd measure_temp
vcgencmd get_throttled

Use performance governor:
sudo apt install -y cpufrequtils
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
sudo systemctl restart cpufrequtils

Reduce SD card wear:

Use Docker bind mounts or tmpfs for logs.

11. 🧪 Troubleshooting
❌ TFLite says “unsupported op”

Your model uses ops not included in TF Lite Micro / TF Lite Runtime minimal build.
Solution: Enable “SELECT_TF_OPS” or reduce model complexity.

❌ MQTT TLS failure

Verify CA file matches broker’s CA:

openssl s_client -connect mqtt.example.local:8883 -CAfile certs/ca.pem

❌ Low performance

Try:

int8 quantized model

fewer filters / layers

smaller window size

use Pi 4 overclocking (if safe)

12. 🎉 Raspberry Pi 4 Deployment Complete

Your Pi now:

Runs quantized TFLite inference

Publishes anomaly events to MQTT securely

Starts automatically on boot via systemd or Docker

Can be mass-deployed using SD card images or fleet tools like Balena, Ansible, or Mender


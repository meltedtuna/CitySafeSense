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

## Quick summary (what you’ll build)

A weather/air-quality/motion edge node built around a single-board computer (Raspberry Pi 4 / Pi Zero 2 W alternative) or an MCU (ESP32 option) with sensors (temp/humidity, particulate matter, GPS, inertial), a robust battery pack with BMS, optional solar input, cellular + Wi-Fi comms, and layered redundancies (dual comms, UPS, storage backup, watchdog & healthcheck).

## 1) Parts & tools (recommended)
Core compute (pick one)

## Raspberry Pi 4 (4GB) — for heavier local processing / neural inferencing OR

Raspberry Pi Zero 2 W — low-power, for light workloads OR

ESP32 (Wroom) — ultra low power (if no Linux needed)

(Optional) NVIDIA Jetson Nano / Orin Nano — for heavy vision/AI

## Connectivity

LTE modem (USB or HAT) — e.g., Quectel EC25 / Quectel EG25 / USB LTE dongle with external antenna support

Wi-Fi (built into Pi)

LoRa module (SX127x) for long-range low-power mesh (optional)

GPS module (u-blox NEO-M8N recommended)

## Sensors

Temperature & humidity: SHT31 or SHT35 (I2C)

Particulate matter (PM2.5): Plantower PMS7003 or Sensirion SPS30 (UART/I2C)

Gas / VOC (optional): Sensirion SGP40 or BME680 (VOC + temp/humidity/pressure) — avoid raw MQ sensors for production without calibration

Inertial: MPU6050 / ICM20948 (imu) — accelerometer/gyro

Light sensor: TSL2591 or BH1750 (I2C)

Passive infrared (PIR) sensor (motion)

Camera (optional): Raspberry Pi Camera v2 / IMX219 or Pi HQ camera

## Power / battery

LiFePO4 3.2V nominal cells (recommended for safety) OR high-quality Li-ion pack with integrated BMS

Battery Management System (BMS) matched to pack (overcharge, overdischarge, balancing)

5V DC-DC converter / UPS HAT (for Raspberry Pi): e.g., Pi UPS HAT, PowerBoost 5V with LiPo support, or dedicated UPS board with fuel gauge. Must support continuous 5V @ device current.

Inline fuse (fast blow) on battery output (rating slightly above expected max current)

Optional solar charge controller (MPPT) if using solar

## Storage & redundancy

microSD (industrial grade) + external USB SSD (for mirrored data/overflow)

microSD write-protect switch / overlayfs to reduce SD corruption

## Mechanical / enclosure / misc

IP66/67-rated enclosure (if outdoor) sized to fit SBC + battery pack + connectors

Gasket, cable glands (appropriate diameters), stainless hardware (screws, standoffs)

DIN rail mounts or wall mounts, vibration damping pads

Antenna(s) with SMA connectors (LTE, GPS separate)

Heat sinks, thermal pads, small fan (if enclosed and hot environment)

## Tools

Soldering iron + flux, hot air station optional

Multimeter, clamp meter, thermal probe

Wire strippers, crimpers, M2–M4 hex drivers, screwdrivers

Heat shrink tubes, cable ties, silicone sealant

USB to serial adapter (for debugging)

## 2) Planning & layout (decisions before assembly)

Pick compute platform based on workload (Pi4 = heavy; Pi Zero/ESP32 = low-power).

Decide primary comms: will it use LTE (cellular) as primary, Wi-Fi as fallback, or vice versa? Plan dual-SIM LTE if you want carrier redundancy.

Define expected run time on battery and update frequency (sensing & transmission cadence affect power). You’ll need this for battery sizing — example calculation below.

Select enclosure rated for the environment. If outdoor, include desiccant and conformal coating for PCBs.

## 3) Power budgeting (worked example — follow this exactly)

We must calculate power draw precisely (digit by digit). Assume the configuration below (you can swap values for your parts):

Assumed component peak currents at 5 V:

Raspberry Pi 4 peak draw: 1.200 A

LTE modem TX peak: 0.600 A

PMS7003 particulate sensor peak: 0.100 A

SHT31 temp/humidity: 0.002 A

MPU6050 inertial sensor: 0.003 A

GPS module: 0.045 A

Camera (when active): 0.250 A

Misc USB peripherals (LEDs, antenna amplifiers): 0.200 A

Now add them digit by digit:

Start: 1.200 A (Pi)

0.600 A = 1.800 A

0.100 A = 1.900 A

0.002 A = 1.902 A

0.003 A = 1.905 A

0.045 A = 1.950 A

0.250 A = 2.200 A

0.200 A = 2.400 A

Total peak current = 2.400 A at 5 V.

Power (Watts) = Voltage × Current = 5 V × 2.400 A = 12.000 W.

If you need the device to run for 12 hours, energy required:

Energy (Wh) = Power (W) × Time (h) = 12.000 W × 12 h = 144.000 Wh.

If you will use a 5 V power bank specified in mAh, convert:

mAh required at 5 V = (Wh ÷ V) × 1000
Compute: 144.000 Wh ÷ 5 V = 28.800 Ah = 28,800 mAh.

Account for DC-DC conversion inefficiency (typical 85% efficiency): divide by 0.85.

28,800 mAh ÷ 0.85 = 33,882.352941... mAh ≈ 34,000 mAh (round up and allow margin).

Conclusion: For the example configuration, plan a 5V battery pack with effective capacity ≥ 34,000 mAh (or battery energy ≥ 144 Wh with BMS and connectors), or provide solar trickle-charge to extend runtime.

Safety note: If you build battery packs from cells, compute for cell voltage and pack configuration and always include a BMS; never rely on raw cells without proper protection.

## 4) Mechanical & electrical assembly — step-by-step
Step 0 — Prep

Work on an anti-static mat. Verify you have standoffs to keep SBC off enclosure floor.

Label each cable and connector with tape and marker.

## Step 1 — Mount compute board

Use appropriate standoffs (M2.5 or M3 as required). Place board so connectors face final access holes in enclosure.

Affix thermal pad / heatsinks if heavy load expected.

## Step 2 — Mount battery & UPS

Install battery pack inside enclosure with vibration-damping tape/foam. Keep battery away from hot components (heat sink area).

Install UPS HAT or DC-DC booster near Pi with secure screws. Connect battery to BMS input, BMS output to DC-DC converter, then to 5V rail. Place inline fuse between BMS output and DC-DC.

Wiring snippet:

Battery pack (+) -> BMS (+) -> inline fuse -> DC-DC input (+)
Battery pack (-) -> BMS (-) -> DC-DC input (-)
DC-DC output 5V -> Raspberry Pi 5V IN (or UPS HAT)

## Step 3 — Route antennas outside

Install cable glands and route LTE & GPS antenna cables through separate glands. Use gold/plated SMA connectors. Keep GPS antenna away from LTE for less interference.

## Step 4 — Sensor wiring

Use I2C for SHT31, BME680, light sensor. Connect SDA -> SDA, SCL -> SCL, power -> 3.3V (or 5V per sensor), ground -> GND. Use pull-ups only if not already on board.

PMS7003 uses UART — connect TX/RX to Pi UART (use level shifter if needed).

MPU6050 via I2C (same bus) but consider sensor address conflicts.

Camera connects via CSI ribbon cable. Secure with lock.

Keep sensor cables short where possible; use shielded cable for long runs.

## Step 5 — Grounding

Connect chassis ground to system ground only at single point to avoid ground loops. If outdoor with lightning risk, include surge protection and proper grounding to earth if possible.

## Step 6 — Storage redundancy

Install microSD with OS, then connect external USB SSD. Set up backup policy to copy sensor logs from SD to SSD frequently. For low risk of SD corruption, use overlayfs or read-only rootfs.

## Step 7 — Close enclosure & test seals

Verify gaskets, torque screws evenly, apply silicone where necessary. Add desiccant.

5) Software: flashing, services, healthcheck & watchdog
Flash OS & initial config (Raspberry Pi example)

Flash Raspberry Pi OS (Lite) to microSD.

Boot once with keyboard/monitor or enable SSH in /boot/ssh. Set locale, timezone, change password.

sudo apt update && sudo apt upgrade -y

Install Python3, pip: sudo apt install -y python3 python3-pip git

Healthcheck HTTP endpoint (simple Python Flask)

Create /opt/edge/healthcheck.py:

#!/usr/bin/env python3
from flask import Flask, jsonify
import psutil, time
app = Flask(__name__)
start = time.time()

@app.route("/health")
def health():
    uptime = time.time() - start
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    return jsonify({"status":"ok","uptime_s":int(uptime),"cpu_pct":cpu,"mem_pct":mem,"disk_pct":disk})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


## Make executable and create systemd service /etc/systemd/system/edge-health.service:

[Unit]
Description=Edge Healthcheck
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/edge/healthcheck.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target


Enable it:

sudo systemctl daemon-reload
sudo systemctl enable --now edge-health.service

Watchdog & auto-reboot

Use hardware watchdog or systemd watchdog. For software, create a cron or systemd service that checks health endpoint and reboots if unresponsive. Example: check & reboot if /health 3 times fails.

OTA & update strategy

Keep software in git. Use a simple updater script that does git pull, runs migrations, and restarts services. Secure updates using signed commits or a CI artifact with checksum. Keep fallback image on USB SSD so if update bricks SD, system can boot from secondary media.

6) Redundancy strategies (detailed)
Power redundancy

Primary: battery pack (LiFePO4 recommended) -> UPS HAT -> device.

Secondary: solar panel + MPPT + battery charger for remote sites.

Tertiary: supercapacitor or small 12 V SLA for short bursts to ride through high current modem TX spikes.

Add fuse and TVS diodes on power lines to prevent transients.

Communication redundancy

Multi-SIM LTE with failover (two carriers), or one LTE + Wi-Fi fallback + LoRa for low-bandwidth uplink.

Use connection manager (e.g., NetworkManager or connman) with priorities and a script that switches to the next available interface if the primary fails.

Storage redundancy

Mirror critical logs to external USB SSD (daily rsync). Use log rotation and a circular buffer to avoid filling storage. Consider remote log replication to cloud if bandwidth allows.

Software redundancy / safety

Keep an alternate boot partition or USB boot image with known-good release for rollback.

Use systemd to auto-restart failed services.

Implement heartbeat messages to central server; if no heartbeat for X minutes, remote operator alerted and device can reboot.

Sensor redundancy

Duplicate critical sensors (e.g., two temperature sensors) and use outlier detection (median or majority voting) before reporting.

7) Calibration, testing & commissioning
Initial checks (bench)

Power device (without batteries for first test) via regulated 5V bench PSU. Set current limit to 3 A.

Verify voltages at each sensor header.

Boot OS, verify logs, run dmesg for errors.

Check sensors one by one (Python quick scripts to read values). e.g., i2cdetect -y 1 for I2C sensors.

Test LTE connection: sudo mmcli -L or sudo usb_modeswitch depending on modem. Ping a known server: ping -c 4 8.8.8.8.

Field test

Deploy device in final enclosure without closing it fully. Test comms at deployment location and confirm signal strengths. Calibrate sensors (PM sensor needs zero and span tests where possible). Confirm heat behavior over a few hours.

Acceptance tests

Battery discharge test: run device under normal sampling/transmit profile until battery reaches low threshold; validate BMS cut-off triggers safely.

Failover test: simulate primary comms down and verify failover. Simulate SD corruption by forcing rootfs read-only and verify device continues recording to SSD.

## 8) Troubleshooting common problems

Device not booting: check power rail voltages and inline fuse. Connect serial console to read boot messages.

SD card corruption: use industrial-grade SD cards, set vm.swappiness=10, enable overlayfs, or use read-only root to protect.

LTE modems dropping: check antenna placement, use ferrite bead on USB cable, update modem firmware, ensure SIM provisioning (APN) correct.

Sensor drift: re-calibrate sensors periodically and keep a second sensor for comparison.

## 9) Bill of Materials (example, approximate items)

Raspberry Pi 4 (4GB) — SBC

microSD (industrial) 32 GB

USB SSD 120 GB

LTE modem (USB) + external antenna

GPS module (u-blox) + antenna

SHT31 temp/humidity (I2C)

PMS7003 particulate sensor (UART)

MPU6050 IMU (I2C)

Pi Camera v2 (optional)

LiFePO4 battery pack (12,800 mAh nominal pack or configurable to meet Wh) + BMS

DC-DC step-up / UPS HAT with fuel gauge

IP66 enclosure with glands

Gasket, screws, standoffs, cable, connectors

Inline fuse, TVS diodes, surge protector (for outdoor)

(Quantities depend on your design; list the item sources and part numbers in your final BOM before ordering.)

## 10) Safety & regulatory notes

Lithium batteries can catch fire if abused. Always use BMS, fuses, and correct charge circuitry. Prefer LiFePO4 for outdoor/industrial use due to greater thermal stability.

If mounting outdoors, ensure lightning protection and proper grounding. Follow local regulations for antenna placement and RF emissions.

If device will be installed in public or critical infrastructure, include tamper detection and encrypted comms (TLS + certificate pinning).

## 11) Quick checklist for final deployment

 All sensors attached & verified on bench

 Battery sized & BMS tested; inline fuse installed

 Antennas installed, signal strength verified at site

 Healthcheck endpoint running & accessible on LAN

 Watchdog/service auto-restart configured

 Backup USB SSD receiving copies of logs

 Documentation (wiring diagram, calibration data, firmware version) stored centrally

## 🚀 CitySafeSense — Raspberry Pi 4 Edge Deployment Guide

This guide walks you through preparing a Raspberry Pi 4 to run the CitySafeSense Edge AI Inference Runtime, including:

OS setup

Installing dependencies

Installing the model + inference service

Secure MQTT configuration

Running as a systemd service or as a Docker container

Everything is optimized for Raspberry Pi 4 (ARM64 or ARMv7).

## 1. 🔧 Raspberry Pi 4 — System Preparation
✔️ Recommended OS

Use Raspberry Pi OS (64-bit):

Raspberry Pi OS Lite 64-bit (preferred)

Raspberry Pi OS Desktop 64-bit

✔️ Update the system
sudo apt update && sudo apt full-upgrade -y
sudo reboot

✔️ Essential packages
sudo apt install -y python3 python3-pip python3-venv git wget unzip mosquitto-clients

## 2. 🔐 Install TFLite Runtime (optimized for Pi 4)

TensorFlow Lite full is too heavy; Raspberry Pi uses tflite-runtime.

Determine your Python version:
python3 --version

Install TFLite Runtime wheel

For Python 3.9+ on Raspberry Pi 4 (ARM64):

# Example wheel (replace with the latest ARM64 wheel matching your version):
pip3 install https://github.com/google-coral/pycoral/releases/download/release-frogfish/tflite_runtime-2.14.0-cp39-cp39-linux_aarch64.whl


If you're running ARMv7 (32-bit), install the ARMv7 wheel instead.

## 3. 📁 Deploy CitySafeSense Files to Pi

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

## 4. ⚙️ Create Python Virtual Environment
cd ~/citysafesense
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt


If tflite_runtime was not inside requirements, install manually:

pip install tflite-runtime

## 5. 🔧 Configure MQTT Secure Connection (Recommended)
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

## 6. 🤖 Running the Model — Manual Test
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

## 7. 🔁 Running as a Persistent systemd Service (recommended)

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

## 8. 🐳 Running with Docker (optional but excellent)
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

## 9. 📊 Validate Data Flow
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

## 10. ✔️ Performance Tips for Raspberry Pi 4
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

## 11. 🧪 Troubleshooting
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


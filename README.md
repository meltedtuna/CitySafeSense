CitySafeSense
Edge-Powered Mugging Detection, Triangulation & Real-Time Public Safety Alerts

CitySafeSense is a privacy-preserving edge AI platform designed to detect muggings and violent incidents in real time, triangulate alerts across distributed devices, and notify both nearby civilians and command centers—without sending video off the device.

Built for edge devices, smart cities, public security infrastructure, and autonomous community safety systems.

🔍 Features
🎯 On-Device Threat Detection

Lightweight inference optimized for low-power hardware (Pi, Jetson, Coral).

Detects muggings, assaults, and high-risk actions.

Runs completely locally — no streaming, no cloud inference.

📡 Triangulated Incident Localization

Multiple units collaborate to determine:

Precise incident coordinates

Cross-device confidence scoring

Directional movement patterns

Reduces false positives significantly.

🚨 Real-Time Alerting

Alerts can be distributed to:

Mobile devices nearby (BLE broadcast or Wi-Fi local push)

City operators / command center

Slack, PagerDuty, Opsgenie, Email (via Alertmanager)

MQTT brokers or HTTP endpoints

📊 Fully Integrated Observability

Prometheus metrics exported by all services

Pre-built Grafana dashboards

Automatic alerting rules

🔐 Secure & Hardened

Vault-backed secrets

Non-root Docker images

Network isolation enforcement

OTA update support

🧱 Architecture Overview
┌───────────────────┐
│   Edge Device      │
│ ┌───────────────┐ │
│ │   detector     │─┐
│ └───────────────┘ │  Locally detects threats
│ ┌───────────────┐ │
│ │ triangulation │─┼→ Federated location inference
│ └───────────────┘ │
│ ┌───────────────┐ │
│ │   dispatcher  │─┘ Sends alerts + events upstream
│ └───────────────┘ │
│ ┌───────────────┐ │
│ │   heartbeat   │→ OTA, healthchecks
│ └───────────────┘ │
└───────────────────┘

┌──────────────────────────┐
│ Central Monitoring Stack │
│  Prometheus + Grafana    │
│  Alertmanager            │
└──────────────────────────┘

📦 Repository Structure
citysafesense/
 ├── src/citysafesense/        # Python package (pip-installable)
 │   ├── detector/             # Core ML inference + feature extraction
 │   ├── triangulation/        # Geospatial clustering
 │   ├── dispatcher/           # Alert routing
 │   └── heartbeat/            # OTA + health
 │
 ├── docker/                   # Hardened Dockerfiles
 ├── compose/                  # docker-compose.yml + overrides
 ├── prometheus/               # Scrape configs, rules
 ├── grafana/                  # Dashboards + provisioning
 ├── alertmanager/             # Templates, routes, start.sh
 ├── ansible/                  # Fleet deployment playbooks
 ├── systemd/                  # Unit service files
 ├── docs/                     # Setup, secrets, diagrams
 ├── tests/                    # Unit + integration tests
 ├── Makefile                  # build/run/test shortcuts
 └── README.md

🚀 Quick Start
1. Install Project (Developer Mode)
pip install -e .

2. Launch Full Stack (Dev Mode, Hot Reload)
docker compose -f docker-compose.yml -f docker-compose.override.yml up --build

3. View Metrics

Prometheus:
http://localhost:9090

Grafana (admin / admin):
http://localhost:3000

⚡ Deploying to Edge Devices
Using GitHub Actions (recommended)

Two workflows are available:

Workflow	Purpose
deploy_with_vault.yml	Vault-integrated secret retrieval + remote deploy
deploy_remote_ssh.yml	Lightweight, direct SSH deploy

Trigger on pushes to main or manually via workflow_dispatch.

Using Systemd

Copy files from systemd/ into /etc/systemd/system/, then:

sudo systemctl enable citysafesense
sudo systemctl start citysafesense

Using Ansible
ansible-playbook ansible/deploy.yml -i inventory.ini

🔐 Configuring Secrets

CitySafeSense uses Vault KV v2 for secure secret storage:

secret/data/citysafesense/alertmanager
  ├── slack_webhook
  ├── smtp_smarthost
  ├── smtp_username
  ├── smtp_password
  ├── pagerduty_key
  ├── opsgenie_key
  └── alert_email_to


For full details:
👉 See docs/secrets.md

🧪 Tests
Unit Tests
pytest -q

Integration Tests (Docker Compose)
pytest tests/integration -q

CI Integration

All tests run inside GitHub Actions.

📡 Alerting Flow
detector → triangulation → dispatcher → Alertmanager → Slack / Email / PagerDuty / Opsgenie


Custom receivers can be added via templated Alertmanager configs.

🛠 Makefile Shortcuts
Command	Action
make build	Build Docker images
make test	Run unit tests
make compose-dev	Start hot-reload service stack
make deploy	Trigger local deploy script
make clean	Remove build artifacts
🗺 Roadmap

More granular threat categories (robbery, aggression spectrum)

Distributed ledger for tamper-proof audit logs

Device-to-device mesh routing

Integration with smart street lighting / city IoT

Rust migration for triangulation engine

🤝 Contributing

Pull requests are welcome!
Before submitting, please run:

make lint
make test


If you're adding a new service, add corresponding:

Metrics endpoint

Dockerfile

Prometheus scrape config

Unit/integration tests

📜 License

This project can include any license you choose.
If you want, I can write a complete MIT, Apache 2.0, or Proprietary License file.

❤️ Acknowledgments

Thanks to everyone involved in the development of CitySafeSense — combining AI + edge computing to make public spaces safer while respecting privacy.

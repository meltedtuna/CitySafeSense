CitySafeSense — Edge AI for Urban Safety

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

Required signage & compliance notes

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


## Pushing this repo to GitHub

You can push this repository to GitHub in two ways:

1. **Using the `gh` CLI (recommended)**

```bash
# ensure gh is installed and authenticated: gh auth login
./scripts/create_and_push_repo.sh <OWNER>/<REPO>
```

2. **Manually with a Personal Access Token (PAT)**

Create a repository in the GitHub UI or use the REST API with a PAT that has `repo` and `workflow` scopes, then push:

```bash
git remote add origin git@github.com:<OWNER>/<REPO>.git
git branch -M main
git push -u origin main
```

If you want me to push on your behalf, provide a repo name and a PAT with `repo` and `workflow` scopes. (Be careful sharing tokens.)


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

The `publish-ghcr` workflow will publish the image when you push a tag matching `v*` (for example `v1.0.0`) or when you run the workflow manually via Actions → Publish Docker image to GHCR.


## Publish GHCR workflow badge

[![Publish to GHCR](https://github.com/meltedtuna/CitySafeSense/actions/workflows/publish-ghcr.yml/badge.svg)](https://github.com/meltedtuna/CitySafeSense/actions/workflows/publish-ghcr.yml)

This badge shows the latest status of the `publish-ghcr` workflow.


## Smoke workflow dispatch examples

You can run the **Smoke training & export** workflow manually via the GitHub UI (Actions → Smoke training & export → Run workflow)
or via the `gh` CLI. The workflow supports two inputs:

- `image_tag` — optional, pull a specific GHCR image tag (e.g. `v1.0.0`). If omitted, the workflow will try:
  1. the provided `image_tag` input,
  2. the latest GitHub Release tag,
  3. the latest Git tag (via `git describe --tags --abbrev=0`),
  4. fallback to `latest`.

- `build_override` — optional boolean (`true`/`false`). If `true`, forces a local build even if the image is available.

### Examples:

Run the workflow with a specific tag:
```bash
gh workflow run ci.yml --repo meltedtuna/CitySafeSense --ref main --field image_tag=v1.0.0
```

Run the workflow and force a local build:
```bash
gh workflow run ci.yml --repo meltedtuna/CitySafeSense --ref main --field build_override=true
```

Run the workflow, auto-selecting the latest release or git tag if available:
```bash
gh workflow run ci.yml --repo meltedtuna/CitySafeSense --ref main
```

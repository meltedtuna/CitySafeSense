# 📡 CitySafeSense  
### *Edge AI for Urban Safety & Mobility Anomaly Detection*

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-92%25-green)]()
[![Docker](https://img.shields.io/badge/docker-ready-blue)]()
[![Docs](https://img.shields.io/badge/docs-mkdocs-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey)]()

CitySafeSense is a **privacy-preserving edge-AI platform** that detects **abrupt movement anomalies** (e.g., forced displacement, sudden vector changes, and risky mobility patterns associated with urban muggings) using **anonymous sensors**, **secure MQTT ingestion**, and **lightweight temporal neural networks** optimized for low-cost hardware.

It is an end-to-end reference system that covers:

- Edge ML modeling (TCN-based)
- Sensor simulation (IMU + GNSS + Acoustic)
- Real-time ingestion (Mosquitto MQTT with TLS + passwords)
- Visualization + data tools
- Infrastructure + Dockerization
- API + CLI
- Documentation + whitepaper generator
- Deployment checklists for installers

---

# 🚀 Features

### 🔍 1. Edge Temporal Convolutional Network (TCN)  
Lightweight TensorFlow model for microcontrollers and edge devices.  
Detects:

- Normal walking patterns  
- Walking → entering a vehicle  
- Walking → being forced (mugging signature)  
- Sudden directional changes  
- High-acceleration displacement

### 🛰 2. Synthetic Sensor Dataset Generator  
Generates realistic multi-sensor data:

- Accelerometer (3-axis)  
- Gyroscope (3-axis)  
- GNSS speed & direction  
- Acoustic pressure spikes  

Includes augmentation:

- Gaussian noise  
- Jitter  
- Random rotations  
- Time-warp stretching  

### 🧪 3. Complete Training Pipeline  
Includes:

- Data loading  
- Augmentation  
- Batching  
- On-device quantization  
- TFLite export  

### 🧰 4. Tools  
- CLI wrapper for all subsystems  
- Synthetic data visualizer  
- Overlay comparisons (walking vs driving vs mugging)  
- Auto-export of figures to PDF

### 🔐 5. MQTT Secure Ingestion  
- Mosquitto broker  
- Password authentication enabled by default  
- TLS certificates  
- Docker Compose setup  
- Hardened configuration

### 🏙 6. Privacy-Preserving Hotspot Monitoring  
No personal data collected.  
Only anonymous aggregated motion vectors:

- Flow intensity  
- Directional shifts  
- Event probabilities  
- Density changes


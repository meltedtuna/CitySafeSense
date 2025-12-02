# Installer Checklist

1. Provision edge device (Raspberry Pi 4 or similar)
2. Install Docker & Docker Compose
3. Place TLS certs into `infra/certs/`
4. Set strong MQTT passwords in `infra/mosquitto/passwords`
5. Start stack: `docker compose up -d`
6. Verify: `mosquitto_sub -h localhost -p 8883 --cafile infra/certs/ca.crt -t 'citysafesense/#'`
7. Deploy model.tflite to device and run `src/ingest/mqtt_publisher.py` for live testing

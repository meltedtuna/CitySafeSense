"""
Simple MQTT publisher for testing ingestion; publishes synthetic frames to a topic.
"""
import time
import json
import numpy as np
import paho.mqtt.client as mqtt

def publish_loop(broker='localhost', port=1883, topic='citysafesense/sensor', fps=10):
    client = mqtt.Client()
    # Note: in production enable TLS and authentication
    client.connect(broker, port, 60)
    client.loop_start()
    try:
        while True:
            # small synthetic payload
            payload = {
                'ts': time.time(),
                'frame': np.random.randn(10).tolist()
            }
            client.publish(topic, json.dumps(payload))
            time.sleep(1.0/fps)
    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()

if __name__=='__main__':
    publish_loop()

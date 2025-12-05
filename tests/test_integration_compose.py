import subprocess, time, requests, os, sys
def wait_for_prometheus(url, timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(2)
    return False

def test_compose_smoke():
    # Requires Docker & docker compose installed in the environment where tests run.
    # This test will spin up the compose stack (detached), wait for Prometheus, query targets, then tear down.
    cmd_up = ["docker","compose","-f","docker-compose.yml","up","-d","--build"]
    cmd_down = ["docker","compose","-f","docker-compose.yml","down"]
    try:
        subprocess.check_call(cmd_up)
        assert wait_for_prometheus("http://localhost:9090/-/ready", timeout=120), "Prometheus not ready"
        # Check targets API
        r = requests.get("http://localhost:9090/api/v1/targets", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert 'data' in data
        targets = [t['labels'] for t in data['data'].get('activeTargets',[])]
        # Ensure at least one expected target present
        found = any('heartbeat' in str(t) or '8000' in str(t) for t in targets)
        assert found, f"No heartbeat target found in {targets}"
    finally:
        subprocess.check_call(cmd_down)

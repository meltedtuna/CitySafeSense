# Secrets & Vault KV Structure (CitySafeSense) — Updated (Final)

This document lists the exact GitHub Actions workflow names in this repository, the repository secrets required by each workflow, and the expected structure of the Vault KV used to store Alertmanager secrets.

---
## Workflow names (files)
- `deploy_with_vault.yml` — located at `.github/workflows/deploy_with_vault.yml`  
  Purpose: Fetches Alertmanager secrets from Vault (KV v2), writes them to files on the runner, then **securely rsyncs** the repository and secret files to a remote host and performs a remote `docker compose up`.
- `deploy_remote_ssh.yml` — located at `.github/workflows/deploy_remote_ssh.yml`  
  Purpose: A simpler remote-deploy workflow that uses `ssh-agent` or a file-key fallback to rsync the repository to a remote host and run `docker compose up` there.
- `integration.yml` — integration tests workflow; does not require deploy secrets (keeps CI integration test logic).

Both deploy workflows use the same secret names and follow the same ssh-agent + fallback pattern.

---
## Exact GitHub repository secrets (add these under Settings → Secrets and variables → Actions → New repository secret)

**Required for deploy workflows:**
- `VAULT_ADDR` — Vault server URL (e.g. `https://vault.example.com:8200`)
- `VAULT_TOKEN` — Vault token with permission to read the KV path (or use AppRole and adapt the workflow)
- `DEPLOY_SSH_PRIVATE_KEY` — Private SSH key (PEM format). The workflows load it into `ssh-agent` (preferred) or fall back to writing it to `~/.ssh/id_rsa` (only during the job).
- `DEPLOY_HOST` — Hostname or IP address of the remote deploy target (e.g. `1.2.3.4`)
- `DEPLOY_USER` — SSH user for the remote host (e.g. `ubuntu` or `csuser`)

**Optional (if you want to bypass Vault and inject secrets via GitHub Secrets):**
- `SLACK_WEBHOOK`
- `SMTP_SMARTHOST`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `PAGERDUTY_SERVICE_KEY`
- `OPSGENIE_API_KEY`
- `ALERT_EMAIL_TO`

> Note: The current `deploy_with_vault.yml` fetches secrets from Vault and writes them into `alertmanager/secrets/` on the runner. If you prefer to use GitHub Secrets instead of Vault, you can modify the workflow to write these GitHub Secrets into the same files before rsyncing to the remote host.

---
## Vault KV v2 path & expected keys

The workflows assume your Vault KV v2 secrets are at the following path and keys. Adjust `VAULT_KV_PATH` in the workflow if you store secrets elsewhere.

- **KV path (v2):** `secret/data/citysafesense/alertmanager`
- **Keys stored under that path (each key is a string value):**
  - `slack_webhook`
  - `smtp_smarthost`
  - `smtp_username`
  - `smtp_password`
  - `pagerduty_key`
  - `opsgenie_key`
  - `alert_email_to`

### Example: writing secrets to Vault (CLI)
```bash
vault kv put secret/citysafesense/alertmanager   slack_webhook="https://hooks.slack.com/services/T/..."   smtp_smarthost="smtp.example.com:587"   smtp_username="smtp-user"   smtp_password="smtp-pass"   pagerduty_key="PD_INTEGRATION_KEY"   opsgenie_key="OPSGENIE_API_KEY"   alert_email_to="alerts@example.com"
```

> The workflow uses `vault kv get -format=json` and extracts fields from `.data.data.*` (KV v2). If your Vault uses KV v1, or a different mount path, update the workflow `VAULT_KV_PATH` and `jq` extraction lines accordingly.

---
## How the ssh-agent + fallback behavior works

- The workflow first attempts to load `DEPLOY_SSH_PRIVATE_KEY` into the runner's ssh-agent using `webfactory/ssh-agent` (recommended).
- It then runs `ssh-add -l` to see whether an identity is loaded in the agent. If the agent is empty (e.g., runner environment doesn't support agent), the workflow **falls back** to writing the private key to `~/.ssh/id_rsa` with `chmod 600` (restricted permissions). This fallback key is used only during the job and is not printed to logs.
- The workflow sets an environment variable `SSH_SSH_ARGS` (exported to `GITHUB_ENV`) which is used consistently in later steps to pass either an empty value (agent-based auth) or `-i ~/.ssh/id_rsa -o StrictHostKeyChecking=no` (file key) to `ssh`, `scp`, and `rsync` steps. This ensures consistent behavior across all SSH invocations in the workflow.

---
## Security best practices and notes

- **Do not commit secret files.** Ensure `alertmanager/secrets/*` is in `.gitignore`.
- **Prefer short-lived Vault AppRole or GitHub OIDC** over long-lived Vault tokens. You can adapt the workflow to use AppRole or OIDC if required.
- **Rotate SSH keys and Vault tokens** periodically and update the GitHub Secrets accordingly.
- **On the remote host**, ensure `DEPLOY_USER` has the correct permissions to run `docker compose` or use a `sudo` wrapper. Ensure the remote machine is secured and patched.

---
## Troubleshooting quick tips

- If the workflow fails to fetch secrets: verify `VAULT_ADDR`, `VAULT_TOKEN`, `VAULT_KV_PATH`, and Vault policies for the token.
- If SSH auth fails: ensure the public key corresponding to `DEPLOY_SSH_PRIVATE_KEY` is in `~/.ssh/authorized_keys` for `DEPLOY_USER` on the remote host.
- If rsync/scp fails due to permission: ensure `DEPLOY_USER` has write access to `REMOTE_DIR` (default `/opt/citysafesense`) or adjust `REMOTE_DIR` in the workflow.

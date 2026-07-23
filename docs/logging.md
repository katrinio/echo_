## Docker Build Cache Cleanup Logging

This repo includes a small, repo-owned setup for Docker build cache cleanup logs:

- cleanup script: [scripts/docker-build-cache-prune.sh](/Users/katrin/PycharmProjects/personal/echo_/scripts/docker-build-cache-prune.sh)
- systemd unit: [ops/systemd/docker-build-cache-prune.service](/Users/katrin/PycharmProjects/personal/echo_/ops/systemd/docker-build-cache-prune.service)
- systemd env example: [ops/systemd/docker-build-cache-prune.env.example](/Users/katrin/PycharmProjects/personal/echo_/ops/systemd/docker-build-cache-prune.env.example)
- Alloy config: [ops/alloy/docker-build-cache-prune.alloy](/Users/katrin/PycharmProjects/personal/echo_/ops/alloy/docker-build-cache-prune.alloy)
- Alloy env example: [ops/alloy/docker-build-cache-prune.env.example](/Users/katrin/PycharmProjects/personal/echo_/ops/alloy/docker-build-cache-prune.env.example)
- Grafana dashboard: [ops/grafana/docker-build-cache-prune-dashboard.json](/Users/katrin/PycharmProjects/personal/echo_/ops/grafana/docker-build-cache-prune-dashboard.json)

### What it does

- The cleanup script writes short, human-readable `INFO`, `WARN`, and `ERROR` lines.
- `INFO` goes to stdout.
- `WARN` and `ERROR` go to stderr.
- The systemd service sends both stdout and stderr to journald.
- Grafana Alloy reads only `docker-build-cache-prune.service` journal entries and forwards them to Loki.
- Loki labels added by Alloy:
  - `job="docker-cache-cleanup"`
  - `service="docker-build-cache-prune"`
  - `host="<current hostname>"`

Cache sizes stay inside the log message and are not promoted to Loki labels.

### Install

1. Make the script executable:

```bash
chmod +x scripts/docker-build-cache-prune.sh
```

2. Create the systemd environment file from the example and set the repo path:

```bash
sudo cp ops/systemd/docker-build-cache-prune.env.example /etc/default/docker-build-cache-prune
sudoedit /etc/default/docker-build-cache-prune
```

Set:

```text
REPO_DIR=/absolute/path/to/echo_
```

3. Install the systemd unit:

```bash
sudo cp ops/systemd/docker-build-cache-prune.service /etc/systemd/system/docker-build-cache-prune.service
sudo systemctl daemon-reload
```

4. Install Grafana Alloy if it is not already installed, then copy the Alloy config from this repo:

```bash
sudo cp ops/alloy/docker-build-cache-prune.alloy /etc/alloy/config.alloy
```

5. Create the Alloy environment file and set the Loki endpoint:

```bash
sudo cp ops/alloy/docker-build-cache-prune.env.example /etc/default/alloy
sudoedit /etc/default/alloy
```

Required:

```text
LOKI_URL=https://your-loki.example/loki/api/v1/push
```

Optional if your Loki deployment requires them:

```text
LOKI_TENANT_ID=your-tenant-id
LOKI_USERNAME=your-username
LOKI_PASSWORD=your-password
```

If you need tenant ID or basic auth, uncomment the optional block in [ops/alloy/docker-build-cache-prune.alloy](/Users/katrin/PycharmProjects/personal/echo_/ops/alloy/docker-build-cache-prune.alloy).

6. Allow Alloy to read journald:

```bash
sudo usermod -aG adm,systemd-journal alloy
sudo systemctl restart alloy
```

7. Import the Grafana dashboard from [ops/grafana/docker-build-cache-prune-dashboard.json](/Users/katrin/PycharmProjects/personal/echo_/ops/grafana/docker-build-cache-prune-dashboard.json) and select your Loki data source for `${DS_LOKI}`.

### Verify

1. Run the cleanup service:

```bash
sudo systemctl start docker-build-cache-prune.service
```

2. Check the unit logs in journald:

```bash
journalctl -u docker-build-cache-prune.service -n 50 --no-pager
```

You should see lines like:

```text
2026-07-15 04:30:01 INFO  Starting Docker build cache cleanup
2026-07-15 04:30:02 INFO  Build cache before cleanup: 17.4GB
2026-07-15 04:30:12 INFO  Reclaimed: 16.7GB
2026-07-15 04:30:12 INFO  Cleanup completed successfully in 10s
```

3. Confirm Alloy is healthy:

```bash
sudo systemctl status alloy
```

4. In Grafana Explore, query:

```logql
{job="docker-cache-cleanup", service="docker-build-cache-prune"}
```

5. Open the imported dashboard and verify:

- `All Cleanup Logs` shows all runs.
- `ERROR Logs` shows only failures.
- `Latest Successful Cleanup` shows the most recent successful completion.

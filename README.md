# Docker Autoheal

Monitor and automatically restart unhealthy Docker containers.

# How to Use

### Docker Image Tags

The Docker image is available in multiple tag formats:

- **`main` (Development Build)**
  - Tracks the latest commit on the `main` branch.
  - **Recommended for:** Developers and testers.
  - **Note:** Updated with every commit; may include breaking changes.

- **`latest` (Stable Release)**
  - Points to the most recent stable release.
  - **Recommended for:** General use in production environments.

  > **Note**: Currently, there is no `latest` tag available. Please check back for updates on the availability of this tag.

- **`A.B.C.D` (Versioned Releases)**
  - Provides specific versioned releases for consistency.
  - **Recommended for:** Environments that require version control.

  > **Note**: Currently, there are no versioned tags (e.g., `A.B.C.D`) available. When they are published, each will remain fixed, ensuring a stable and unchanging image for users needing version control.

## Installation Options

You can pull the Docker image from either of the following registries:

- `ghcr.io/journeydocker/docker-autoheal:<tagname>`
- `journeyover/docker-autoheal:<tagname>`

### 1. Running with Docker CLI

#### Using UNIX Socket
```bash
docker run -d \
    --name autoheal \
    --restart=always \
    -e AUTOHEAL_CONTAINER_LABEL=all \
    -v /var/run/docker.sock:/var/run/docker.sock \
    journeyover/docker-autoheal:main
```

#### Using TCP Socket
```bash
docker run -d \
    --name autoheal \
    --restart=always \
    -e AUTOHEAL_CONTAINER_LABEL=all \
    -e DOCKER_SOCK=tcp://$HOST:$PORT \
    -v /path/to/certs/:/certs/:ro \
    journeyover/docker-autoheal:main
```

#### Using TCP with mTLS (HTTPS)
```bash
docker run -d \
    --name autoheal \
    --restart=always \
    --tlscacert=/certs/ca.pem \
    --tlscert=/certs/client-cert.pem \
    --tlskey=/certs/client-key.pem \
    -e AUTOHEAL_CONTAINER_LABEL=all \
    -e DOCKER_HOST=tcp://$HOST:2376 \
    -e DOCKER_SOCK=tcps://$HOST:2376 \
    -e DOCKER_TLS_VERIFY=1 \
    -v /path/to/certs/:/certs/:ro \
    journeyover/docker-autoheal:main
```
The required certificate files inside the container:
- `ca.pem`
- `client-cert.pem`
- `client-key.pem`

> Refer to [Docker's documentation](https://docs.docker.com/engine/security/https/) for configuring TCP with mTLS.

### 2. Docker Compose Example

```yaml
services:
  autoheal:
    image: journeyover/docker-autoheal:main
    restart: always
    network_mode: none
    environment:
      - AUTOHEAL_CONTAINER_LABEL=autoheal-app
    deploy:
      replicas: 1
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /var/run/docker.sock:/var/run/docker.sock
```

### 3. Using in Your Container Image

You can enable autoheal by choosing one of the following methods:

- **Label-based**: Add `autoheal=true` to your container labels.
- **Environment Variable**: Set `AUTOHEAL_CONTAINER_LABEL=all` to monitor all running containers.
- **Custom Label**: Use `AUTOHEAL_CONTAINER_LABEL` with an existing container label that has the value `true`.

> **Note:** Ensure that your Docker images have a `HEALTHCHECK` configured. See [Docker's Healthcheck Reference](https://docs.docker.com/engine/reference/builder/#healthcheck) for details.

## Optional Container Labels
| Label | Description |
| --- | --- |
| `autoheal.stop.timeout=20` | Overrides stop timeout (in seconds) for container restarts. |

## Environment Defaults
| Variable | Description |
| --- | --- |
| `AUTOHEAL_CONTAINER_LABEL=autoheal` | Monitors containers with the specified label set to `true`. |
| `AUTOHEAL_INTERVAL=5` | Checks container health every 5 seconds. |
| `AUTOHEAL_START_PERIOD=0` | Initial delay before the first health check (in seconds). |
| `AUTOHEAL_DEFAULT_STOP_TIMEOUT=10` | Maximum time (in seconds) Docker waits before forcefully stopping a container. |
| `AUTOHEAL_ONLY_MONITOR_RUNNING=false` | If `true`, only running containers are monitored (paused containers are ignored). |
| `AUTOHEAL_RESTART_THRESHOLD=5` | The maximum number of times a container can be restarted within the `AUTOHEAL_RESTART_WINDOW` before it is stopped. |
| `AUTOHEAL_RESTART_WINDOW=600` | The time window (in seconds) within which the restart count is tracked. If the container is restarted more than `AUTOHEAL_RESTART_THRESHOLD` times within this window, it will be stopped. |
| `DOCKER_SOCK=/var/run/docker.sock` | Unix socket path for Docker API requests. |
| `CURL_TIMEOUT=30` | Maximum time (in seconds) for `curl` requests to the Docker API. |
| `WEBHOOK_URL=""` | Sends a webhook notification if a container is restarted or fails to restart. |

## Local Testing & Development

To build and run locally:

```bash
docker buildx build -t autoheal .

docker run -d \
    -e AUTOHEAL_CONTAINER_LABEL=all \
    -v /var/run/docker.sock:/var/run/docker.sock \
    autoheal
```

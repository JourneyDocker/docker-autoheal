# Stage 0: Base
FROM python:3.14.3-alpine AS base

# Set the working directory
WORKDIR /app

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    AUTOHEAL_CONTAINER_LABEL=autoheal \
    AUTOHEAL_START_PERIOD=0 \
    AUTOHEAL_INTERVAL=5 \
    AUTOHEAL_DEFAULT_STOP_TIMEOUT=10 \
    AUTOHEAL_RESTART_THRESHOLD=5 \
    AUTOHEAL_RESTART_WINDOW=600 \
    DOCKER_SOCK=/var/run/docker.sock \
    CURL_TIMEOUT=30 \
    WEBHOOK_URL="" \
    WEBHOOK_JSON_ENTRY="text" \
    APPRISE_URL="" \
    POST_RESTART_SCRIPT=""

# Stage 1: Build
FROM base AS build

# Create a Python virtual environment
RUN python -m venv /opt/venv

# Upgrade pip and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY autoheal/ /app/autoheal/

# Stage 2: Final
FROM base AS final

# Install runtime system dependencies
RUN apk add --no-cache tzdata procps

# Copy the virtual environment and application code from the build stage
COPY --from=build /opt/venv /opt/venv
COPY --from=build /app/autoheal /app/autoheal/

# Set the entrypoint and default command
ENTRYPOINT ["python", "-m", "autoheal"]
CMD ["autoheal"]

# Configure the health check
HEALTHCHECK --interval=5s CMD pgrep -f python || exit 1

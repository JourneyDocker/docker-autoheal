FROM python:3.14.2-alpine

# Install required packages
RUN apk add --no-cache tzdata procps

# Set working directory
WORKDIR /app

# Copy source code and build files
COPY autoheal/ /app/autoheal/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install -r requirements.txt

# Environment variables
ENV AUTOHEAL_CONTAINER_LABEL=autoheal \
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

# Health check to ensure the process is running
HEALTHCHECK --interval=5s CMD pgrep -f python || exit 1

# Set entrypoint and default command
ENTRYPOINT ["python", "-m", "autoheal"]
CMD ["autoheal"]

FROM alpine:3.22

# Install required packages
RUN apk add --no-cache curl jq tzdata

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
    WEBHOOK_JSON_KEY="content" \
    APPRISE_URL="" \
    POST_RESTART_SCRIPT=""

# Copy entrypoint script
COPY docker-entrypoint /

# Health check to ensure the process is running
HEALTHCHECK --interval=5s CMD pgrep -f autoheal || exit 1

# Set entrypoint and default command
ENTRYPOINT ["/docker-entrypoint"]
CMD ["autoheal"]

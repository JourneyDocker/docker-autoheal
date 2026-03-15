"""Configuration management for Docker Autoheal."""

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    """Configuration class for environment variables."""

    docker_sock: str = field(default_factory=lambda: os.getenv("DOCKER_SOCK", "/var/run/docker.sock"))
    curl_timeout: int = field(default_factory=lambda: int(os.getenv("CURL_TIMEOUT", "30")))
    webhook_url: str = field(default_factory=lambda: os.getenv("WEBHOOK_URL", ""))
    webhook_json_entry: str = field(default_factory=lambda: os.getenv("WEBHOOK_JSON_ENTRY", "text"))
    apprise_url: str = field(default_factory=lambda: os.getenv("APPRISE_URL", ""))
    post_restart_script: str = field(default_factory=lambda: os.getenv("POST_RESTART_SCRIPT", ""))
    autoheal_container_label: str = field(default_factory=lambda: os.getenv("AUTOHEAL_CONTAINER_LABEL", "autoheal"))
    autoheal_start_period: int = field(default_factory=lambda: int(os.getenv("AUTOHEAL_START_PERIOD", "0")))
    autoheal_interval: int = field(default_factory=lambda: int(os.getenv("AUTOHEAL_INTERVAL", "5")))
    autoheal_default_stop_timeout: int = field(default_factory=lambda: int(os.getenv("AUTOHEAL_DEFAULT_STOP_TIMEOUT", "10")))
    autoheal_only_monitor_running: bool = field(default_factory=lambda: os.getenv("AUTOHEAL_ONLY_MONITOR_RUNNING", "false").lower() == "true")
    autoheal_restart_threshold: int = field(default_factory=lambda: int(os.getenv("AUTOHEAL_RESTART_THRESHOLD", "5")))
    autoheal_restart_window: int = field(default_factory=lambda: int(os.getenv("AUTOHEAL_RESTART_WINDOW", "600")))
    log_level: int = field(default_factory=lambda: int(os.getenv("LOG_LEVEL", "1")))  # 1=INFO, 2=DEBUG

    @property
    def http_endpoint(self) -> str:
        """Determine the HTTP endpoint based on DOCKER_SOCK."""
        if self.docker_sock.startswith("tcp://"):
            return self.docker_sock.replace("tcp://", "http://", 1)
        elif self.docker_sock.startswith("tcps://"):
            return self.docker_sock.replace("tcps://", "https://", 1)
        else:
            return "http://localhost"

    @property
    def unix_sock(self) -> str:
        """Return unix socket path if applicable."""
        if not self.docker_sock.startswith(("tcp://", "tcps://")):
            return self.docker_sock
        return ""

    @property
    def ca_cert(self) -> str:
        """CA cert path for TLS."""
        return "/certs/ca.pem" if self.docker_sock.startswith("tcps://") else ""

    @property
    def client_key(self) -> str:
        """Client key path for TLS."""
        return "/certs/client-key.pem" if self.docker_sock.startswith("tcps://") else ""

    @property
    def client_cert(self) -> str:
        """Client cert path for TLS."""
        return "/certs/client-cert.pem" if self.docker_sock.startswith("tcps://") else ""

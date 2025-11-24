"""Docker API interaction functions."""

import docker
from .config import Config
from .logging_utils import get_logger

logger = get_logger()


def get_docker_client(config: Config) -> docker.DockerClient:
    """Get Docker client."""
    kwargs = {}
    if config.unix_sock:
        kwargs["base_url"] = f"unix://{config.unix_sock}"
    elif config.docker_sock.startswith("tcp://"):
        kwargs["base_url"] = config.docker_sock
    elif config.docker_sock.startswith("tcps://"):
        tls_config = docker.tls.TLSConfig(
            ca_cert=config.ca_cert,
            client_cert=(config.client_cert, config.client_key),
            verify=True
        )
        kwargs["base_url"] = config.docker_sock
        kwargs["tls"] = tls_config
    else:
        pass  # default
    return docker.DockerClient(**kwargs)


def get_container_info(config: Config) -> list:
    """Get list of unhealthy containers."""
    client = get_docker_client(config)
    filters = {"health": ["unhealthy"]}
    if config.autoheal_container_label != "all":
        filters["label"] = [f"{config.autoheal_container_label}=true"]
    if config.autoheal_only_monitor_running:
        filters["status"] = ["running"]
    return client.containers.list(filters=filters)


def restart_container(container_id: str, timeout: int, config: Config) -> bool:
    """Restart a container."""
    client = get_docker_client(config)
    try:
        container = client.containers.get(container_id)
        container.restart(timeout=timeout)
        return True
    except docker.errors.APIError:
        return False


def stop_container(container_id: str, timeout: int, config: Config) -> bool:
    """Stop a container."""
    client = get_docker_client(config)
    try:
        container = client.containers.get(container_id)
        container.stop(timeout=timeout)
        return True
    except docker.errors.APIError:
        return False
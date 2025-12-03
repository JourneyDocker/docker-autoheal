"""Health monitoring logic."""

import threading
from .config import Config
from .docker_api import get_container_info, restart_container, stop_container
from .restart_tracker import RestartTracker
from .notifications import notify_webhook, notify_apprise, notify_post_restart_script
from .logging_utils import get_logger

logger = get_logger()


def monitor_containers(config: Config, shutdown_event: threading.Event):
    """Main monitoring loop."""
    tracker = RestartTracker(config)

    logger.info("Starting container health monitoring")

    while not shutdown_event.is_set():
        try:
            containers = get_container_info(config)

            for container in containers:
                if shutdown_event.is_set():
                    break
                if container.labels.get("autoheal") == "False":
                    continue

                container_id = container.id
                container_name = container.name
                container_name = container_name.lstrip("/")
                container_state = container.status
                stop_timeout = container.labels.get("autoheal.stop.timeout", str(config.autoheal_default_stop_timeout))

                short_id = container_id[:12]

                if not container_name:
                    logger.warning(f"Container name of ({short_id}) is null - don't restart")
                    continue

                if container_state == "restarting":
                    logger.info(f"Container {container_name} ({short_id}) found to be restarting - don't restart")
                    continue

                if tracker.should_stop_container(container_id):
                    logger.warning(f"Container {container_name} ({short_id}) exceeded restart threshold - Stopping")
                    if stop_container(container_id, int(stop_timeout), config):
                        logger.info(f"Successfully stopped container {container_name} ({short_id})")
                        notify_webhook(f"Container {container_name} ({short_id}) exceeded restart threshold. Stopped!", config)
                    else:
                        logger.error(f"Failed to stop container {container_name} ({short_id})")
                        notify_webhook(f"Container {container_name} ({short_id}) exceeded restart threshold. Failed to stop!", config)
                else:
                    logger.info(f"Container {container_name} ({short_id}) found to be unhealthy - Restarting")
                    if restart_container(container_id, int(stop_timeout), config):
                        logger.info(f"Successfully restarted container {container_name} ({short_id})")
                        notify_webhook(f"Container {container_name} ({short_id}) found to be unhealthy. Restarted!", config)
                    else:
                        logger.error(f"Failed to restart container {container_name} ({short_id})")
                        notify_webhook(f"Container {container_name} ({short_id}) found to be unhealthy. Failed to restart!", config)

                notify_apprise(f"Container {container_name} ({short_id}) action taken", config)
                notify_post_restart_script(container_name, short_id, container_state, int(stop_timeout), config)

        except Exception as e:
            logger.exception(f"Unexpected error in monitoring loop: {e}")

        if not shutdown_event.wait(config.autoheal_interval):
            continue  # timeout, continue loop
        else:
            break  # event set

    logger.info("Container health monitoring stopped")
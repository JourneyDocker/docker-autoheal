"""Notification handling for webhooks and Apprise."""

import json
import requests
from .config import Config
from .logging_utils import get_logger

logger = get_logger()


def notify_webhook(message: str, config: Config):
    """Send webhook notification."""
    if not config.webhook_url:
        return

    payload = {config.webhook_json_entry: message}
    try:
        requests.post(config.webhook_url, json=payload, timeout=30)
        logger.debug("Sent webhook notification")
    except requests.RequestException as e:
        logger.error(f"Failed to send webhook: {e}")


def notify_apprise(message: str, config: Config):
    """Send Apprise notification."""
    if not config.apprise_url:
        return

    payload = {"title": "Autoheal", "body": message}
    try:
        requests.post(config.apprise_url, json=payload, timeout=30)
        logger.debug("Sent Apprise notification")
    except requests.RequestException as e:
        logger.error(f"Failed to send Apprise: {e}")


def notify_post_restart_script(container_name: str, container_short_id: str, container_state: str, timeout: int, config: Config):
    """Execute post-restart script."""
    if not config.post_restart_script:
        return

    import subprocess
    try:
        subprocess.run([config.post_restart_script, container_name, container_short_id, container_state, str(timeout)], check=True)
        logger.debug("Executed post-restart script")
    except subprocess.CalledProcessError as e:
        logger.error(f"Post-restart script failed: {e}")
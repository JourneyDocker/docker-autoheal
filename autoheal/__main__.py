"""Main entry point for Docker Autoheal."""

import signal
import sys
import time
import os
import threading
from .config import Config
from .health_monitor import monitor_containers
from .logging_utils import setup_logging


def signal_handler(signum, frame, shutdown_event):
    """Handle SIGTERM and SIGINT."""
    logger.info(f"Received signal {signum}, shutting down gracefully")
    shutdown_event.set()


def main():
    """Main function."""
    config = Config()
    logger = setup_logging(config.log_level)

    logger.info(f"Docker Autoheal v{__import__('autoheal').__version__} starting up")
    logger.info("Configuration:")
    for key, value in config.__dict__.items():
        if key.lower() == 'webhook_url':
            # Mask sensitive URLs
            str_value = str(value)
            if str_value:
                masked_value = str_value[:20] + '...' if len(str_value) > 20 else '***'
            else:
                masked_value = str_value
        else:
            masked_value = str(value)
        logger.info(f"  {key.upper()}={masked_value}")

    if config.unix_sock and not os.path.exists(config.docker_sock):
        logger.error("Unix socket is currently not available")
        sys.exit(1)

    shutdown_event = threading.Event()
    signal.signal(signal.SIGTERM, lambda signum, frame: signal_handler(signum, frame, shutdown_event))
    signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, shutdown_event))

    if config.autoheal_start_period > 0:
        logger.info(f"Waiting {config.autoheal_start_period} second(s) before starting monitoring")
        time.sleep(config.autoheal_start_period)

    monitor_containers(config, shutdown_event)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "autoheal":
        main()
    else:
        # Exec other commands
        os.execvp(sys.argv[1], sys.argv[1:])
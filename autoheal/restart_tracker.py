"""Restart tracking for containers."""

import os
import time
from .config import Config


class RestartTracker:
    """Tracks restart counts and timestamps for containers."""

    def __init__(self, config: Config):
        self.config = config
        self.tracker_file = "/tmp/autoheal_restart_tracker.txt"
        if not os.path.exists(self.tracker_file):
            with open(self.tracker_file, "w") as f:
                pass

    def get_restart_info(self, container_id: str) -> tuple[int, int]:
        """Get first restart time and count for a container."""
        with open(self.tracker_file, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3 and parts[0] == container_id:
                    return int(parts[1]), int(parts[2])
        return int(time.time()), 0

    def update_restart_info(self, container_id: str, first_time: int, count: int):
        """Update restart info for a container."""
        lines = []
        with open(self.tracker_file, "r") as f:
            lines = f.readlines()

        # Remove existing entry
        lines = [line for line in lines if not line.startswith(container_id + " ")]

        # Add new entry
        lines.append(f"{container_id} {first_time} {count}\n")

        with open(self.tracker_file, "w") as f:
            f.writelines(lines)

    def should_stop_container(self, container_id: str) -> bool:
        """Check if container should be stopped based on restart threshold."""
        current_time = int(time.time())
        first_time, count = self.get_restart_info(container_id)

        if current_time - first_time > self.config.autoheal_restart_window:
            first_time = current_time
            count = 0

        count += 1

        if count >= self.config.autoheal_restart_threshold:
            return True

        self.update_restart_info(container_id, first_time, count)
        return False
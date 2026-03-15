"""Restart tracking for containers."""

import os
import time
import fcntl
from .config import Config


class RestartTracker:
    """Tracks restart counts and timestamps for containers."""

    def __init__(self, config: Config):
        self.config = config
        self.tracker_file = "/tmp/autoheal_restart_tracker.txt"
        # Ensure file exists
        with open(self.tracker_file, "a") as f:
            pass

    def get_restart_info(self, container_id: str) -> tuple[int, int]:
        """Get first restart time and count for a container."""
        with open(self.tracker_file, "r") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Shared lock for reading
            try:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 3 and parts[0] == container_id:
                        return int(parts[1]), int(parts[2])
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return int(time.time()), 0

    def update_restart_info(self, container_id: str, first_time: int, count: int):
        """Update restart info for a container."""
        with open(self.tracker_file, "r+") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock
            try:
                lines = f.readlines()

                # Remove existing entry
                lines = [line for line in lines if not line.startswith(container_id + " ")]

                # Add new entry
                lines.append(f"{container_id} {first_time} {count}\n")

                f.seek(0)
                f.truncate()
                f.writelines(lines)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Unlock

    def should_stop_container(self, container_id: str) -> bool:
        """Check if container should be stopped based on restart threshold."""
        current_time = int(time.time())
        first_time, count = self.get_restart_info(container_id)

        if current_time - first_time > self.config.autoheal_restart_window:
            first_time = current_time
            count = 0

        count += 1

        self.update_restart_info(container_id, first_time, count)

        return count >= self.config.autoheal_restart_threshold

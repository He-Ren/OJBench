import time
import math

def format_time(seconds: float) -> str:
    """
    Convert a time duration in seconds to a human-readable string with automatic unit scaling.

    Args:
        seconds (float): Time duration in seconds.

    Returns:
        str: A string formatted in hours (h), minutes (m), or seconds (s) with two decimal places.
             Examples: '1.50h', '5.00m', '30.00s'.
    """
    if seconds is None or math.isnan(seconds):
        return "??"
    # More than or equal to 1 hour
    if seconds >= 3600:
        return f"{seconds / 3600:.2f}h"
    # More than or equal to 1 minute
    if seconds >= 60:
        return f"{seconds / 60:.2f}m"
    # Seconds
    return f"{seconds:.2f}s"

class ProgressTracker:
    """
    ProgressTracker: A utility to track and report iteration progress.

    Attributes:
        total (int): Total number of iterations expected.
        n (int): Number of iterations completed.
        start_time (float): Time when tracking started.
    """

    def __init__(self, total: int):
        """
        Initialize the tracker.

        Args:
            total (int): Total number of steps to track. Defaults to 1 if falsy.
        """
        self.total = total or 1
        self.n = 0
        self.start_time = time.time()

    def update(self, step: int = 1):
        """
        Increment the count of completed iterations.

        Args:
            step (int): Number of iterations to add. Defaults to 1.
        """
        self.n += step

    def get_progress(self) -> str:
        """
        Return a formatted progress string including current count, percentage,
        average time per iteration, elapsed time, and estimated remaining time with scaled units.

        Format:
            "Progress: {current}/{total} ({percent:.2f}%) | "
            "Elapsed: {elapsed_str} | Avg: {avg_str}/iter | ETA: {eta_str}"

        Returns:
            str: Progress summary.
        """
        current = self.n
        percent = (current / self.total) * 100

        # Compute elapsed time
        elapsed = time.time() - self.start_time
        elapsed_str = format_time(elapsed)

        # Compute average time per iteration
        avg_iter = elapsed / current if current else 0.0
        avg_str = format_time(avg_iter)

        # Estimate remaining time
        rem_iters = max(self.total - current, 0)
        eta_sec = avg_iter * rem_iters if current else 0.0
        eta_str = format_time(eta_sec)

        return (
            f"Progress: {current}/{self.total} ({percent:.2f}%) | "
            f"Elapsed: {elapsed_str} | Avg: {avg_str}/iter | ETA: {eta_str}"
        )

    def get_dict(self) -> dict:
        """
        Return raw progress data for programmatic use.

        Returns:
            dict: {
                "current": int,
                "total": int,
                "percent": float,
                "elapsed_seconds": float,
                "avg_time_per_iter": float,
                "eta_seconds": float
            }
        """
        elapsed = time.time() - self.start_time
        avg_iter = elapsed / self.n if self.n else 0.0
        eta_sec = avg_iter * (self.total - self.n) if self.n else 0.0

        return {
            "current": self.n,
            "total": self.total,
            "percent": round((self.n / self.total) * 100, 4),
            "elapsed_seconds": elapsed,
            "avg_time_per_iter": avg_iter,
            "eta_seconds": eta_sec,
        }
    
    def is_complete(self) -> bool:
        """
        Check if the progress has reached or exceeded the total.

        Returns:
            bool: True if all iterations are completed, False otherwise.
        """
        return self.n >= self.total

import shutil
import os

def check_disk_space(required_bytes: int, path: str = ".") -> bool:
    """
    Checks if there is enough free disk space on the volume containing `path`.
    Returns True if space is sufficient, False otherwise.
    """
    try:
        # Create directory if it doesn't exist so we can get its mount point's usage
        os.makedirs(path, exist_ok=True)
        usage = shutil.disk_usage(path)
        # Add a 10% safety buffer
        required_with_buffer = required_bytes * 1.10
        if usage.free < required_with_buffer:
            print(f"WARNING: Insufficient disk space on {path}.")
            print(f"  Required: {required_with_buffer / (1024**3):.2f} GB (incl. 10% buffer)")
            print(f"  Available: {usage.free / (1024**3):.2f} GB")
            return False
        return True
    except Exception as e:
        print(f"WARNING: Could not determine disk space for {path}: {e}")
        # In case of error (e.g. permission issues in restricted env), return True to avoid hard-blocking
        # unless strict enforcement is desired.
        return True

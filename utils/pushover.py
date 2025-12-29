"""Pushover notification utility with fallback logging."""

import os
import requests
from datetime import datetime
from pathlib import Path

# Configuration
FALLBACK_LOG_PATH = "logs/push_notifications_fallback.log"


def push(text: str) -> bool:
    """
    Send a push notification via Pushover API.

    Args:
        text: The message text to send

    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    try:
        token = os.getenv("PUSHOVER_TOKEN")
        user = os.getenv("PUSHOVER_USER")

        if not token or not user:
            print("ERROR: PUSHOVER_TOKEN or PUSHOVER_USER not set in environment")
            _log_to_fallback(text, "Missing credentials")
            return False

        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": token,
                "user": user,
                "message": text,
            },
            timeout=10
        )

        if response.status_code == 200:
            print(f"✓ Push notification sent successfully: {text[:50]}...")
            return True
        else:
            error_msg = f"Status {response.status_code}: {response.text}"
            print(f"ERROR: Push notification failed with {error_msg}")
            _log_to_fallback(text, error_msg)
            return False

    except requests.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        print(f"ERROR: Failed to send push notification: {error_msg}")
        _log_to_fallback(text, error_msg)
        return False
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"ERROR: Failed to send push notification: {error_msg}")
        _log_to_fallback(text, error_msg)
        return False


def _log_to_fallback(message: str, error: str) -> None:
    """
    Log failed push notifications to a fallback file.

    Args:
        message: The message that failed to send
        error: The error message describing why it failed
    """
    try:
        log_path = Path(FALLBACK_LOG_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] ERROR: {error}\nMessage: {message}\n{'-' * 80}\n"

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)

        print(f"✓ Notification logged to fallback file: {log_path}")

    except Exception as e:
        print(f"ERROR: Failed to write to fallback log: {str(e)}")

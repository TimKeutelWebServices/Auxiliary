import json
from datetime import datetime
from pathlib import Path


def _get_timestamp_file() -> Path:
    """Get the timestamp tracking file path."""
    return Path("last_fetch_timestamp.json")


def get_last_fetch_timestamp(place_id: str) -> datetime | None:
    """Get the last fetch timestamp for a specific place_id."""
    timestamp_file = _get_timestamp_file()
    if not timestamp_file.exists():
        return None
    
    try:
        with timestamp_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
            timestamp_str = data.get(place_id)
            if timestamp_str:
                return datetime.fromisoformat(timestamp_str)
    except (json.JSONDecodeError, IOError, ValueError):
        pass
    
    return None


def save_last_fetch_timestamp(place_id: str, timestamp: datetime | None = None) -> None:
    """Save the last fetch timestamp for a specific place_id."""
    if timestamp is None:
        timestamp = datetime.now()
    
    timestamp_file = _get_timestamp_file()
    
    # Load existing data
    data = {}
    if timestamp_file.exists():
        try:
            with timestamp_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    # Update with new timestamp
    data[place_id] = timestamp.isoformat()
    
    # Save back
    try:
        with timestamp_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except IOError:
        pass  # Silently fail if can't write

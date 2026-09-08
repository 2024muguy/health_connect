"""
HealthConnect AI - Helper Functions
====================================
General utility helpers.

Features:
- ID generation
- Date/time formatting
- JSON handling
- String manipulation
- Data conversion
"""

import json
import uuid
import random
import string
from datetime import datetime, date, timezone, timedelta
from typing import Optional, Any, Dict, List
import hashlib

from config.logging_config import get_logger

logger = get_logger(__name__)


def generate_id(prefix: str = "", length: int = 8) -> str:
    """
    Generate a unique ID with optional prefix.
    
    Args:
        prefix: ID prefix (e.g., "APT", "PAT", "CONV")
        length: Length of random portion
        
    Returns:
        str: Generated ID
    """
    random_part = uuid.uuid4().hex[:length].upper()
    
    if prefix:
        return f"{prefix.upper()}-{random_part}"
    
    return random_part


def generate_short_id(length: int = 6) -> str:
    """
    Generate a short random ID.
    
    Args:
        length: ID length
        
    Returns:
        str: Short ID
    """
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(random.choices(alphabet, k=length))


def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string.
    
    Args:
        dt: Datetime object
        format: Output format
        
    Returns:
        str: Formatted datetime
    """
    if not dt:
        return ""
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.strftime(format)


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """
    Parse datetime string to datetime object.
    Supports multiple formats.
    
    Args:
        dt_str: Datetime string
        
    Returns:
        Optional[datetime]: Parsed datetime or None
    """
    if not dt_str:
        return None
    
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    
    logger.warning(f"Failed to parse datetime: {dt_str}")
    return None


def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    Safely load JSON string.
    
    Args:
        data: JSON string
        default: Default value if parsing fails
        
    Returns:
        Any: Parsed JSON or default
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """
    Safely dump data to JSON string.
    
    Args:
        data: Data to serialize
        default: Default string if serialization fails
        
    Returns:
        str: JSON string or default
    """
    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError):
        return default


def chunk_list(data: List[Any], chunk_size: int = 100) -> List[List[Any]]:
    """
    Split list into chunks.
    
    Args:
        data: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List[List]: Chunked list
    """
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """
    Flatten nested list.
    
    Args:
        nested_list: Nested list
        
    Returns:
        List: Flattened list
    """
    return [item for sublist in nested_list for item in sublist]


def remove_duplicates(data: List[Any]) -> List[Any]:
    """
    Remove duplicates while preserving order.
    
    Args:
        data: List with possible duplicates
        
    Returns:
        List: Deduplicated list
    """
    seen = set()
    result = []
    
    for item in data:
        if item not in seen:
            seen.add(item)
            result.append(item)
    
    return result


def deep_get(data: Dict, path: str, default: Any = None) -> Any:
    """
    Get nested dictionary value using dot notation.
    
    Args:
        data: Dictionary
        path: Path using dot notation (e.g., "user.profile.name")
        default: Default value if not found
        
    Returns:
        Any: Value or default
    """
    keys = path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def deep_set(data: Dict, path: str, value: Any) -> Dict:
    """
    Set nested dictionary value using dot notation.
    
    Args:
        data: Dictionary
        path: Path using dot notation
        value: Value to set
        
    Returns:
        Dict: Updated dictionary
    """
    keys = path.split('.')
    current = data
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return data


def to_bool(value: Any) -> bool:
    """
    Convert value to boolean.
    
    Args:
        value: Value to convert
        
    Returns:
        bool: Converted boolean
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ['true', '1', 'yes', 'y', 'on']
    
    return bool(value)


def to_int(value: Any, default: int = 0) -> int:
    """
    Convert value to integer.
    
    Args:
        value: Value to convert
        default: Default if conversion fails
        
    Returns:
        int: Converted integer
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def to_float(value: Any, default: float = 0.0) -> float:
    """
    Convert value to float.
    
    Args:
        value: Value to convert
        default: Default if conversion fails
        
    Returns:
        float: Converted float
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def humanize_bytes(bytes_count: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        bytes_count: Number of bytes
        
    Returns:
        str: Human-readable size
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024
    
    return f"{bytes_count:.2f} PB"


def humanize_time(seconds: float) -> str:
    """
    Convert seconds to human-readable time.
    
    Args:
        seconds: Number of seconds
        
    Returns:
        str: Human-readable time
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f}m"
    
    hours = minutes / 60
    return f"{hours:.1f}h"


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to max length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.
    
    Args:
        text: Text to convert
        
    Returns:
        str: Slugified text
    """
    import re
    
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def calculate_confidence_score(
    scores: List[float],
    weights: Optional[List[float]] = None,
) -> float:
    """
    Calculate weighted confidence score.
    
    Args:
        scores: List of scores (0-1)
        weights: Optional weights for each score
        
    Returns:
        float: Weighted average score
    """
    if not scores:
        return 0.0
    
    if weights is None:
        weights = [1.0] * len(scores)
    
    if len(scores) != len(weights):
        weights = [1.0] * len(scores)
    
    total_weight = sum(weights)
    if total_weight == 0:
        return sum(scores) / len(scores)
    
    weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
    return weighted_sum / total_weight


def calculate_age(birth_date: date) -> int:
    """
    Calculate age from birth date.
    
    Args:
        birth_date: Date of birth
        
    Returns:
        int: Age in years
    """
    today = date.today()
    age = today.year - birth_date.year
    
    # Adjust if birthday hasn't occurred this year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age
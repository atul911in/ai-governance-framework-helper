"""Knowledge base loader module for the AI Governance Framework Helper.

Provides functions to load, validate, and cache governance framework,
technology, and industry JSON data from the data directory.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Module-level cache for loaded data
_cache: dict[str, Any] = {}

# Base data directory (relative to project root)
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _get_data_dir() -> Path:
    """Return the base data directory path."""
    return _DATA_DIR


def _load_json_file(file_path: Path) -> Any:
    """Load and parse a JSON file.

    Args:
        file_path: Path to the JSON file.

    Returns:
        Parsed JSON data.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _validate_framework_data(data: dict) -> bool:
    """Validate framework data has required fields.

    Args:
        data: Framework data dictionary.

    Returns:
        True if valid, raises ValueError otherwise.
    """
    required_fields = [
        "framework_id",
        "display_name",
        "country_or_region",
        "summary",
        "last_updated",
        "version",
        "risk_tiers",
        "key_obligations",
    ]
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValueError(
            f"Framework data missing required fields: {', '.join(missing)}"
        )
    return True


def _validate_technology_entry(data: dict) -> bool:
    """Validate a technology entry has required fields.

    Args:
        data: Technology entry dictionary.

    Returns:
        True if valid, raises ValueError otherwise.
    """
    required_fields = [
        "category",
        "name",
        "provider",
        "description",
        "key_capabilities",
        "pros",
        "cons",
        "compliance_notes",
    ]
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValueError(
            f"Technology entry missing required fields: {', '.join(missing)}"
        )
    return True


def _validate_industry_data(data: dict) -> bool:
    """Validate industry data has required fields.

    Args:
        data: Industry data dictionary.

    Returns:
        True if valid, raises ValueError otherwise.
    """
    required_fields = [
        "sector",
        "display_name",
        "regulatory_context",
        "common_ai_use_cases",
        "best_practices",
    ]
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValueError(
            f"Industry data missing required fields: {', '.join(missing)}"
        )
    return True


def clear_cache() -> None:
    """Clear the in-memory data cache."""
    _cache.clear()


def get_framework(framework_id: str) -> dict:
    """Load a single governance framework by its ID.

    Args:
        framework_id: The framework identifier (e.g., 'eu_ai_act').

    Returns:
        Dictionary containing the framework data.

    Raises:
        FileNotFoundError: If the framework JSON file does not exist.
        ValueError: If the loaded data fails validation.
    """
    cache_key = f"framework:{framework_id}"
    if cache_key in _cache:
        return _cache[cache_key]

    file_path = _get_data_dir() / "frameworks" / f"{framework_id}.json"
    data = _load_json_file(file_path)
    _validate_framework_data(data)
    _cache[cache_key] = data
    return data


def get_all_frameworks() -> list[dict]:
    """Load all governance frameworks.

    Returns:
        List of dictionaries, each containing a framework's data.

    Raises:
        FileNotFoundError: If the frameworks directory does not exist.
    """
    cache_key = "all_frameworks"
    if cache_key in _cache:
        return _cache[cache_key]

    frameworks_dir = _get_data_dir() / "frameworks"
    if not frameworks_dir.exists():
        raise FileNotFoundError(f"Frameworks directory not found: {frameworks_dir}")

    frameworks = []
    for file_path in sorted(frameworks_dir.glob("*.json")):
        try:
            data = _load_json_file(file_path)
            _validate_framework_data(data)
            frameworks.append(data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Skipping invalid framework file {file_path.name}: {e}")
            continue

    _cache[cache_key] = frameworks
    return frameworks


def get_technology_db() -> dict:
    """Load all technology data (platforms, orchestration, models).

    Returns:
        Dictionary with keys 'platforms', 'orchestration', and 'models',
        each containing a list of technology entries.

    Raises:
        FileNotFoundError: If any technology JSON file does not exist.
    """
    cache_key = "technology_db"
    if cache_key in _cache:
        return _cache[cache_key]

    tech_dir = _get_data_dir() / "technology"
    tech_files = {
        "platforms": "platforms.json",
        "orchestration": "orchestration.json",
        "models": "models.json",
    }

    technology_db: dict[str, list[dict]] = {}
    for key, filename in tech_files.items():
        file_path = tech_dir / filename
        data = _load_json_file(file_path)

        if not isinstance(data, list):
            raise ValueError(f"Technology file {filename} must contain a JSON array")

        for entry in data:
            _validate_technology_entry(entry)

        technology_db[key] = data

    _cache[cache_key] = technology_db
    return technology_db


def get_industry_context(sector: str) -> dict:
    """Load industry data for a specific sector.

    Args:
        sector: The industry sector identifier (e.g., 'banking', 'health').

    Returns:
        Dictionary containing the industry context data.

    Raises:
        FileNotFoundError: If the industry JSON file does not exist.
        ValueError: If the loaded data fails validation.
    """
    cache_key = f"industry:{sector}"
    if cache_key in _cache:
        return _cache[cache_key]

    file_path = _get_data_dir() / "industries" / f"{sector}.json"
    data = _load_json_file(file_path)
    _validate_industry_data(data)
    _cache[cache_key] = data
    return data

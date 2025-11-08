"""File storage utilities"""
import os
import json
from pathlib import Path
from typing import Any, Dict
import logging

from ..config import settings

logger = logging.getLogger(__name__)


def ensure_output_dir(job_id: str) -> Path:
    """Create output directory structure for a job"""
    job_dir = Path(settings.output_dir) / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (job_dir / "data").mkdir(exist_ok=True)
    (job_dir / "models").mkdir(exist_ok=True)
    
    return job_dir


def save_json(job_id: str, filename: str, data: Dict[str, Any]):
    """Save JSON data to job directory"""
    job_dir = ensure_output_dir(job_id)
    filepath = job_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved {filename} for job {job_id}")


def load_json(job_id: str, filename: str) -> Dict[str, Any]:
    """Load JSON data from job directory"""
    filepath = Path(settings.output_dir) / job_id / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"File {filename} not found for job {job_id}")
    
    with open(filepath, 'r') as f:
        return json.load(f)


def job_exists(job_id: str) -> bool:
    """Check if a job directory exists"""
    job_dir = Path(settings.output_dir) / job_id
    return job_dir.exists()


def get_job_dir(job_id: str) -> Path:
    """Get job directory path"""
    return Path(settings.output_dir) / job_id


def save_config(job_id: str, config: Dict[str, Any]):
    """Save job configuration"""
    save_json(job_id, "config.json", config)


def load_config(job_id: str) -> Dict[str, Any]:
    """Load job configuration"""
    return load_json(job_id, "config.json")


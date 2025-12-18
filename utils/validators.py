"""Input validation utilities."""

import re
from typing import List, Optional

# Common Indian market sectors for validation
VALID_SECTORS: List[str] = [
    "pharmaceuticals",
    "technology",
    "banking",
    "finance",
    "telecommunications",
    "automotive",
    "real estate",
    "energy",
    "oil and gas",
    "steel",
    "cement",
    "fashion",
    "retail",
    "agriculture",
    "healthcare",
    "education",
    "media",
    "entertainment",
    "food and beverages",
    "tourism",
    "infrastructure",
    "power",
    "chemicals",
    "textiles",
    "it services",
    "consumer goods",
]


def validate_sector(sector: str, strict: bool = False) -> bool:
    """
    Validate sector input.
    
    Args:
        sector: Sector name to validate
        strict: If True, only allow predefined sectors. If False, validate format only.
        
    Returns:
        True if valid, False otherwise
    """
    sector = sector.strip().lower()
    
    # Format validation: alphanumeric, spaces, hyphens
    if not re.match(r"^[a-z0-9\s\-]+$", sector):
        return False
    
    # If strict mode, check against whitelist
    if strict:
        return sector in VALID_SECTORS
    
    return True


def normalize_sector(sector: str) -> str:
    """
    Normalize sector name (lowercase, strip whitespace).
    
    Args:
        sector: Sector name to normalize
        
    Returns:
        Normalized sector name
    """
    return sector.strip().lower()


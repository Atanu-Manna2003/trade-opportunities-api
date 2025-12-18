"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema for JWT payload."""
    username: Optional[str] = None
    user_id: Optional[str] = None


class SectorAnalysisRequest(BaseModel):
    """Schema for sector analysis request."""
    sector: str = Field(
        ...,
        description="Sector name for analysis (e.g., pharmaceuticals, technology, banking)",
        min_length=2,
        max_length=100,
    )

    @field_validator("sector")
    @classmethod
    def validate_sector(cls, v: str) -> str:
        """Validate sector input - alphanumeric, spaces, hyphens only."""
        v = v.strip().lower()
        if not re.match(r"^[a-z0-9\s\-]+$", v):
            raise ValueError(
                "Sector must contain only letters, numbers, spaces, and hyphens"
            )
        return v


class AnalyzeResponse(BaseModel):
    """Response schema for sector analysis."""
    sector: str
    report: str = Field(..., description="Structured Markdown report")
    generated_at: str = Field(..., description="ISO format timestamp")


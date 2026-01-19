"""Configuration models for website crawling."""

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class WebsiteConfiguration(BaseModel):
    """Configuration for a single government website to crawl.

    Attributes:
        id: Unique identifier for the website (e.g., "miac-national")
        name: Human-readable name (e.g., "Ministry of Internal Affairs")
        base_url: Base URL of the website (must be valid HTTP/HTTPS URL)
        description: Optional description of the website
        crawl_frequency: Suggested crawl frequency (e.g., "monthly") - informational only
        enabled: Whether this website should be crawled (default: True)
    """

    id: str = Field(..., pattern=r"^[a-z0-9-]+$")
    name: str
    base_url: HttpUrl
    description: Optional[str] = None
    crawl_frequency: Optional[str] = None
    enabled: bool = True

    model_config = {"json_schema_extra": {"examples": [
        {
            "id": "miac-national",
            "name": "Ministry of Internal Affairs and Communications",
            "base_url": "https://www.soumu.go.jp/senkyo/seiji_s/",
            "description": "National political finance disclosure site",
            "crawl_frequency": "monthly",
            "enabled": True,
        }
    ]}}


class WebsiteConfigurationList(BaseModel):
    """Root configuration object containing the list of all websites to crawl.

    Attributes:
        version: Configuration schema version (e.g., "1.0")
        websites: List of website configurations
    """

    version: str = Field(..., pattern=r"^\d+\.\d+$")
    websites: list[WebsiteConfiguration]

    @field_validator("websites")
    @classmethod
    def unique_ids(cls, v: list[WebsiteConfiguration]) -> list[WebsiteConfiguration]:
        """Validate that all website IDs are unique."""
        ids = [w.id for w in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Website IDs must be unique")
        if not v:
            raise ValueError("Must contain at least one website")
        return v

    model_config = {"json_schema_extra": {"examples": [
        {
            "version": "1.0",
            "websites": [
                {
                    "id": "miac-national",
                    "name": "Ministry of Internal Affairs",
                    "base_url": "https://www.soumu.go.jp/senkyo/seiji_s/",
                },
                {
                    "id": "tokyo-prefecture",
                    "name": "Tokyo Prefecture",
                    "base_url": "https://www.senkyo.metro.tokyo.lg.jp/",
                },
            ],
        }
    ]}}

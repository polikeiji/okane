"""Website scraping strategy models."""

from typing import Optional

from pydantic import BaseModel, Field


class ScrapingStrategy(BaseModel):
    """AI-determined approach for extracting PDFs from a specific website.

    Attributes:
        website_id: ID of the website this strategy applies to
        strategy_type: Type of strategy (css_selector, xpath, regex, pagination)
        pdf_link_selectors: CSS selectors or XPath expressions to find PDF links
        pagination_selector: Optional selector for "next page" link if pagination exists
        max_pages: Maximum number of pages to crawl (default: 10)
        metadata_extraction: Optional selectors for extracting metadata from page
        confidence: AI confidence score (0.0-1.0) in this strategy
    """

    website_id: str
    strategy_type: str = Field(..., pattern=r"^(css_selector|xpath|regex|pagination)$")
    pdf_link_selectors: list[str]
    pagination_selector: Optional[str] = None
    max_pages: Optional[int] = Field(default=10, gt=0)
    metadata_extraction: Optional[dict[str, str]] = None
    confidence: float = Field(..., ge=0.0, le=1.0)

    @property
    def is_confident(self) -> bool:
        """Return True if confidence score is >= 0.8."""
        return self.confidence >= 0.8

    model_config = {"json_schema_extra": {"examples": [
        {
            "website_id": "miac-national",
            "strategy_type": "css_selector",
            "pdf_link_selectors": ["a[href$='.pdf']", "a.pdf-link"],
            "pagination_selector": "a.next-page",
            "max_pages": 10,
            "metadata_extraction": {
                "organization": ".org-name",
                "period": ".reporting-period",
            },
            "confidence": 0.95,
        }
    ]}}

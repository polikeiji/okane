"""Metadata models for crawl tracking and file information."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl


class DownloadedPDF(BaseModel):
    """Represents a political cash flow report PDF file that has been downloaded.

    Attributes:
        file_id: Unique identifier for this file (UUID)
        original_url: Source URL where PDF was found
        local_path: Relative path where file is stored
        filename: Structured filename
        file_size_bytes: Size of the downloaded file in bytes
        sha256_hash: SHA-256 hash of file content for deduplication
        organization_name: Extracted political party/organization name
        organization_slug: URL-safe organization identifier
        reporting_period: Fiscal period (e.g., "2024-Q1", "2024-annual")
        download_timestamp: When the file was downloaded (ISO 8601 format)
        website_id: ID of source website configuration
        http_status_code: HTTP response status code
        http_headers: Relevant HTTP response headers
        crawl_status: Status of crawl (success, failed, partial)
        error_message: Error message if crawl failed
        metadata_version: Version of metadata schema
    """

    file_id: str
    original_url: HttpUrl
    local_path: str
    filename: str
    file_size_bytes: int = Field(..., gt=0)
    sha256_hash: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    organization_name: Optional[str] = None
    organization_slug: str = Field(..., pattern=r"^[a-z0-9-]+$")
    reporting_period: Optional[str] = None
    download_timestamp: datetime
    website_id: str
    http_status_code: int
    http_headers: dict[str, str]
    crawl_status: str = Field(..., pattern=r"^(success|failed|partial)$")
    error_message: Optional[str] = None
    metadata_version: str

    model_config = {"json_schema_extra": {"examples": [
        {
            "file_id": "550e8400-e29b-41d4-a716-446655440000",
            "original_url": "https://www.soumu.go.jp/senkyo/seiji_s/reports/2024/ldp_2024_q1.pdf",
            "local_path": "pdfs/ldp_2024-q1_annual-report.pdf",
            "filename": "ldp_2024-q1_annual-report.pdf",
            "file_size_bytes": 2457600,
            "sha256_hash": "a3b2c1d4e5f6789012345678901234567890123456789012345678901234567890",
            "organization_name": "Liberal Democratic Party",
            "organization_slug": "ldp",
            "reporting_period": "2024-Q1",
            "download_timestamp": "2026-01-19T10:30:00Z",
            "website_id": "miac-national",
            "http_status_code": 200,
            "http_headers": {
                "Content-Type": "application/pdf",
                "Last-Modified": "2024-04-15T08:00:00Z",
            },
            "crawl_status": "success",
            "error_message": None,
            "metadata_version": "1.0",
        }
    ]}}


class CrawlMetadata(BaseModel):
    """Collection-level information about a crawl execution.

    Attributes:
        crawl_id: Unique identifier for this crawl execution (UUID)
        crawl_start_time: When the crawl started (ISO 8601)
        crawl_end_time: When the crawl completed (ISO 8601), None if in progress
        total_websites: Total number of websites in configuration
        websites_crawled: Number of websites successfully crawled
        websites_failed: Number of websites that failed to crawl
        total_pdfs_discovered: Total number of PDF URLs found
        total_pdfs_downloaded: Number of PDFs successfully downloaded
        total_pdfs_failed: Number of PDFs that failed to download
        total_bytes_downloaded: Total size of all downloaded files
        parallelism: Parallelism level used for this crawl
        max_files_limit: Max files limit if specified, None for unlimited
        output_folder: Path to output folder (local or Azure)
        storage_backend: Type of storage used (local or adls)
        config_file_path: Path to configuration file used
        downloaded_files: List of all downloaded PDF metadata
        errors: List of errors encountered during crawl
        metadata_version: Version of metadata schema
    """

    crawl_id: str
    crawl_start_time: datetime
    crawl_end_time: Optional[datetime] = None
    total_websites: int = Field(..., ge=0)
    websites_crawled: int = Field(..., ge=0)
    websites_failed: int = Field(..., ge=0)
    total_pdfs_discovered: int = Field(..., ge=0)
    total_pdfs_downloaded: int = Field(..., ge=0)
    total_pdfs_failed: int = Field(..., ge=0)
    total_bytes_downloaded: int = Field(..., ge=0)
    parallelism: int = Field(..., gt=0)
    max_files_limit: Optional[int] = Field(default=None, gt=0)
    output_folder: str
    storage_backend: str = Field(..., pattern=r"^(local|adls)$")
    config_file_path: str
    downloaded_files: list[DownloadedPDF]
    errors: list[dict[str, Any]]
    metadata_version: str

    model_config = {"json_schema_extra": {"examples": [
        {
            "crawl_id": "660e9500-f39c-41d4-b826-556655440000",
            "crawl_start_time": "2026-01-19T10:00:00Z",
            "crawl_end_time": "2026-01-19T10:25:00Z",
            "total_websites": 10,
            "websites_crawled": 9,
            "websites_failed": 1,
            "total_pdfs_discovered": 47,
            "total_pdfs_downloaded": 45,
            "total_pdfs_failed": 2,
            "total_bytes_downloaded": 125829120,
            "parallelism": 5,
            "max_files_limit": None,
            "output_folder": "/path/to/output",
            "storage_backend": "local",
            "config_file_path": "/path/to/config.json",
            "downloaded_files": [],
            "errors": [
                {
                    "website_id": "site-xyz",
                    "error_type": "NetworkError",
                    "error_message": "Connection timeout",
                    "timestamp": "2026-01-19T10:15:00Z",
                }
            ],
            "metadata_version": "1.0",
        }
    ]}}

"""PDF downloader service."""

import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path

import httpx

from okane.lib.pdf_utils import calculate_sha256, is_valid_pdf
from okane.lib.url_utils import sanitize_filename
from okane.models.metadata import DownloadedPDF


class PDFDownloader:
    """Downloads and validates PDF files."""

    def __init__(
        self,
        user_agent: str = "Okane-Crawler/1.0.0 (+https://github.com/polikeiji/okane)",
        timeout: int = 300,
    ) -> None:
        """Initialize PDF downloader.

        Args:
            user_agent: User-Agent header for requests
            timeout: HTTP request timeout in seconds (default: 300 for large files)
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.client = httpx.Client(
            headers={"User-Agent": user_agent},
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        )

    def __enter__(self) -> "PDFDownloader":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: object) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close HTTP client."""
        self.client.close()

    def download_pdf(
        self, url: str, website_id: str, organization_slug: str = "unknown"
    ) -> tuple[bytes, DownloadedPDF]:
        """Download PDF file and create metadata.

        Args:
            url: URL of the PDF file
            website_id: ID of the source website
            organization_slug: URL-safe organization identifier

        Returns:
            Tuple of (PDF file content as bytes, DownloadedPDF metadata)

        Raises:
            Exception: If download or validation fails
        """
        # Download file
        response = self.client.get(url)
        response.raise_for_status()

        pdf_content = response.content
        http_status = response.status_code
        http_headers = dict(response.headers)

        # Save to temporary file for validation
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_content)
            tmp_path = Path(tmp_file.name)

        try:
            # Validate PDF
            if not is_valid_pdf(tmp_path):
                raise ValueError(f"Downloaded file is not a valid PDF: {url}")

            # Calculate hash
            sha256_hash = calculate_sha256(tmp_path)

            # Generate file ID
            file_id = str(uuid.uuid4())

            # Extract filename from URL
            url_filename = url.split("/")[-1].split("?")[0]
            sanitized_filename = sanitize_filename(url_filename)

            # Create structured filename
            timestamp_str = datetime.now(UTC).strftime("%Y%m%d")
            filename = f"{organization_slug}_{timestamp_str}_{sanitized_filename}"
            if not filename.endswith(".pdf"):
                filename += ".pdf"

            # Create metadata
            metadata = DownloadedPDF(
                file_id=file_id,
                original_url=url,
                local_path=f"pdfs/{filename}",
                filename=filename,
                file_size_bytes=len(pdf_content),
                sha256_hash=sha256_hash,
                organization_name=None,  # TODO: Extract from HTML metadata
                organization_slug=organization_slug,
                reporting_period=None,  # TODO: Extract from filename or HTML
                download_timestamp=datetime.now(UTC),
                website_id=website_id,
                http_status_code=http_status,
                http_headers={
                    k: v
                    for k, v in http_headers.items()
                    if k.lower() in ("content-type", "last-modified", "content-length")
                },
                crawl_status="success",
                error_message=None,
                metadata_version="1.0",
            )

            return pdf_content, metadata

        finally:
            # Clean up temp file
            try:
                tmp_path.unlink()
            except Exception:
                pass

    def download_pdf_with_retry(
        self,
        url: str,
        website_id: str,
        organization_slug: str = "unknown",
        max_retries: int = 3,
    ) -> tuple[bytes | None, DownloadedPDF | None, str | None]:
        """Download PDF with retry logic.

        Args:
            url: URL of the PDF file
            website_id: ID of the source website
            organization_slug: URL-safe organization identifier
            max_retries: Maximum number of retry attempts

        Returns:
            Tuple of (PDF content or None, metadata or None, error message or None)
        """
        last_error: str | None = None

        for attempt in range(max_retries):
            try:
                content, metadata = self.download_pdf(url, website_id, organization_slug)
                return content, metadata, None
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    # Wait before retry (exponential backoff)
                    import time

                    time.sleep(2**attempt)

        # All retries failed
        # Create error metadata
        error_metadata = DownloadedPDF(
            file_id=str(uuid.uuid4()),
            original_url=url,
            local_path="",
            filename="",
            file_size_bytes=0,
            sha256_hash="0" * 64,
            organization_name=None,
            organization_slug=organization_slug,
            reporting_period=None,
            download_timestamp=datetime.now(UTC),
            website_id=website_id,
            http_status_code=0,
            http_headers={},
            crawl_status="failed",
            error_message=last_error,
            metadata_version="1.0",
        )

        return None, error_metadata, last_error

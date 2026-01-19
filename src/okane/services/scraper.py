"""Website scraper service for extracting PDF URLs."""

import time
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from okane.lib.ai_analyzer import AIAnalyzer
from okane.lib.url_utils import check_robots_txt, is_valid_url
from okane.models.website import ScrapingStrategy


class WebsiteScraper:
    """Scrapes government websites to extract PDF URLs."""

    def __init__(
        self,
        ai_analyzer: AIAnalyzer | None = None,
        user_agent: str = "Okane-Crawler/1.0.0 (+https://github.com/polikeiji/okane)",
        timeout: int = 30,
        polite_delay: float = 1.5,
    ) -> None:
        """Initialize website scraper.

        Args:
            ai_analyzer: AI analyzer for determining scraping strategy
            user_agent: User-Agent header for requests
            timeout: HTTP request timeout in seconds
            polite_delay: Delay between requests in seconds (default: 1.5s)
        """
        self.ai_analyzer = ai_analyzer or AIAnalyzer()
        self.user_agent = user_agent
        self.timeout = timeout
        self.polite_delay = polite_delay
        self.client = httpx.Client(
            headers={"User-Agent": user_agent},
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        )

    def __enter__(self) -> "WebsiteScraper":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: object) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close HTTP client."""
        self.client.close()

    def scrape_website(
        self, website_id: str, base_url: str, max_pdfs: int | None = None
    ) -> tuple[list[str], ScrapingStrategy]:
        """Scrape website to extract PDF URLs.

        Args:
            website_id: ID of the website configuration
            base_url: Base URL of the website
            max_pdfs: Maximum number of PDFs to extract (None for unlimited)

        Returns:
            Tuple of (list of PDF URLs, scraping strategy used)

        Raises:
            Exception: If scraping fails
        """
        # Check robots.txt
        if not check_robots_txt(base_url, self.user_agent):
            raise PermissionError(f"Crawling disallowed by robots.txt: {base_url}")

        # Fetch homepage
        html_content = self._fetch_html(base_url)

        # Analyze with AI to get strategy
        strategy = self.ai_analyzer.analyze_website(html_content, website_id, base_url)

        # Extract PDF URLs using strategy
        pdf_urls = self._extract_pdf_urls(html_content, base_url, strategy, max_pdfs)

        return pdf_urls, strategy

    def _fetch_html(self, url: str) -> str:
        """Fetch HTML content from URL.

        Args:
            url: URL to fetch

        Returns:
            HTML content as string

        Raises:
            Exception: If fetch fails
        """
        # Polite delay before request
        time.sleep(self.polite_delay)

        response = self.client.get(url)
        response.raise_for_status()
        return response.text

    def _extract_pdf_urls(
        self,
        html_content: str,
        base_url: str,
        strategy: ScrapingStrategy,
        max_pdfs: int | None = None,
    ) -> list[str]:
        """Extract PDF URLs from HTML using scraping strategy.

        Args:
            html_content: HTML content
            base_url: Base URL for resolving relative URLs
            strategy: Scraping strategy to use
            max_pdfs: Maximum number of PDFs to extract

        Returns:
            List of absolute PDF URLs
        """
        soup = BeautifulSoup(html_content, "html.parser")
        pdf_urls: list[str] = []

        # Apply selectors from strategy
        for selector in strategy.pdf_link_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get("href")
                if href:
                    # Convert to absolute URL
                    absolute_url = urljoin(base_url, href)
                    # Validate and add
                    if is_valid_url(absolute_url) and absolute_url.lower().endswith(".pdf"):
                        if absolute_url not in pdf_urls:
                            pdf_urls.append(absolute_url)
                            if max_pdfs and len(pdf_urls) >= max_pdfs:
                                return pdf_urls

        # Handle pagination if configured
        if strategy.pagination_selector and len(pdf_urls) < (max_pdfs or float("inf")):
            pdf_urls.extend(
                self._handle_pagination(
                    soup, base_url, strategy, max_pdfs - len(pdf_urls) if max_pdfs else None
                )
            )

        return pdf_urls

    def _handle_pagination(
        self,
        soup: BeautifulSoup,
        base_url: str,
        strategy: ScrapingStrategy,
        remaining_pdfs: int | None = None,
    ) -> list[str]:
        """Handle paginated results.

        Args:
            soup: BeautifulSoup object of current page
            base_url: Base URL
            strategy: Scraping strategy
            remaining_pdfs: Remaining PDFs to collect

        Returns:
            List of additional PDF URLs from paginated pages
        """
        pdf_urls: list[str] = []
        current_page = 1

        while current_page < (strategy.max_pages or 10):
            # Find next page link
            next_link = soup.select_one(strategy.pagination_selector or "")
            if not next_link:
                break

            next_href = next_link.get("href")
            if not next_href:
                break

            next_url = urljoin(base_url, next_href)

            try:
                # Fetch next page
                html_content = self._fetch_html(next_url)
                soup = BeautifulSoup(html_content, "html.parser")

                # Extract PDFs from this page
                for selector in strategy.pdf_link_selectors:
                    links = soup.select(selector)
                    for link in links:
                        href = link.get("href")
                        if href:
                            absolute_url = urljoin(base_url, href)
                            if is_valid_url(absolute_url) and absolute_url.lower().endswith(".pdf"):
                                if absolute_url not in pdf_urls:
                                    pdf_urls.append(absolute_url)
                                    if remaining_pdfs and len(pdf_urls) >= remaining_pdfs:
                                        return pdf_urls

                current_page += 1
            except Exception:
                # Stop pagination on error
                break

        return pdf_urls

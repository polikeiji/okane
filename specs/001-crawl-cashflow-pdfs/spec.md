# Feature Specification: Crawl Political Cash Flow PDFs

**Feature Branch**: `001-crawl-cashflow-pdfs`  
**Created**: 2026-01-18  
**Status**: Draft  
**Input**: User description: "a spec for a subcommand of crawling PDFs of cash flow report of political parties and organizations that are officially published by the government and local governments"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic PDF Crawling with Default Configuration (Priority: P1)

A researcher wants to collect all available political party cash flow reports from government websites using default settings. They run the crawl subcommand with minimal parameters to download PDFs from pre-configured government websites into a local folder.

**Why this priority**: This is the core functionality that delivers immediate value. Users can start collecting data without complex configuration, making it the minimum viable product.

**Independent Test**: Can be fully tested by running the subcommand with only an output folder parameter and verifying that PDFs are downloaded from default government websites with a metadata JSON file generated.

**Acceptance Scenarios**:

1. **Given** the tool is installed with default website configuration, **When** user runs the crawl subcommand specifying only an output folder, **Then** PDFs are downloaded from all default government websites and stored in the output folder with a metadata JSON file
2. **Given** a crawl is in progress, **When** user views the output folder during execution, **Then** they can see progressive file downloads and the metadata JSON file being updated
3. **Given** the default website list includes 5 government sites, **When** the crawl completes successfully, **Then** the metadata JSON contains entries for all downloaded PDFs with their original URLs

---

### User Story 2 - Custom Website Configuration (Priority: P2)

A researcher needs to crawl additional regional government websites not included in the default list. They create a custom JSON configuration file with website URLs and run the crawl subcommand pointing to their configuration file.

**Why this priority**: This extends the tool's utility to regional and specialized sources while the core crawling logic remains the same. Essential for real-world usage but can be developed after basic crawling works.

**Independent Test**: Can be tested by creating a custom JSON file with test websites, running the crawl with the config parameter, and verifying PDFs are downloaded only from the specified websites.

**Acceptance Scenarios**:

1. **Given** a custom JSON configuration file with 3 website URLs, **When** user runs the crawl subcommand with the config file path parameter, **Then** PDFs are crawled only from the 3 specified websites
2. **Given** an invalid JSON configuration file, **When** user attempts to run the crawl, **Then** the system displays a clear error message indicating the configuration format issue
3. **Given** a configuration file containing a mix of valid and invalid URLs, **When** the crawl executes, **Then** valid URLs are processed while invalid ones are logged as errors without stopping the entire crawl

---

### User Story 3 - Parallel Processing for Performance (Priority: P3)

A researcher needs to crawl dozens of government websites efficiently. They run the crawl subcommand with a parallelism parameter set to 5 to process multiple websites simultaneously and complete the task faster.

**Why this priority**: Performance optimization that significantly reduces execution time for large-scale crawls. Can be implemented after core functionality is stable.

**Independent Test**: Can be tested by running the same crawl with parallelism=1 and parallelism=5, measuring execution time difference, and verifying all PDFs are downloaded correctly in both cases.

**Acceptance Scenarios**:

1. **Given** a configuration with 10 websites and parallelism set to 5, **When** the crawl executes, **Then** up to 5 websites are processed concurrently, reducing total execution time compared to sequential processing
2. **Given** parallelism set to a value higher than the number of websites, **When** the crawl runs, **Then** all websites are processed concurrently without errors
3. **Given** one website in a parallel crawl encounters an error, **When** the crawl continues, **Then** other parallel tasks proceed unaffected and the error is logged in the metadata

---

### User Story 4 - Cloud Storage Integration (Priority: P4)

An organization running automated data collection needs to store crawled PDFs directly in Azure Data Lake Storage Gen2 for enterprise data pipelines. They configure the output folder path to an ADLS Gen2 location and run the crawl subcommand.

**Why this priority**: Enterprise integration feature that enables automation and scalability. Required for production deployments but not essential for initial validation.

**Independent Test**: Can be tested by configuring an ADLS Gen2 output path, running the crawl, and verifying PDFs and metadata are stored in the cloud storage location with proper authentication.

**Acceptance Scenarios**:

1. **Given** an ADLS Gen2 path configured as output folder with valid credentials, **When** the crawl executes, **Then** all PDFs and metadata JSON are stored directly in the cloud storage location
2. **Given** an ADLS Gen2 path configured but credentials are invalid, **When** user attempts to run the crawl, **Then** the system displays a clear authentication error before starting the crawl
3. **Given** PDFs are being written to ADLS Gen2 during crawl, **When** network interruption occurs, **Then** the system retries the upload and logs any permanent failures in the metadata

---

### Edge Cases

- What happens when a government website is temporarily unavailable during the crawl?
- How does the system handle websites with different structures (tables, lists, nested pages)?
- What occurs when a PDF file is corrupted or incomplete on the source website?
- How does the system handle websites requiring authentication or with CAPTCHA?
- What happens when the output folder runs out of disk space during a large crawl?
- How does the system behave when crawling a website that has already been crawled (duplicate detection)?
- What occurs when the AI analysis service is temporarily unavailable or returns ambiguous results?
- How does the system handle extremely large PDF files (e.g., 100+ MB)?
- What happens when multiple crawl processes are run simultaneously with overlapping output folders?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a CLI subcommand for crawling political cash flow PDF reports
- **FR-002**: System MUST accept a parallelism parameter via CLI to control the number of concurrent website crawls (default: 1)
- **FR-003**: System MUST accept a configuration file path parameter via CLI that specifies website URLs to crawl
- **FR-004**: System MUST include a default JSON configuration file containing Japanese national government political finance disclosure websites (Ministry of Internal Affairs and Communications political finance disclosure site, National Diet Library) plus all 47 prefectural government political finance disclosure sites
- **FR-005**: System MUST accept an output folder path parameter via CLI where downloaded PDFs will be stored
- **FR-006**: System MUST support both local file system and Azure Data Lake Storage Gen2 (ADLS Gen2) as valid output folder destinations
- **FR-007**: System MUST analyze each target website using generative AI to dynamically determine the appropriate scraping logic for that specific website structure
- **FR-008**: System MUST download all discovered PDF files containing political party or organization cash flow reports from each configured website
- **FR-009**: System MUST store downloaded PDF files in the specified output folder using a structured naming convention: `{organization-slug}_{reporting-period}_{original-name}.pdf` where organization-slug is a URL-safe identifier for the political party/organization, reporting-period is the fiscal period covered (e.g., 2024-Q1), and original-name is the sanitized original filename
- **FR-010**: System MUST create and maintain a metadata JSON file in the output folder containing information about all crawled files
- **FR-011**: System MUST include in the metadata JSON file for each crawled file: original URL, download timestamp, file size, file hash (SHA-256 for deduplication), HTTP response headers, crawl status (success/failure/partial), error messages (if any), extracted organization name, reporting period, file type/version information, and source website identifier
- **FR-012**: System MUST handle network errors gracefully by logging failures and continuing with remaining websites
- **FR-013**: System MUST validate that the output folder path is accessible and writable before starting the crawl
- **FR-014**: System MUST validate the configuration JSON file format before starting the crawl
- **FR-015**: System MUST respect robots.txt and implement polite crawling with appropriate delays between requests to avoid overwhelming government servers
- **FR-016**: System MUST log progress information during crawling, including websites being processed, files discovered, and download status
- **FR-017**: System MUST provide clear error messages when required CLI parameters are missing or invalid

### Key Entities

- **Website Configuration**: Represents a government website to crawl, containing the base URL, optional selectors or hints for PDF discovery, and crawl frequency preferences
- **Downloaded PDF**: Represents a political cash flow report PDF file, containing the file content, original source URL, download timestamp, file metadata (size, hash), and associated organization information
- **Crawl Metadata**: Represents the collection-level information about a crawl execution, containing the list of all downloaded PDFs, their metadata, crawl execution timestamp, success/failure status, and any errors encountered
- **Website Scraping Strategy**: Represents the AI-determined approach for extracting PDFs from a specific website, containing identified PDF links, page structure analysis, and navigation logic required for that site

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully download PDFs from at least 10 pre-configured government websites with a single command execution
- **SC-002**: The system correctly generates a metadata JSON file containing accurate information for 100% of successfully downloaded PDFs
- **SC-003**: Parallel crawling with parallelism=5 completes the same task at least 3 times faster than sequential crawling (parallelism=1)
- **SC-004**: The system successfully stores downloaded PDFs and metadata to ADLS Gen2 cloud storage with 99% success rate under normal network conditions
- **SC-005**: Users can add a new government website to the configuration and successfully crawl it without modifying any code
- **SC-006**: The AI-powered website analysis correctly identifies and extracts PDF links from at least 90% of tested government websites with varying structures
- **SC-007**: The crawl process completes within 30 minutes for a default configuration of 10 government websites when using parallelism=5
- **SC-008**: Error messages clearly indicate the specific issue (missing parameters, invalid paths, network failures) in 100% of error scenarios

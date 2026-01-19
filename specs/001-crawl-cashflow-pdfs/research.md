# Research: Crawl Political Cash Flow PDFs

**Feature**: 001-crawl-cashflow-pdfs  
**Date**: 2026-01-19  
**Status**: Complete

## Overview

This document captures the research findings for implementing a CLI tool to crawl political cash flow PDF reports from Japanese government websites with AI-powered scraping strategies.

## Technology Decisions

### 1. Web Scraping Library

**Decision**: Use `httpx` for HTTP requests + `beautifulsoup4` for HTML parsing

**Rationale**:
- `httpx` is a modern, async-capable HTTP client that supports both sync and async patterns
- Provides better performance than `requests` while maintaining similar API
- `beautifulsoup4` is the de facto standard for HTML parsing in Python
- Simple, battle-tested, and widely understood by developers
- Lightweight with minimal dependencies
- Easy to integrate with AI-powered analysis (pass HTML structure to LLM)

**Alternatives Considered**:
- **Scrapy**: Full framework with built-in parallelism and pipelines, but adds unnecessary complexity for our use case. We need flexibility to integrate AI-driven scraping logic, which is harder with Scrapy's rigid architecture.
- **Playwright**: Provides browser automation for JavaScript-heavy sites, but government websites are typically static HTML. Adds significant overhead (requires browser binaries) without clear benefit. Can be added later if needed.
- **selenium**: Similar to Playwright but older and slower. Same issues with overhead.

### 2. LLM Integration for Website Analysis

**Decision**: Direct OpenAI Python SDK (`openai` package)

**Rationale**:
- Official SDK provides reliable, well-maintained access to GPT models
- Simple API for sending HTML structure and receiving scraping instructions
- Supports function calling for structured output (e.g., JSON with selectors)
- Easy to mock for testing without hitting real API
- No additional abstraction layer needed for our use case

**Alternatives Considered**:
- **LangChain**: Provides higher-level abstractions for LLM applications, but adds complexity and dependencies for a straightforward use case. Our needs are simple: analyze HTML → return scraping strategy. Direct SDK calls are clearer.
- **Anthropic Claude API**: Alternative LLM provider, but OpenAI has better function calling support and is more widely used. Can be added as an alternative provider later if needed.
- **Local models (Ollama, etc.)**: Would eliminate API costs but require local model hosting, adds deployment complexity, and likely has lower quality output for HTML analysis tasks.

### 3. Azure Data Lake Storage Gen2 (ADLS Gen2) Integration

**Decision**: `azure-storage-file-datalake` SDK

**Rationale**:
- Official Azure SDK for ADLS Gen2 file system operations
- Provides dedicated ADLS Gen2 API (not just blob storage wrapper)
- Supports hierarchical namespace and directory operations
- Well-documented with good Python integration
- Part of the azure-sdk-for-python ecosystem with consistent API patterns

**Alternatives Considered**:
- **azure-storage-blob**: Lower-level blob storage API. While ADLS Gen2 is built on blob storage, using the dedicated datalake SDK provides better abstractions for file system operations (directories, paths) that match our needs.
- **fsspec + adlfs**: Generic filesystem interface that works with ADLS Gen2. Adds abstraction layer without clear benefit. Direct SDK usage is more explicit and easier to debug.

### 4. PDF Validation and Handling

**Decision**: `pypdf` for PDF validation + file hash utilities from standard library

**Rationale**:
- `pypdf` (formerly PyPDF2) is a pure Python PDF library
- Lightweight and suitable for basic validation (check if file is valid PDF, get metadata)
- We don't need full PDF parsing (OCR, text extraction) - just need to validate downloads
- Standard library `hashlib` for SHA-256 hashing (no additional dependency)
- Can add more sophisticated PDF tools later if text extraction is needed

**Alternatives Considered**:
- **pdfplumber**: More feature-rich with text extraction and table parsing, but heavier and unnecessary since we're only storing PDFs, not extracting data from them in this feature.
- **PyMuPDF (fitz)**: Fast and powerful, but has C dependencies which complicates deployment. Overkill for our validation needs.

### 5. Parallel Processing

**Decision**: Python `concurrent.futures.ThreadPoolExecutor`

**Rationale**:
- Standard library solution (no additional dependency)
- Perfect for I/O-bound tasks (network requests, file downloads)
- Simple, straightforward API for managing parallel workers
- Easy to configure parallelism level via CLI parameter
- Thread-safe data structures available in standard library

**Alternatives Considered**:
- **asyncio**: More performant for large-scale parallelism, but adds complexity with async/await throughout the codebase. ThreadPoolExecutor is sufficient for our scale (parallelism=5-10).
- **multiprocessing**: Provides true parallelism (bypasses GIL) but unnecessary for I/O-bound tasks. Adds overhead for process creation and inter-process communication.
- **celery/rq**: Task queue systems are overkill for a CLI tool. We don't need distributed task management, just concurrent downloads.

### 6. CLI Argument Parsing

**Decision**: Standard library `argparse`

**Rationale**:
- Required by Python constitution for all CLI tools
- No additional dependencies
- Comprehensive feature set (subcommands, help text, validation)
- Well-documented and widely understood

### 7. Configuration Management

**Decision**: JSON files + Pydantic for validation

**Rationale**:
- JSON is human-readable and easy to edit
- Specified in requirements (FR-003, FR-004)
- Pydantic provides runtime validation and clear error messages
- Type-safe configuration models with IDE support
- Easy to test with sample config files

**Alternatives Considered**:
- **YAML/TOML**: More human-friendly for complex configs, but JSON is sufficient for our needs (list of websites with URLs). Simpler to parse (standard library) and matches requirement.

### 8. Logging

**Decision**: Standard library `logging` with structured output support

**Rationale**:
- Standard library solution
- Supports both human-readable console output and JSON structured logs
- Built-in log levels (DEBUG, INFO, WARNING, ERROR)
- Easy to configure formatters for different output modes
- No additional dependencies needed

## Implementation Best Practices

### Polite Crawling
- Implement rate limiting between requests (e.g., 1-2 seconds delay)
- Parse and respect `robots.txt` using `urllib.robotparser` (standard library)
- Set appropriate User-Agent header identifying the tool
- Handle HTTP 429 (Too Many Requests) with exponential backoff
- Fail gracefully on individual site errors without stopping entire crawl

### Error Handling Strategy
- Network errors: Retry with exponential backoff (max 3 attempts)
- Invalid PDFs: Log error, record in metadata, continue crawling
- Azure storage errors: Retry with backoff, fail clearly if credentials invalid
- LLM API errors: Fall back to simple heuristics (look for .pdf links) if API unavailable
- Timeout handling: Set reasonable timeouts for HTTP requests (30s connect, 300s read)

### Testing Strategy
- **Unit tests**: Mock all external dependencies (HTTP, LLM API, Azure storage)
- **Integration tests**: Use real HTTP requests to test sites (with VCR.py for recording)
- **Contract tests**: Validate CLI interface, metadata JSON schema, configuration file format
- Test with small file limits (max-files=5) to avoid long test runs
- Use pytest fixtures for common test setup (mock configs, sample HTML)

### Security Considerations
- Validate all URLs before crawling (check scheme, avoid file:// protocol)
- Sanitize filenames to prevent directory traversal attacks
- Store Azure credentials in environment variables, never in config files
- Validate configuration JSON schema before processing
- Set maximum file size limit for downloads to prevent disk exhaustion
- Use HTTPS for all government website URLs

## Dependencies Summary

### Production Dependencies
```
httpx>=0.27.0           # Modern HTTP client with async support
beautifulsoup4>=4.12.0  # HTML parsing
openai>=1.0.0           # LLM integration for website analysis
azure-storage-file-datalake>=12.0.0  # ADLS Gen2 integration
pypdf>=4.0.0            # PDF validation
pydantic>=2.0.0         # Configuration validation
```

### Development Dependencies
```
pytest>=8.0.0           # Testing framework
pytest-asyncio>=0.23.0  # Async test support
pytest-mock>=3.12.0     # Mocking utilities
ruff>=0.1.0             # Linting and formatting
mypy>=1.8.0             # Type checking
vcrpy>=6.0.0            # HTTP interaction recording for tests
```

## Architecture Patterns

### Storage Abstraction
Create abstract base class `StorageBackend` with implementations:
- `LocalStorageBackend`: Write to local filesystem
- `ADLSStorageBackend`: Write to Azure Data Lake Storage Gen2

This allows testing without Azure credentials and easy addition of other storage backends (S3, GCS) in future.

### AI Scraper Strategy Pattern
1. Send website HTML structure to LLM with prompt template
2. LLM returns JSON with scraping strategy (CSS selectors, pagination logic)
3. Parse and validate strategy JSON
4. Execute strategy to extract PDF URLs
5. Fall back to simple heuristic (find all .pdf links) if LLM fails

### Metadata Tracking
- Single JSON file updated atomically after each successful download
- File locking to support potential future parallel writes
- Schema validation with Pydantic models
- Include all required fields from FR-011

## Performance Expectations

- **Sequential crawling** (parallelism=1): ~1-2 minutes per website
- **Parallel crawling** (parallelism=5): ~20-30 seconds per batch of 5 websites
- **10 websites with parallelism=5**: ~4-6 minutes total
- **LLM API latency**: ~2-5 seconds per website analysis
- **PDF download speed**: Depends on file size and network, typically 100-500 KB/s per file

## Open Questions and Future Enhancements

### Resolved in This Research
- ✅ Choice of web scraping library
- ✅ LLM integration approach
- ✅ Azure storage SDK selection
- ✅ Parallel processing strategy
- ✅ Testing approach

### Deferred for Future Iterations
- PDF content extraction and analysis (not required for v1)
- Distributed crawling across multiple machines (not needed at current scale)
- Database for metadata (JSON files sufficient for now)
- Web UI for monitoring crawls (CLI only for v1)
- Incremental crawling (detect already-downloaded files) - can add in v2
- Support for other cloud providers (S3, GCS) - ADLS Gen2 sufficient for v1

## Conclusion

This research has identified all primary dependencies and patterns needed for implementation. The chosen technologies prioritize:
1. **Simplicity**: Use standard library where possible, minimal dependencies
2. **Testability**: All external dependencies can be mocked
3. **Constitution compliance**: Follows all Python and main constitution requirements
4. **Flexibility**: AI-powered scraping allows adapting to different website structures
5. **Production-ready**: Proper error handling, logging, and observability

All NEEDS CLARIFICATION items from Technical Context have been resolved. Ready to proceed with Phase 1 design.

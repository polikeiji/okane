# CLI Interface Contract

**Feature**: 001-crawl-cashflow-pdfs  
**Version**: 1.0.0  
**Date**: 2026-01-19

## Overview

This document defines the command-line interface contract for the Okane PDF crawling tool. This contract MUST remain backward compatible within major versions.

## Main Command

```bash
okane [global-options] <subcommand> [subcommand-options]
```

### Global Options

- `--version`: Display version information and exit
- `--help`, `-h`: Display help message and exit
- `--verbose`, `-v`: Enable verbose logging (can be repeated: `-vv`, `-vvv`)
- `--quiet`, `-q`: Suppress non-error output

## Crawl Subcommand

```bash
okane crawl [options]
```

### Description

Crawl government websites to download political cash flow PDF reports.

### Required Arguments

- `--output-folder PATH`, `-o PATH`: Path to output folder where PDFs will be stored. Can be:
  - Local filesystem path (e.g., `/path/to/output` or `./output`)
  - Azure Data Lake Storage Gen2 path (e.g., `abfss://container@account.dfs.core.windows.net/path`)

### Optional Arguments

- `--config PATH`, `-c PATH`: Path to JSON configuration file specifying websites to crawl
  - Default: Use built-in default configuration with ~50 Japanese government sites
  - File format: See `config-schema.json`

- `--parallelism N`, `-p N`: Number of websites to crawl in parallel
  - Type: Positive integer
  - Default: `1` (sequential)
  - Recommended: `5` for optimal performance
  - Maximum: `10` (soft limit, higher values may cause rate limiting)

- `--max-files N`, `-m N`: Maximum total number of PDF files to download across all websites
  - Type: Positive integer
  - Default: unlimited (download all discovered PDFs)
  - Use case: Testing, sampling, limiting bandwidth usage

- `--log-level LEVEL`: Set logging level
  - Values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
  - Default: `INFO`

- `--log-format FORMAT`: Set log output format
  - Values: `text`, `json`
  - Default: `text` (human-readable)
  - JSON format useful for log aggregation systems

- `--timeout SECONDS`: Timeout for HTTP requests
  - Type: Positive integer
  - Default: `30` seconds (connection), `300` seconds (read)

- `--user-agent STRING`: Custom User-Agent header for HTTP requests
  - Default: `"Okane-Crawler/1.0.0 (+https://github.com/polikeiji/okane)"`

- `--dry-run`: Simulate crawl without downloading files
  - Useful for testing configuration and seeing what would be downloaded

### Environment Variables

- `AZURE_STORAGE_ACCOUNT_NAME`: Azure storage account name (required for ADLS Gen2)
- `AZURE_STORAGE_ACCOUNT_KEY`: Azure storage account key (required for ADLS Gen2)
- `AZURE_CLIENT_ID`: Azure AD client ID (alternative auth method)
- `AZURE_CLIENT_SECRET`: Azure AD client secret (alternative auth method)
- `AZURE_TENANT_ID`: Azure AD tenant ID (alternative auth method)
- `OPENAI_API_KEY`: OpenAI API key for AI-powered website analysis
- `OKANE_LOG_LEVEL`: Default log level (overridden by `--log-level`)

### Examples

#### Example 1: Basic crawl with default configuration
```bash
okane crawl --output-folder ./output
```

#### Example 2: Parallel crawl with custom configuration
```bash
okane crawl \
  --output-folder ./pdfs \
  --config my-sites.json \
  --parallelism 5
```

#### Example 3: Test crawl with file limit
```bash
okane crawl \
  --output-folder ./test \
  --max-files 10 \
  --log-level DEBUG
```

#### Example 4: Crawl to Azure Data Lake Storage Gen2
```bash
export AZURE_STORAGE_ACCOUNT_NAME=myaccount
export AZURE_STORAGE_ACCOUNT_KEY=mykey
export OPENAI_API_KEY=sk-...

okane crawl \
  --output-folder abfss://container@myaccount.dfs.core.windows.net/pdfs \
  --parallelism 5 \
  --log-format json
```

#### Example 5: Dry run to preview crawl
```bash
okane crawl \
  --output-folder ./output \
  --dry-run
```

### Exit Codes

- `0`: Success (all websites crawled successfully)
- `1`: Partial failure (some websites failed but some succeeded)
- `2`: Complete failure (all websites failed or critical error)
- `3`: Invalid arguments or configuration
- `4`: Authentication error (Azure or OpenAI credentials invalid)
- `5`: Permission error (output folder not writable)

### Standard Output

Progress information and summary are written to stdout in the selected format (text or JSON).

#### Text Format (Default)

```
Starting crawl...
Configuration: /path/to/config.json
Output folder: /path/to/output
Parallelism: 5

[1/10] Crawling: Ministry of Internal Affairs and Communications
  Analyzing website structure... done (3.2s)
  Found 12 PDF links
  Downloading PDFs... 12/12 done (45.3s)

[2/10] Crawling: Tokyo Prefecture Political Finance
  ...

Crawl completed in 5m 23s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary:
  Websites crawled: 9/10 (1 failed)
  PDFs downloaded: 127
  Total size: 245.3 MB
  Failed downloads: 3
  
Metadata saved to: /path/to/output/metadata.json
```

#### JSON Format

```json
{
  "status": "partial_success",
  "summary": {
    "total_websites": 10,
    "websites_crawled": 9,
    "websites_failed": 1,
    "total_pdfs_downloaded": 127,
    "total_pdfs_failed": 3,
    "total_bytes": 257343488,
    "duration_seconds": 323,
    "output_folder": "/path/to/output",
    "metadata_file": "/path/to/output/metadata.json"
  },
  "errors": [
    {
      "website_id": "site-xyz",
      "error": "Connection timeout",
      "timestamp": "2026-01-19T10:15:23Z"
    }
  ]
}
```

### Standard Error

Error messages and warnings are written to stderr.

#### Error Message Format (Text)

```
ERROR: Failed to crawl website 'site-xyz': Connection timeout
WARNING: PDF validation failed for 'file.pdf': Invalid PDF structure
ERROR: Authentication failed: Invalid Azure storage credentials
```

#### Error Message Format (JSON)

```json
{
  "level": "ERROR",
  "timestamp": "2026-01-19T10:15:23.456Z",
  "message": "Failed to crawl website 'site-xyz'",
  "error": "Connection timeout",
  "context": {
    "website_id": "site-xyz",
    "url": "https://example.com"
  }
}
```

## Contract Tests

Contract tests MUST verify:

1. **Command Existence**: `okane crawl` command exists and accepts specified arguments
2. **Exit Codes**: Correct exit codes for success, partial failure, and error scenarios
3. **Output Files**: Metadata JSON file created with valid schema
4. **Argument Validation**: Invalid arguments produce exit code 3 with error message
5. **Help Text**: `okane crawl --help` displays usage information
6. **Version**: `okane --version` displays version number
7. **Environment Variables**: Azure and OpenAI credentials read from environment
8. **Dry Run**: `--dry-run` produces output without creating files
9. **File Limits**: `--max-files` respected (stops after N files)
10. **Parallelism**: `--parallelism` accepts valid values, rejects invalid ones

## Backward Compatibility

### Guaranteed Stable (MAJOR version changes only)

- Command name: `okane crawl`
- Required argument: `--output-folder`
- Exit code meanings (0=success, non-zero=error)
- Metadata JSON schema (field additions allowed, field removal requires MAJOR bump)
- Default configuration file location

### May Change in MINOR versions

- New optional arguments (must not break existing usage)
- New environment variables
- Log message formats (text and JSON structure)
- Default values for optional arguments
- Performance characteristics

### May Change in PATCH versions

- Bug fixes in argument parsing
- Error message wording
- Help text improvements
- Default configuration content (adding new websites)

## Deprecation Policy

When an argument or feature needs to be removed:

1. Mark as deprecated in MINOR version (show warning when used)
2. Document removal date (minimum 6 months)
3. Remove in next MAJOR version
4. Provide migration guide in changelog

## Versioning

CLI version follows semantic versioning and MUST match package version in `pyproject.toml`.

Version displayed by `okane --version`:
```
Okane 1.0.0
Python 3.11.7
```

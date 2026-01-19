# Quickstart Guide: Crawl Political Cash Flow PDFs

**Feature**: 001-crawl-cashflow-pdfs  
**Date**: 2026-01-19  
**Status**: Design Complete

## Prerequisites

- Python 3.11 or higher
- `uv` package manager installed
- OpenAI API key (for AI-powered website analysis)
- Optional: Azure storage account (for ADLS Gen2 storage)

## Installation

```bash
# Clone the repository
git clone https://github.com/polikeiji/okane.git
cd okane

# Install with uv
uv sync

# Verify installation
uv run okane --version
```

## Basic Usage

### 1. Simple Local Crawl

Download PDFs from default government websites to a local folder:

```bash
# Set OpenAI API key
export OPENAI_API_KEY=sk-...

# Run crawl
uv run okane crawl --output-folder ./output
```

This will:
- Use the built-in configuration with ~50 Japanese government sites
- Download PDFs sequentially (parallelism=1)
- Store PDFs in `./output/pdfs/`
- Generate metadata in `./output/metadata.json`

### 2. Fast Parallel Crawl

Speed up crawling by processing multiple websites concurrently:

```bash
uv run okane crawl \
  --output-folder ./output \
  --parallelism 5
```

**Expected performance**: 10 websites in ~5 minutes (vs ~15 minutes sequential)

### 3. Test with File Limit

Limit the number of downloaded files for testing:

```bash
uv run okane crawl \
  --output-folder ./test \
  --max-files 10 \
  --log-level DEBUG
```

This downloads only 10 PDFs total across all websites, useful for:
- Testing the setup
- Validating configuration
- Trying out the tool without large downloads

### 4. Custom Website Configuration

Create a custom config file to crawl specific websites:

```bash
# Create custom configuration
cat > my-sites.json << 'EOF'
{
  "version": "1.0",
  "websites": [
    {
      "id": "tokyo-prefecture",
      "name": "Tokyo Prefecture Political Finance",
      "base_url": "https://www.senkyo.metro.tokyo.lg.jp/",
      "enabled": true
    },
    {
      "id": "osaka-prefecture",
      "name": "Osaka Prefecture Political Finance",
      "base_url": "https://www.pref.osaka.lg.jp/senkan/",
      "enabled": true
    }
  ]
}
EOF

# Run crawl with custom config
uv run okane crawl \
  --output-folder ./output \
  --config my-sites.json \
  --parallelism 2
```

### 5. Store to Azure Data Lake Storage Gen2

Upload PDFs directly to cloud storage:

```bash
# Set Azure credentials
export AZURE_STORAGE_ACCOUNT_NAME=myaccount
export AZURE_STORAGE_ACCOUNT_KEY=mykey
export OPENAI_API_KEY=sk-...

# Run crawl to ADLS Gen2
uv run okane crawl \
  --output-folder abfss://container@myaccount.dfs.core.windows.net/pdfs \
  --parallelism 5 \
  --log-format json
```

### 6. Dry Run (Preview Mode)

See what would be downloaded without actually downloading:

```bash
uv run okane crawl \
  --output-folder ./output \
  --dry-run
```

This will:
- Analyze all websites
- Report discovered PDF URLs
- Skip actual downloads
- Not create any files

## Understanding Output

### Directory Structure

```
output/
├── metadata.json           # Complete crawl metadata
└── pdfs/
    ├── ldp_2024-q1_financial-report.pdf
    ├── cdp_2024-q1_financial-report.pdf
    ├── komei_2024-q1_cash-flow.pdf
    └── ...
```

### Metadata File

The `metadata.json` contains comprehensive information about the crawl:

```json
{
  "crawl_id": "550e8400-e29b-41d4-a716-446655440000",
  "crawl_start_time": "2026-01-19T10:00:00Z",
  "crawl_end_time": "2026-01-19T10:25:00Z",
  "total_websites": 10,
  "websites_crawled": 9,
  "websites_failed": 1,
  "total_pdfs_downloaded": 127,
  "downloaded_files": [
    {
      "file_id": "...",
      "original_url": "https://www.soumu.go.jp/.../report.pdf",
      "filename": "ldp_2024-q1_financial-report.pdf",
      "sha256_hash": "a3b2c1...",
      "organization_name": "Liberal Democratic Party",
      "download_timestamp": "2026-01-19T10:05:00Z",
      ...
    }
  ],
  "errors": [...]
}
```

Key fields:
- `downloaded_files`: Array of all downloaded PDFs with metadata
- `sha256_hash`: For deduplication and integrity verification
- `original_url`: Source URL for traceability
- `errors`: Any errors encountered during crawl

## Common Workflows

### Development/Testing Workflow

```bash
# 1. Test with minimal downloads
uv run okane crawl -o ./test -m 5 --log-level DEBUG

# 2. Check output
ls -lh ./test/pdfs/
cat ./test/metadata.json | jq '.total_pdfs_downloaded'

# 3. Clean up
rm -rf ./test
```

### Production Crawl Workflow

```bash
# 1. Set credentials
export OPENAI_API_KEY=sk-...
export AZURE_STORAGE_ACCOUNT_NAME=prod-account
export AZURE_STORAGE_ACCOUNT_KEY=...

# 2. Run production crawl
uv run okane crawl \
  --output-folder abfss://okane@prodaccount.dfs.core.windows.net/pdfs \
  --parallelism 5 \
  --log-format json \
  > crawl.log 2>&1

# 3. Check results
echo $?  # Exit code (0=success)
tail crawl.log
```

### Scheduled/Automated Crawl

```bash
#!/bin/bash
# monthly-crawl.sh - Run via cron monthly

set -e

# Setup
export OPENAI_API_KEY=${OKANE_OPENAI_KEY}
export AZURE_STORAGE_ACCOUNT_NAME=myaccount
export AZURE_STORAGE_ACCOUNT_KEY=${OKANE_AZURE_KEY}

DATE=$(date +%Y%m%d)
OUTPUT_PATH="abfss://okane@myaccount.dfs.core.windows.net/crawls/$DATE"

# Run crawl
uv run okane crawl \
  --output-folder "$OUTPUT_PATH" \
  --parallelism 5 \
  --log-format json \
  >> /var/log/okane-crawl.log 2>&1

# Send notification
echo "Crawl completed: $DATE" | mail -s "Okane Crawl" admin@example.com
```

Add to crontab:
```
# Run on 1st day of each month at 2 AM
0 2 1 * * /path/to/monthly-crawl.sh
```

## Troubleshooting

### Error: Invalid OpenAI API Key

```
ERROR: Authentication failed: Invalid OpenAI API key
```

**Solution**: Verify your API key is set correctly:
```bash
echo $OPENAI_API_KEY  # Should show sk-...
export OPENAI_API_KEY=sk-your-actual-key
```

### Error: Output folder not writable

```
ERROR: Permission error: Output folder not writable
```

**Solutions**:
1. Check folder permissions: `ls -ld ./output`
2. Create folder first: `mkdir -p ./output`
3. For Azure: Verify storage account credentials

### Error: Connection timeout

```
ERROR: Failed to crawl website 'site-xyz': Connection timeout
```

**Solutions**:
1. Check internet connectivity
2. Increase timeout: `--timeout 60`
3. Try again later (government site may be down)

### Warning: Some PDFs failed to download

```
WARNING: 3 PDFs failed to download
```

**Normal behavior**: Some government websites may have:
- Broken links
- Temporarily unavailable files
- Access restrictions

**Action**: Check `metadata.json` `errors` array for details. Successfully downloaded files are still available.

## Configuration Reference

### Default Configuration

The built-in default configuration includes:

- **National sites**: Ministry of Internal Affairs and Communications, National Diet Library
- **47 prefectural sites**: All Japanese prefecture political finance disclosure sites

To see the default configuration:
```bash
uv run okane crawl --dry-run --log-level DEBUG 2>&1 | grep "Website:"
```

### Custom Configuration Format

See full schema: `specs/001-crawl-cashflow-pdfs/contracts/config-schema.json`

Minimal example:
```json
{
  "version": "1.0",
  "websites": [
    {
      "id": "unique-id",
      "name": "Website Name",
      "base_url": "https://example.com"
    }
  ]
}
```

With all optional fields:
```json
{
  "version": "1.0",
  "websites": [
    {
      "id": "tokyo-prefecture",
      "name": "Tokyo Prefecture Political Finance",
      "base_url": "https://www.senkyo.metro.tokyo.lg.jp/",
      "description": "Tokyo metropolitan area political reports",
      "crawl_frequency": "monthly",
      "enabled": true
    }
  ]
}
```

## Performance Tips

1. **Use parallelism**: Set `--parallelism 5` for ~3-5x speedup
2. **Limit max files for testing**: Use `--max-files 10` during development
3. **JSON logging for production**: Use `--log-format json` for structured logs
4. **Network-friendly**: Tool respects robots.txt and includes polite delays
5. **Incremental crawling**: v2 will support detecting already-downloaded files

## Next Steps

- **View metadata**: `cat output/metadata.json | jq '.downloaded_files | length'`
- **Analyze PDFs**: Use other Okane features to extract and analyze data (future features)
- **Automate crawls**: Set up scheduled crawls using cron or cloud schedulers
- **Monitor**: Check error logs and metadata for crawl health

## Getting Help

- CLI help: `uv run okane crawl --help`
- Full documentation: See `specs/001-crawl-cashflow-pdfs/` directory
- Issues: https://github.com/polikeiji/okane/issues

## Development Setup

For contributing or modifying the crawler:

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Run linter
uv run ruff check src/

# Format code
uv run ruff format src/

# Type check
uv run mypy src/
```

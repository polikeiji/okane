# Okane - Political Cash Flow PDF Crawler

A CLI tool for crawling political cash flow PDF reports from Japanese government websites using AI-powered website analysis.

## Features

- **AI-Powered Scraping**: Uses OpenAI LLMs to dynamically determine scraping strategies for different government websites
- **Parallel Processing**: Download PDFs from multiple websites concurrently for improved performance
- **Cloud Storage**: Store PDFs directly to Azure Data Lake Storage Gen2 or local filesystem
- **Comprehensive Metadata**: Track all downloads with detailed metadata including SHA-256 hashes, timestamps, and source URLs
- **Polite Crawling**: Respects robots.txt and implements proper rate limiting
- **Flexible Configuration**: Use default government sites or provide custom website lists

## Prerequisites

- Python 3.11 or higher
- `uv` package manager
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

## Quick Start

### Basic Local Crawl

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

### Fast Parallel Crawl

```bash
uv run okane crawl \
  --output-folder ./output \
  --parallelism 5
```

### Test with File Limit

```bash
uv run okane crawl \
  --output-folder ./test \
  --max-files 10 \
  --log-level DEBUG
```

### Custom Configuration

```bash
# Create custom config file
cat > my-sites.json << 'EOF'
{
  "version": "1.0",
  "websites": [
    {
      "id": "tokyo-prefecture",
      "name": "Tokyo Prefecture Political Finance",
      "base_url": "https://www.senkyo.metro.tokyo.lg.jp/",
      "enabled": true
    }
  ]
}
EOF

# Run crawl with custom config
uv run okane crawl \
  --output-folder ./output \
  --config my-sites.json
```

### Azure Data Lake Storage Gen2

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

## CLI Usage

```
okane crawl [options]

Required:
  --output-folder PATH, -o PATH     Output folder (local or Azure ADLS Gen2 path)

Optional:
  --config PATH, -c PATH            Custom website configuration JSON file
  --parallelism N, -p N             Number of websites to crawl in parallel (default: 1)
  --max-files N, -m N               Maximum total PDFs to download (default: unlimited)
  --log-level LEVEL                 Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  --log-format FORMAT               Log format (text, json)
  --timeout SECONDS                 HTTP request timeout (default: 30/300)
  --user-agent STRING               Custom User-Agent header
  --dry-run                         Preview crawl without downloading files
  --help, -h                        Show help message
```

## Output Structure

```
output/
├── metadata.json           # Complete crawl metadata
└── pdfs/
    ├── ldp_2024-q1_financial-report.pdf
    ├── cdp_2024-q1_financial-report.pdf
    └── ...
```

### Metadata Format

The `metadata.json` file contains:
- Crawl summary (websites crawled, PDFs downloaded, total size)
- Detailed information for each downloaded PDF
- SHA-256 hashes for integrity verification
- Source URLs for traceability
- Error logs for failed downloads

## Exit Codes

- `0`: Success (all websites crawled successfully)
- `1`: Partial failure (some websites failed but some succeeded)
- `2`: Complete failure (all websites failed or critical error)
- `3`: Invalid arguments or configuration
- `4`: Authentication error (Azure or OpenAI credentials invalid)
- `5`: Permission error (output folder not writable)

## Development

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

## Documentation

For detailed documentation, see:
- [Quick Start Guide](specs/001-crawl-cashflow-pdfs/quickstart.md)
- [CLI Interface Contract](specs/001-crawl-cashflow-pdfs/contracts/cli-interface.md)
- [Data Model](specs/001-crawl-cashflow-pdfs/data-model.md)
- [Implementation Plan](specs/001-crawl-cashflow-pdfs/plan.md)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please see the development setup above and follow the project's code style.

## Support

- Issues: https://github.com/polikeiji/okane/issues
- Documentation: See `specs/` directory

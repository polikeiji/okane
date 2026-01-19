# Implementation Plan: Crawl Political Cash Flow PDFs

**Branch**: `001-crawl-cashflow-pdfs` | **Date**: 2026-01-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-crawl-cashflow-pdfs/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature implements a CLI tool for crawling political cash flow report PDFs from Japanese government websites. The tool uses AI-powered website analysis to dynamically determine scraping strategies for different government sites, downloads PDFs with parallel processing capabilities, and stores them with comprehensive metadata in either local filesystem or Azure Data Lake Storage Gen2. The implementation must support configurable parallelism, file limits, and maintain detailed tracking of all crawled documents.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: httpx + beautifulsoup4 (web scraping), openai (LLM integration), azure-storage-file-datalake (ADLS Gen2), pypdf (PDF validation), pydantic (config validation)  
**Storage**: Local filesystem and Azure Data Lake Storage Gen2 (ADLS Gen2), JSON metadata files  
**Testing**: pytest with unit, integration, and contract tests; vcrpy for HTTP recording  
**Target Platform**: Linux/macOS CLI (cross-platform Python)  
**Project Type**: Single project (CLI tool with subcommands)  
**Performance Goals**: Complete crawl of 10 government websites within 30 minutes using parallelism=5; handle 50+ PDFs per website  
**Constraints**: Must respect robots.txt, implement polite crawling delays, handle network failures gracefully, support parallel processing up to configurable limit  
**Scale/Scope**: 50+ government websites (national + 47 prefectures), potentially thousands of PDFs per crawl, metadata tracking for all files

*All dependencies researched and justified in research.md*

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Main Constitution Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| Test-Driven Development | ✅ PASS | Will follow TDD - tests written before implementation |
| Integration Testing | ✅ PASS | Required for: CLI subcommand interface, Azure storage integration, LLM API integration, web scraping |
| Observability | ✅ PASS | CLI with structured logging, JSON and human-readable output, progress tracking, error context |
| Versioning & Breaking Changes | ✅ PASS | Will follow semantic versioning for CLI interface |
| Simplicity & YAGNI | ✅ PASS | Implementing only specified features, no speculative functionality |
| Documentation | ✅ PASS | README with usage, API docs for public interfaces, inline comments for complex logic |
| Security | ✅ PASS | Input validation, secure credential handling for Azure, robots.txt compliance |
| PR Workflow | ✅ PASS | Clean commit history, rebase workflow, code review |

### Python Constitution Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| Package Management (uv) | ✅ PASS | Will use uv for dependency management |
| CLI (argparse) | ✅ PASS | CLI tool will use argparse standard library |
| Code Quality (ruff) | ✅ PASS | Will use ruff for linting and formatting |
| Type Hints | ✅ PASS | All functions will have type hints |
| Project Structure | ✅ PASS | Will follow src/ and tests/ structure |
| Testing (pytest) | ✅ PASS | Will use pytest for all tests |
| Documentation | ✅ PASS | Google-style docstrings for all public APIs |
| Error Handling | ✅ PASS | Specific exceptions, meaningful error messages |
| Dependencies | ✅ PASS | Will minimize and justify all dependencies |
| Python Version | ✅ PASS | Target Python 3.11+ |

**Gate Status**: ✅ PASS - No violations detected. All constitution requirements will be met.

**Post-Design Re-evaluation (Phase 1 Complete)**: ✅ PASS - Design artifacts reviewed. All constitution requirements confirmed. No complexity violations introduced.

## Project Structure

### Documentation (this feature)

```text
specs/001-crawl-cashflow-pdfs/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── okane/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py           # Main CLI entry point
│   │   └── crawl.py          # Crawl subcommand implementation
│   ├── models/
│   │   ├── __init__.py
│   │   ├── config.py         # Configuration models
│   │   ├── metadata.py       # Metadata models
│   │   └── website.py        # Website configuration models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── crawler.py        # Core crawling logic
│   │   ├── scraper.py        # AI-powered scraping strategy
│   │   ├── storage.py        # Storage abstraction (local/Azure)
│   │   └── downloader.py     # PDF download handler
│   └── lib/
│       ├── __init__.py
│       ├── ai_analyzer.py    # LLM integration for website analysis
│       ├── pdf_utils.py      # PDF validation/utilities
│       └── url_utils.py      # URL handling and validation

tests/
├── contract/
│   ├── test_cli_interface.py        # CLI contract tests
│   └── test_metadata_format.py      # Metadata format contract
├── integration/
│   ├── test_azure_storage.py        # Azure storage integration
│   ├── test_llm_integration.py      # LLM API integration
│   └── test_crawl_workflow.py       # End-to-end crawl workflow
└── unit/
    ├── test_crawler.py               # Crawler unit tests
    ├── test_scraper.py               # Scraper unit tests
    ├── test_storage.py               # Storage unit tests
    └── test_models.py                # Model unit tests

config/
└── default_websites.json             # Default government website list

pyproject.toml                        # Project metadata and dependencies
README.md                             # Project documentation
```

**Structure Decision**: Single project structure selected as this is a standalone CLI tool. All code will be in `src/okane/` with clear separation between CLI interface, business logic (services), domain models, and utility libraries. Tests are organized by type (contract/integration/unit) following Python constitution requirements.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No complexity violations detected. The implementation follows all constitution principles with straightforward design patterns appropriate for a CLI tool.

---

## Planning Workflow Status

**Phase 0 - Research**: ✅ COMPLETE
- All technology dependencies researched and justified
- See: `research.md`

**Phase 1 - Design**: ✅ COMPLETE
- Data models defined with Pydantic validation
- CLI interface contract specified
- Configuration and metadata schemas defined
- Quickstart guide created
- Agent context updated (GitHub Copilot)
- See: `data-model.md`, `contracts/`, `quickstart.md`

**Phase 2 - Task Generation**: ⏸️ DEFERRED
- Task breakdown will be created separately using `/speckit.tasks` command
- See: Agent instructions specify this is NOT created by `/speckit.plan`

**Next Steps**:
1. Run `/speckit.tasks` to generate `tasks.md` with dependency-ordered implementation tasks
2. Begin implementation following TDD approach
3. Reference design artifacts during implementation

**Artifacts Generated**:
- ✅ `plan.md` (this file)
- ✅ `research.md` - Technology research and decisions
- ✅ `data-model.md` - Core entities and relationships
- ✅ `contracts/cli-interface.md` - CLI contract specification
- ✅ `contracts/config-schema.json` - Website configuration JSON schema
- ✅ `contracts/metadata-schema.json` - Crawl metadata JSON schema
- ✅ `quickstart.md` - User-facing quick start guide
- ✅ `.github/agents/copilot-instructions.md` - Updated with project context

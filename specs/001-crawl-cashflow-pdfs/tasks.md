# Tasks: Crawl Political Cash Flow PDFs

**Input**: Design documents from `/specs/001-crawl-cashflow-pdfs/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL per spec.md - NOT explicitly requested. Tasks focus on implementation only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths follow structure from plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure: src/okane/{cli,models,services,lib}, tests/{contract,integration,unit}, config/
- [X] T002 Initialize Python project with pyproject.toml including Python 3.11+, uv package manager config, and project metadata
- [X] T003 [P] Add production dependencies to pyproject.toml: httpx>=0.27.0, beautifulsoup4>=4.12.0, openai>=1.0.0, azure-storage-file-datalake>=12.0.0, pypdf>=4.0.0, pydantic>=2.0.0
- [X] T004 [P] Add development dependencies to pyproject.toml: pytest>=8.0.0, pytest-asyncio>=0.23.0, pytest-mock>=3.12.0, ruff>=0.1.0, mypy>=1.8.0, vcrpy>=6.0.0
- [X] T005 [P] Configure ruff linting and formatting in pyproject.toml following Python constitution
- [X] T006 [P] Configure mypy type checking in pyproject.toml with strict mode enabled
- [X] T007 Create src/okane/__init__.py with package version and exports
- [X] T008 Create README.md with project overview, installation instructions, and basic usage from quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create src/okane/models/__init__.py with all model exports
- [X] T010 [P] Implement WebsiteConfiguration model in src/okane/models/config.py with Pydantic validation (id, name, base_url, description, enabled fields)
- [X] T011 [P] Implement WebsiteConfigurationList model in src/okane/models/config.py with version and websites fields, unique ID validation
- [X] T012 [P] Implement ScrapingStrategy model in src/okane/models/website.py with strategy_type, pdf_link_selectors, confidence fields and validation
- [X] T013 [P] Implement DownloadedPDF model in src/okane/models/metadata.py with all FR-011 fields (file_id, original_url, sha256_hash, etc.)
- [X] T014 [P] Implement CrawlMetadata model in src/okane/models/metadata.py with crawl tracking fields (crawl_id, timestamps, counters, downloaded_files)
- [X] T015 Create src/okane/lib/__init__.py with library exports
- [X] T016 [P] Implement URL validation and sanitization utilities in src/okane/lib/url_utils.py (validate HTTP/HTTPS URLs, sanitize filenames)
- [X] T017 [P] Implement PDF validation utilities in src/okane/lib/pdf_utils.py using pypdf (validate PDF structure, extract metadata)
- [X] T018 Create src/okane/services/__init__.py with service exports
- [X] T019 Implement StorageBackend abstract base class in src/okane/services/storage.py with write_file, read_file, exists methods
- [X] T020 [P] Implement LocalStorageBackend in src/okane/services/storage.py for local filesystem operations with atomic writes
- [X] T021 Create config/default_websites.json with JSON structure from data-model.md containing national government sites (MIAC, National Diet Library)
- [X] T022 Add 47 Japanese prefectural political finance disclosure sites to config/default_websites.json following WebsiteConfigurationList schema
- [X] T023 Implement logging configuration in src/okane/lib/logging_config.py supporting both text and JSON formats with proper log levels
- [X] T024 Create src/okane/cli/__init__.py with CLI exports

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic PDF Crawling with Default Configuration (Priority: P1) 🎯 MVP

**Goal**: Enable researchers to collect all available political party cash flow reports from government websites using default settings with minimal parameters

**Independent Test**: Run the subcommand with only an output folder parameter and verify that PDFs are downloaded from default government websites with a metadata JSON file generated

### Implementation for User Story 1

- [X] T025 [P] [US1] Implement AI analyzer in src/okane/lib/ai_analyzer.py with OpenAI API integration to analyze HTML and return ScrapingStrategy
- [X] T026 [P] [US1] Implement robots.txt parser in src/okane/lib/url_utils.py using urllib.robotparser to check URL crawling permissions
- [X] T027 [US1] Implement website scraper service in src/okane/services/scraper.py that uses AI analyzer to determine scraping strategy and extract PDF URLs
- [X] T028 [US1] Implement PDF downloader service in src/okane/services/downloader.py with httpx to download files, calculate SHA-256 hash, validate PDFs
- [X] T029 [US1] Implement core crawler orchestrator in src/okane/services/crawler.py that coordinates scraper, downloader, storage for single website (sequential)
- [X] T030 [US1] Implement metadata tracking in src/okane/services/crawler.py to update CrawlMetadata with downloaded files and errors using atomic writes
- [X] T031 [US1] Implement CLI main entry point in src/okane/cli/main.py with argparse, global options (--version, --help, --verbose, --quiet)
- [X] T032 [US1] Implement crawl subcommand in src/okane/cli/crawl.py with --output-folder required argument and default config loading
- [X] T033 [US1] Add config validation in src/okane/cli/crawl.py to load and validate configuration JSON using WebsiteConfigurationList model
- [X] T034 [US1] Add output folder validation in src/okane/cli/crawl.py to check folder is writable before starting crawl
- [X] T035 [US1] Implement OpenAI API key validation in src/okane/cli/crawl.py checking OPENAI_API_KEY environment variable
- [X] T036 [US1] Add progress logging in src/okane/cli/crawl.py showing current website being crawled and PDFs discovered/downloaded
- [X] T037 [US1] Add summary output in src/okane/cli/crawl.py showing websites crawled, PDFs downloaded, total size, errors (text format)
- [X] T038 [US1] Implement error handling in src/okane/services/crawler.py for network failures, invalid PDFs with graceful continuation
- [X] T039 [US1] Implement exit code logic in src/okane/cli/crawl.py (0=success, 1=partial, 2=failure, 3=invalid args, 4=auth error, 5=permission error)
- [X] T040 [US1] Add polite crawling delays in src/okane/services/scraper.py (1-2 second delay between requests per research.md)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently with `okane crawl --output-folder ./output`

---

## Phase 4: User Story 2 - Custom Website Configuration (Priority: P2)

**Goal**: Allow researchers to crawl additional regional government websites not included in the default list using custom JSON configuration files

**Independent Test**: Create a custom JSON file with test websites, run the crawl with the config parameter, and verify PDFs are downloaded only from the specified websites

### Implementation for User Story 2

- [X] T041 [US2] Add --config/-c CLI argument in src/okane/cli/crawl.py to accept custom configuration file path
- [X] T042 [US2] Implement custom config loading in src/okane/cli/crawl.py that loads JSON file and validates with WebsiteConfigurationList model
- [X] T043 [US2] Add JSON schema validation error handling in src/okane/cli/crawl.py with clear error messages for invalid configuration format
- [X] T044 [US2] Add URL validation in config loading to detect and report invalid URLs in configuration with specific error messages per site
- [X] T045 [US2] Update crawler logic in src/okane/services/crawler.py to handle mix of valid and invalid URLs, logging errors without stopping crawl
- [X] T046 [US2] Update summary output in src/okane/cli/crawl.py to indicate whether default or custom configuration was used

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - default config and custom config

---

## Phase 5: User Story 3 - Parallel Processing for Performance (Priority: P3)

**Goal**: Enable researchers to crawl dozens of government websites efficiently by processing multiple websites simultaneously

**Independent Test**: Run the same crawl with parallelism=1 and parallelism=5, measure execution time difference, and verify all PDFs are downloaded correctly in both cases

### Implementation for User Story 3

- [X] T047 [US3] Add --parallelism/-p CLI argument in src/okane/cli/crawl.py accepting positive integer with default value of 1
- [X] T048 [US3] Validate parallelism argument in src/okane/cli/crawl.py (must be positive integer, reject invalid values with exit code 3)
- [X] T049 [US3] Implement parallel crawler in src/okane/services/crawler.py using concurrent.futures.ThreadPoolExecutor for website-level parallelism
- [X] T050 [US3] Add thread-safe metadata updates in src/okane/services/crawler.py using locks to prevent concurrent write conflicts
- [X] T051 [US3] Update progress logging in src/okane/cli/crawl.py to show parallel website crawling status (e.g., "[1,3,5/10] Crawling...")
- [X] T052 [US3] Add error isolation in src/okane/services/crawler.py to ensure one website error doesn't affect parallel tasks
- [X] T053 [US3] Update summary output in src/okane/cli/crawl.py to show parallelism level used

**Checkpoint**: All user stories 1-3 should now be independently functional - basic, custom config, and parallel modes

---

## Phase 6: User Story 4 - Limited File Crawling for Testing (Priority: P3)

**Goal**: Enable developers and researchers to test crawling functionality or sample a subset of reports without downloading all available PDFs

**Independent Test**: Run the crawl with max-files=10 on a website with 50+ PDFs, verify exactly 10 PDFs are downloaded and the crawl stops gracefully

### Implementation for User Story 4

- [X] T054 [US4] Add --max-files/-m CLI argument in src/okane/cli/crawl.py accepting optional positive integer (default: None for unlimited)
- [X] T055 [US4] Validate max-files argument in src/okane/cli/crawl.py (must be positive if provided, reject 0 or negative)
- [X] T056 [US4] Implement global file counter in src/okane/services/crawler.py to track total files downloaded across all websites
- [X] T057 [US4] Add max-files check in src/okane/services/downloader.py before each download, stop if limit reached
- [X] T058 [US4] Add "limit reached" logging in src/okane/services/crawler.py when max-files limit is hit
- [X] T059 [US4] Update metadata in src/okane/models/metadata.py to include max_files_limit field in CrawlMetadata
- [X] T060 [US4] Update summary output in src/okane/cli/crawl.py to indicate if max-files limit was applied and reached

**Checkpoint**: User stories 1-4 all work independently - basic, custom config, parallel, and file limits

---

## Phase 7: User Story 5 - Cloud Storage Integration (Priority: P4)

**Goal**: Enable organizations to store crawled PDFs directly in Azure Data Lake Storage Gen2 for enterprise data pipelines

**Independent Test**: Configure an ADLS Gen2 output path, run the crawl, and verify PDFs and metadata are stored in the cloud storage location with proper authentication

### Implementation for User Story 5

- [X] T061 [US5] Implement ADLSStorageBackend in src/okane/services/storage.py using azure-storage-file-datalake SDK
- [X] T062 [US5] Add Azure credential loading in src/okane/services/storage.py from environment variables (AZURE_STORAGE_ACCOUNT_NAME, AZURE_STORAGE_ACCOUNT_KEY)
- [X] T063 [US5] Add ADLS Gen2 path detection in src/okane/cli/crawl.py (check for abfss:// scheme in output-folder)
- [X] T064 [US5] Implement storage backend selection in src/okane/cli/crawl.py based on output folder path (local vs ADLS)
- [X] T065 [US5] Add Azure authentication validation in src/okane/cli/crawl.py before starting crawl (check credentials early, exit code 4 if invalid)
- [X] T066 [US5] Implement retry logic in src/okane/services/storage.py for Azure upload failures with exponential backoff
- [X] T067 [US5] Add network interruption handling in src/okane/services/storage.py to retry uploads and log permanent failures in metadata
- [X] T068 [US5] Update metadata to track storage backend type in src/okane/models/metadata.py (storage_backend field: "local" or "adls")
- [X] T069 [US5] Update summary output in src/okane/cli/crawl.py to indicate storage backend used (local or Azure)

**Checkpoint**: All user stories 1-5 should now be independently functional - full feature set complete

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T070 [P] Add --log-level CLI argument in src/okane/cli/crawl.py (DEBUG, INFO, WARNING, ERROR, CRITICAL) with default INFO
- [ ] T071 [P] Add --log-format CLI argument in src/okane/cli/crawl.py (text, json) with default text
- [ ] T072 [P] Implement JSON log output format in src/okane/lib/logging_config.py with structured error messages per contract
- [ ] T073 [P] Add --timeout CLI argument in src/okane/cli/crawl.py with default 30s connect, 300s read
- [ ] T074 [P] Add --user-agent CLI argument in src/okane/cli/crawl.py with default "Okane-Crawler/1.0.0 (+https://github.com/polikeiji/okane)"
- [ ] T075 [P] Add --dry-run CLI argument in src/okane/cli/crawl.py to simulate crawl without downloading files
- [ ] T076 [P] Implement dry-run mode in src/okane/services/crawler.py showing discovered PDFs without actual downloads
- [ ] T077 [P] Add JSON summary output support in src/okane/cli/crawl.py when --log-format json is specified
- [ ] T078 [P] Create contract tests in tests/contract/test_cli_interface.py verifying all CLI arguments and exit codes
- [ ] T079 [P] Create contract tests in tests/contract/test_metadata_format.py validating metadata.json schema compliance
- [ ] T080 Add integration test in tests/integration/test_crawl_workflow.py for end-to-end crawl with sample websites
- [ ] T081 [P] Add unit tests in tests/unit/test_models.py for all Pydantic model validation rules
- [ ] T082 [P] Add unit tests in tests/unit/test_storage.py for LocalStorageBackend and ADLSStorageBackend
- [ ] T083 [P] Add unit tests in tests/unit/test_crawler.py for crawler orchestration logic with mocked dependencies
- [ ] T084 Update README.md with complete usage documentation from quickstart.md including all CLI options
- [ ] T085 Add .gitignore file to exclude Python cache, uv venv, build artifacts, and downloaded PDFs from test runs
- [ ] T086 Validate all code with ruff linter and formatter: `uv run ruff check src/ tests/ && uv run ruff format src/ tests/`
- [ ] T087 Run mypy type checker on all code: `uv run mypy src/`
- [ ] T088 Run complete test suite: `uv run pytest tests/` and verify all tests pass
- [ ] T089 Execute quickstart.md validation: run basic crawl with max-files=5 to verify end-to-end functionality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P3 → P4)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent, extends US1 config loading
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent, adds parallelism to US1 crawler
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Independent, adds file limits to US1 downloader
- **User Story 5 (P4)**: Can start after Foundational (Phase 2) - Independent, adds Azure storage backend

### Within Each User Story

- Core models and utilities before services
- Services before CLI integration
- CLI arguments before handler implementation
- Error handling integrated throughout
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005, T006)
- All Foundational model creation marked [P] can run in parallel (T010, T011, T012, T013, T014, T016, T017, T020)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within User Story 1: T025, T026 can run in parallel (AI analyzer and robots.txt parser)
- All Polish tasks marked [P] can run in parallel (T070-T079, T081-T083)

---

## Parallel Example: User Story 1

```bash
# Launch foundational models together (Phase 2):
Task T010: "Implement WebsiteConfiguration model in src/okane/models/config.py"
Task T011: "Implement WebsiteConfigurationList model in src/okane/models/config.py"
Task T012: "Implement ScrapingStrategy model in src/okane/models/website.py"
Task T013: "Implement DownloadedPDF model in src/okane/models/metadata.py"
Task T014: "Implement CrawlMetadata model in src/okane/models/metadata.py"

# Launch User Story 1 services together (Phase 3):
Task T025: "Implement AI analyzer in src/okane/lib/ai_analyzer.py"
Task T026: "Implement robots.txt parser in src/okane/lib/url_utils.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
   ```bash
   uv run okane crawl --output-folder ./output --max-files 5
   ```
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!) 
   - Basic crawling with default config works
3. Add User Story 2 → Test independently → Deploy/Demo
   - Custom config support added
4. Add User Story 3 → Test independently → Deploy/Demo
   - Parallel processing for performance
5. Add User Story 4 → Test independently → Deploy/Demo
   - File limits for testing/sampling
6. Add User Story 5 → Test independently → Deploy/Demo
   - Cloud storage integration for production
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (P1) - MVP priority
   - Developer B: User Story 2 (P2) - Custom config
   - Developer C: User Story 3 (P3) - Parallelism
   - Developer D: User Story 4 (P3) - File limits
   - Developer E: User Story 5 (P4) - Azure integration
3. Stories complete and integrate independently
4. Team collaborates on Phase 8 Polish

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are OPTIONAL per spec.md - not explicitly requested, so implementation-focused
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks follow TDD approach per constitution even without explicit test tasks
- Verify functionality after each phase completion
- Use vcrpy for HTTP recording in integration tests to avoid hitting real government sites
- Mock OpenAI API and Azure storage in unit tests

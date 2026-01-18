<!--
SYNC IMPACT REPORT
===================
Version Change: 1.0.0 → 1.1.0 (MINOR: New development workflow principles added)

Modified Principles:
  - Enhanced Development Workflow section with PR and commit organization requirements

Added Sections:
  - Pull Request Workflow subsection under Development Workflow
  - Branch Management and Commit Organization requirements

Removed Sections:
  - None

Templates Status:
  ✅ plan-template.md - Reviewed, no changes needed (focuses on feature planning)
  ✅ spec-template.md - Reviewed, no changes needed (focuses on requirements)
  ✅ tasks-template.md - Reviewed, no changes needed (focuses on task organization)

Follow-up TODOs:
  - None - all placeholders filled
-->

# Okane Project Constitution

**Version**: 1.1.0 | **Ratified**: 2026-01-18 | **Last Amended**: 2026-01-18

This constitution defines the mandatory principles and practices for the Okane project across all programming languages and technologies.

## Language-Specific Constitutions

This constitution contains **language-agnostic** principles that apply to all code in the Okane project. Language-specific requirements are defined in separate constitution documents:

- **Python**: `.specify/memory/constitutions/python.md` - Covers argparse, uv, ruff, and Python-specific practices
- **Bicep**: `.specify/memory/constitutions/bicep.md` - Placeholder for infrastructure as code practices

All language-specific constitutions are subordinate to and MUST NOT contradict this main constitution. When developing in a specific language, developers MUST comply with both this document and the relevant language-specific constitution.

## Core Principles

### I. Test-Driven Development (NON-NEGOTIABLE)

**Test-Driven Development (TDD) is mandatory for all feature development.**

- Tests MUST be written before implementation code
- Follow the Red-Green-Refactor cycle strictly:
  1. **Red**: Write a failing test that defines desired functionality
  2. **Green**: Write minimal code to make the test pass
  3. **Refactor**: Improve code quality while keeping tests passing
- All tests MUST fail initially before implementation begins
- Tests MUST be reviewed and approved before implementation starts
- No implementation code without corresponding tests

**Rationale**: TDD ensures code correctness, provides living documentation, enables confident refactoring, and drives better design through testability requirements.

### II. Integration Testing

**Integration tests are required for critical interaction points.**

- Integration tests MUST cover:
  - New library/module contracts
  - Changes to existing contracts or interfaces
  - Inter-service or inter-module communication
  - Shared data schemas and formats
- Integration tests verify components work together correctly
- Mock external dependencies only when necessary (prefer real dependencies in integration tests)
- Document integration test scenarios and expected behaviors

**Rationale**: Unit tests verify individual components, but integration tests catch issues in how components interact, preventing integration failures in production.

### III. Observability

**All code MUST be observable and debuggable.**

- Implement structured logging with appropriate log levels
- Log meaningful context (request IDs, user IDs, operation names)
- Use text-based I/O protocols where possible for debuggability:
  - Input from stdin/arguments → Output to stdout
  - Errors to stderr
- Support both JSON and human-readable output formats
- Include timing and performance metrics for critical operations
- Instrument error paths with detailed context

**Rationale**: Observable systems are debuggable systems. Text-based protocols and structured logging enable effective troubleshooting in development and production.

### IV. Versioning & Breaking Changes

**All public interfaces MUST follow semantic versioning.**

- Use MAJOR.MINOR.PATCH versioning format:
  - **MAJOR**: Incompatible API changes
  - **MINOR**: Backward-compatible functionality additions
  - **PATCH**: Backward-compatible bug fixes
- Document all breaking changes clearly
- Provide migration guides for major version bumps
- Deprecate features before removal when possible
- Maintain backward compatibility within major versions

**Rationale**: Semantic versioning provides clear expectations about compatibility and enables users to make informed upgrade decisions.

### V. Simplicity & YAGNI

**Start simple and avoid premature complexity.**

- Follow the YAGNI principle (You Aren't Gonna Need It)
- Implement only what is currently needed
- Avoid speculative generalization or abstraction
- Add complexity only when justified by real requirements
- Document and justify any complexity introduced
- Prefer simple, obvious solutions over clever ones

**Rationale**: Simple code is easier to understand, test, maintain, and change. Premature complexity creates maintenance burden without proven benefit.

### VI. Documentation

**Code and features MUST be adequately documented.**

- Maintain up-to-date README files with:
  - Project purpose and goals
  - Installation instructions
  - Basic usage examples
  - Links to detailed documentation
- Document public APIs, interfaces, and contracts
- Include inline comments for non-obvious logic
- Maintain design documentation for significant features
- Keep documentation close to code (prefer in-repo docs)

**Rationale**: Good documentation reduces onboarding time, prevents misuse, and captures design decisions for future reference.

### VII. Security

**Security is a mandatory consideration at all stages.**

- Follow secure coding practices for the language/framework
- Validate and sanitize all external input
- Use parameterized queries for database operations
- Implement proper authentication and authorization
- Log security-relevant events
- Keep dependencies updated for security patches
- Review security implications during code review
- Document security considerations and threat models

**Rationale**: Security vulnerabilities can have severe consequences. Prevention through secure development practices is more effective than remediation.

## Development Workflow

### Pull Request Workflow

All code changes MUST follow proper pull request workflow:

- Developers MUST organize commits in their working branch logically and clearly before creating a PR:
  - Use meaningful commit messages that explain the "why" not just the "what"
  - Group related changes into cohesive commits
  - Avoid mixing unrelated changes in a single commit
  - Squash or reorder commits to create a clean, reviewable history
  - Each commit should represent a logical unit of work
- PRs MUST be rebased to the main branch when PRs are approved:
  - Resolve any merge conflicts locally in the feature branch
  - Rebase onto the latest main branch before merging
  - Ensure all tests pass after rebasing
  - No merge commits in the main branch history
  - Fast-forward merges preferred to maintain linear history

**Rationale**: Clean commit history improves code review quality, makes debugging easier through `git bisect`, simplifies rollbacks, and provides clear documentation of changes. Rebasing ensures a linear history that is easier to understand and navigate.

### Code Review Requirements

All code changes MUST undergo code review before merging:

- At least one approving review required
- Reviewers MUST verify:
  - Compliance with this constitution and language-specific constitutions
  - Test coverage and quality
  - Security considerations
  - Documentation completeness
  - Code clarity and maintainability
  - Commit organization and history quality
- Address review feedback before merging

### Quality Gates

Before merging, code MUST pass:

- All automated tests (unit, integration, contract)
- Linting and formatting checks
- Security scanning (if applicable)
- Code review approval
- Constitution compliance verification

### Complexity Justification

Any complexity that violates simplicity principles MUST be justified:

- Document why the complexity is necessary
- Explain why simpler alternatives were rejected
- Track as technical debt if temporary
- Include mitigation plan if possible

## Governance

This constitution supersedes all other development practices and guidelines within the Okane project.

**Amendments**: Changes to this constitution require:

1. Documentation of rationale and impact assessment
2. Review and approval from project maintainers
3. Migration plan for any breaking changes
4. Version bump following semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes or removals
   - **MINOR**: New principles or significant guidance additions
   - **PATCH**: Clarifications, wording improvements, or non-semantic refinements

**Compliance**: All pull requests and code reviews MUST verify compliance with this constitution and applicable language-specific constitutions.

**Exceptions**: Any exceptions to these principles must be:

- Explicitly documented with justification
- Reviewed and approved by maintainers
- Tracked and revisited periodically

**Related Documents**:

- Language-specific constitutions in `.specify/memory/constitutions/`
- Template files in `.specify/templates/`
- Project documentation in repository root

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### 🔍 Advanced CLI Features

- **Dry-run mode** (`--dry-run`): Preview analysis without processing files or cloning repositories
- **Print-only mode** (`--print-only`): Output directly to console instead of writing files
- **Debug mode** (`--keep-temp`): Preserve temporary directories for debugging and development
- Enhanced help documentation with comprehensive examples and usage patterns

#### 🛡️ Security & Validation Enhancements

- **Output format validation**: Added Pydantic field validator to restrict formats to ["txt", "json", "markdown"]
- **Early validation**: Moved input validation to the beginning of parsing pipeline for fail-fast behavior
- **Markdown security**: Added triple-backtick escaping to prevent markdown parser conflicts
- **Shell safety**: Enhanced command handling with `shlex` import for future security improvements

#### 📊 Output Format Improvements

- **Enhanced markdown formatting**: Improved structure with proper escaping and formatting
- **Centralized output rendering**: Unified output file writing across all formats
- **JSON format enhancements**: Better structured data output for programmatic use
- **Token estimation**: Improved accuracy and formatting of token count estimates

#### 📚 Documentation Enhancements

- **Comprehensive README**: Added detailed sections for all new features with examples
- **Advanced usage patterns**: Complete examples for complex use cases
- **Feature categorization**: Organized features by use case (basic, advanced, filtering, etc.)
- **Code documentation**: Enhanced docstrings with detailed explanations, examples, and security notes

#### 🔐 GitHub Authentication Documentation

- **AUTHENTICATION.md**: Comprehensive guide covering authenticated vs unauthenticated access
- **Capability comparison table**: Clear breakdown of features available with/without authentication
- **Step-by-step PAT setup**: Detailed GitHub Personal Access Token creation guide
- **Security best practices**: Complete security guidelines for token handling
- **Rate limiting documentation**: Detailed explanation of GitHub API rate limits
- **Troubleshooting guide**: Common authentication issues and solutions
- **Enhanced README authentication section**: Integrated authentication guide with examples
- **API documentation updates**: Comprehensive authentication parameter documentation

### Changed

#### 🏗️ Architecture Improvements

- **Centralized output handling**: Eliminated redundant formatting logic across modules
- **Enhanced error handling**: Improved cleanup and error reporting with user-friendly messages
- **Modular design**: Better separation of concerns between parsing, formatting, and output
- **Clean code principles**: Applied Uncle Bob's principles throughout the codebase

#### 🔧 Developer Experience

- **Enhanced debugging**: Better temporary directory management with preservation options
- **Improved logging**: More informative debug messages and error reporting
- **Code organization**: Better module structure with comprehensive documentation

### Fixed

#### 🐛 Bug Fixes

- **Output format consistency**: Ensured consistent behavior across all output formats
- **Error handling**: Improved graceful failure handling with informative messages
- **Cleanup reliability**: Enhanced temporary directory cleanup with better error handling

### Security

#### 🔒 Security Improvements

- **Input validation**: Comprehensive validation of all user inputs
- **Markdown injection prevention**: Proper escaping of user content in markdown output
- **Pattern validation**: Enhanced security for file pattern matching
- **Token handling**: Secure handling of GitHub Personal Access Tokens

## Implementation Details

### New CLI Options

```bash
# Dry-run mode - preview without processing
gitingest --dry-run https://github.com/user/repo

# Print-only mode - output to console
gitingest --print-only --output-format json .

# Debug mode - keep temporary files
gitingest --keep-temp https://github.com/user/repo

# Combined usage
gitingest --dry-run --output-format markdown --include-pattern "*.py" .
```

### GitHub Authentication Features

#### Unauthenticated Access (Default)

- ✅ Public repositories
- ❌ Private repositories
- 60 requests/hour rate limit
- Basic error messages

#### Authenticated Access (With PAT Token)

- ✅ Public repositories
- ✅ Private repositories (if permitted)
- 5,000 requests/hour rate limit (83x improvement)
- Enhanced error messages and validation
- User repository listing capabilities

#### Authentication Setup

```bash
# Environment variable (recommended)
export GITHUB_TOKEN="your_token_here"
gitingest https://github.com/private/repo

# CLI flag (less secure)
gitingest --pat-token "your_token_here" https://github.com/private/repo
```

### Enhanced Output Formats

#### Text Format (Default)

- Optimized for LLM prompts
- Includes token count estimation
- Clean, readable structure

#### JSON Format

- Structured data for programmatic use
- Separate sections for summary, structure, and content
- Easy integration with other tools

#### Markdown Format

- Human-readable with proper formatting
- Security-enhanced with backtick escaping
- Suitable for documentation and reports

### Security Enhancements

#### Input Validation

- Early validation of output formats
- Pattern validation for file filtering
- Comprehensive error messages

#### Markdown Security

- Triple-backtick escaping prevents parser conflicts
- Safe handling of user-generated content
- Maintains formatting while ensuring security

#### Authentication Security

- Environment variable token storage
- Secure token handling throughout codebase
- No token logging or exposure
- Comprehensive security best practices documentation

### Developer Features

#### Debug Mode

- Temporary directory preservation for inspection
- Enhanced logging and error reporting
- Useful for development and troubleshooting

#### Centralized Architecture

- Unified output handling across all formats
- Reduced code duplication
- Easier maintenance and testing

## Migration Guide

### For CLI Users

All existing commands continue to work without changes. New features are opt-in:

```bash
# Existing usage (unchanged)
gitingest .
gitingest https://github.com/user/repo

# New features (optional)
gitingest --dry-run .                    # Preview mode
gitingest --print-only .                 # Console output
gitingest --output-format json .         # JSON format

# Authentication (for private repos)
export GITHUB_TOKEN="your_token_here"
gitingest https://github.com/private/repo
```

### For Python API Users

The existing API remains fully compatible:

```python
# Existing usage (unchanged)
from gitingest import ingest, ingest_async

summary, tree, content = ingest(".")
result = await ingest_async("https://github.com/user/repo")

# New authentication features
import os
result = await ingest_async(
    source="https://github.com/private/repo",
    pat_token=os.getenv("GITHUB_TOKEN")
)
```

## Documentation Structure

The project now includes comprehensive documentation:

### Core Documentation

- **README.md**: Enhanced with authentication section and capability comparison
- **API_DOCUMENTATION.md**: Complete API reference with authentication examples
- **CHANGELOG.md**: Detailed changelog with authentication improvements

### Authentication Documentation

- **AUTHENTICATION.md**: Comprehensive authentication guide including:
  - Capability comparison table
  - Step-by-step PAT token setup
  - Security best practices
  - Rate limiting explanation
  - Troubleshooting guide
  - Practical examples for CLI and Python API

### Key Authentication Features Documented

- Automatic authentication detection
- Fallback to unauthenticated access
- Enhanced error messages with authentication
- Rate limit improvements (60/hour → 5,000/hour)
- Private repository access
- Organization repository support
- Security best practices and token management

## Contributors

- Enhanced by the Gitingest development team
- Following Uncle Bob's clean code principles
- Comprehensive testing and validation
- Security-first approach to all improvements
- Complete authentication documentation and implementation

---

**Note**: This release maintains full backward compatibility while adding powerful new features for enhanced usability, security, developer experience, and comprehensive GitHub authentication support.

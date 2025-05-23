# Gitingest API Documentation

This document provides comprehensive documentation for the Gitingest Python API and CLI interface.

## Table of Contents

- [Python API](#python-api)
  - [Synchronous Interface](#synchronous-interface)
  - [Asynchronous Interface](#asynchronous-interface)
  - [Parameters](#parameters)
  - [Return Values](#return-values)
- [CLI Interface](#cli-interface)
  - [Basic Usage](#basic-usage)
  - [Advanced Options](#advanced-options)
  - [Output Formats](#output-formats)
  - [Debugging Features](#debugging-features)
- [Data Models](#data-models)
- [Examples](#examples)
- [Error Handling](#error-handling)

## Python API

### Synchronous Interface

```python
from gitingest import ingest

def ingest(
    source: str,
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB
    include_patterns: Optional[Union[str, Set[str]]] = None,
    exclude_patterns: Optional[Union[str, Set[str]]] = None,
    branch: Optional[str] = None,
    output: Optional[str] = None,
) -> Tuple[str, str, str]:
    """
    Synchronously analyze a source and return analysis results.

    Parameters
    ----------
    source : str
        Local directory path or Git repository URL
    max_file_size : int, optional
        Maximum file size in bytes (default: 10MB)
    include_patterns : Union[str, Set[str]], optional
        File patterns to include (e.g., "*.py", {"*.py", "*.md"})
    exclude_patterns : Union[str, Set[str]], optional
        File patterns to exclude
    branch : str, optional
        Git branch to analyze (for repositories)
    output : str, optional
        Output file path (if None, no file is written)

    Returns
    -------
    Tuple[str, str, str]
        (summary, directory_structure, file_contents)
    """
```

### Asynchronous Interface

```python
from gitingest import ingest_async

async def ingest_async(
    source: str,
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB
    include_patterns: Optional[Union[str, Set[str]]] = None,
    exclude_patterns: Optional[Union[str, Set[str]]] = None,
    branch: Optional[str] = None,
    output: Optional[str] = None,
    include_summary: bool = True,
    include_structure: bool = True,
    include_content: bool = True,
    output_format: str = "txt",
    pat_token: Optional[str] = None,
    keep_temp: bool = False,
) -> Tuple[str, str, str]:
    """
    Asynchronously analyze a source and return analysis results.

    Parameters
    ----------
    source : str
        Local directory path or Git repository URL
    max_file_size : int, optional
        Maximum file size in bytes (default: 10MB)
    include_patterns : Union[str, Set[str]], optional
        File patterns to include
    exclude_patterns : Union[str, Set[str]], optional
        File patterns to exclude
    branch : str, optional
        Git branch to analyze
    output : str, optional
        Output file path
    include_summary : bool, optional
        Include summary section (default: True)
    include_structure : bool, optional
        Include directory structure (default: True)
    include_content : bool, optional
        Include file contents (default: True)
    output_format : str, optional
        Output format: "txt", "json", or "markdown" (default: "txt")
    pat_token : str, optional
        GitHub Personal Access Token for private repositories
    keep_temp : bool, optional
        Keep temporary directories for debugging (default: False)

    Returns
    -------
    Tuple[str, str, str]
        (summary, directory_structure, file_contents)
    """
```

### Parameters

#### `source`

- **Type**: `str`
- **Required**: Yes
- **Description**: The source to analyze
- **Examples**:
  - Local directory: `"."`, `"/path/to/project"`
  - GitHub URL: `"https://github.com/user/repo"`
  - GitHub with branch: `"https://github.com/user/repo/tree/main"`
  - GitHub with subpath: `"https://github.com/user/repo/tree/main/src"`

#### `max_file_size`

- **Type**: `int`
- **Default**: `10485760` (10 MB)
- **Description**: Maximum file size in bytes to process
- **Example**: `1048576` (1 MB)

#### `include_patterns`

- **Type**: `Union[str, Set[str]]`
- **Default**: `None`
- **Description**: File patterns to include in analysis
- **Examples**:
  - Single pattern: `"*.py"`
  - Multiple patterns: `{"*.py", "*.md", "*.txt"}`
  - Complex patterns: `{"src/**/*.py", "docs/*.md"}`

#### `exclude_patterns`

- **Type**: `Union[str, Set[str]]`
- **Default**: `None` (uses default ignore patterns)
- **Description**: File patterns to exclude from analysis
- **Examples**:
  - Single pattern: `"*.log"`
  - Multiple patterns: `{"*.log", "node_modules/*", "*.tmp"}`

#### `output_format`

- **Type**: `str`
- **Default**: `"txt"`
- **Options**: `"txt"`, `"json"`, `"markdown"`
- **Description**: Format for output generation

#### `pat_token`

- **Type**: `str`
- **Default**: `None`
- **Description**: GitHub Personal Access Token for private repository access
- **Security**: Handle securely, never log or expose

### Return Values

All functions return a tuple of three strings:

1. **Summary** (`str`): Repository/directory metadata and statistics
2. **Directory Structure** (`str`): Tree-like representation of the file structure
3. **File Contents** (`str`): Concatenated contents of all analyzed files

## CLI Interface

### Basic Usage

```bash
# Analyze current directory
gitingest .

# Analyze specific directory
gitingest /path/to/project

# Analyze GitHub repository
gitingest https://github.com/user/repo

# Analyze specific branch
gitingest -b develop https://github.com/user/repo
```

### Advanced Options

#### Output Control

```bash
# Custom output file
gitingest -o analysis.txt .

# Different output formats
gitingest --output-format json .
gitingest --output-format markdown .

# Control output sections
gitingest --no-include-content .      # Skip file contents
gitingest --no-include-structure .    # Skip directory tree
gitingest --no-include-summary .      # Skip summary
```

#### Filtering

```bash
# Include specific patterns
gitingest -i "*.py" -i "*.md" .

# Exclude patterns
gitingest -e "*.log" -e "node_modules/*" .

# File size limit
gitingest --max-size 1048576 .  # 1MB limit
```

#### Private Repositories

```bash
# Using PAT token
gitingest --pat-token YOUR_TOKEN https://github.com/private/repo

# Using environment variable
export GITHUB_TOKEN=YOUR_TOKEN
gitingest https://github.com/private/repo
```

### Debugging Features

#### Dry Run Mode

```bash
# Preview what would be analyzed
gitingest --dry-run https://github.com/user/repo
```

**Output Example**:

```
🔍 DRY RUN MODE - Analyzing what would be processed...
Source: https://github.com/user/repo
Max file size: 10,485,760 bytes
Include patterns: None
Exclude patterns: Default patterns only
Output format: txt
Branch: Default
No files will be written or repositories cloned.
```

#### Print-Only Mode

```bash
# Output to console instead of file
gitingest --print-only .

# Combine with other options
gitingest --print-only --output-format json --include-pattern "*.py" .
```

#### Debug Mode

```bash
# Keep temporary directories for inspection
gitingest --keep-temp https://github.com/user/repo
```

**Output Example**:

```
🔧 DEBUG: Temporary directory preserved at: /tmp/gitingest_temp/abc123
```

## Data Models

### IngestionQuery

```python
class IngestionQuery(BaseModel):
    """Main query configuration model."""

    user_name: Optional[str] = None
    repo_name: Optional[str] = None
    local_path: Path
    url: Optional[str] = None
    slug: str
    id: str
    subpath: str = "/"
    type: Optional[str] = None
    branch: Optional[str] = None
    commit: Optional[str] = None
    max_file_size: int = Field(default=MAX_FILE_SIZE)
    ignore_patterns: Optional[Set[str]] = None
    include_patterns: Optional[Set[str]] = None
    include_summary: bool = True
    include_structure: bool = True
    include_content: bool = True
    output_format: str = "txt"  # Validated: "txt", "json", "markdown"
    pat_token: Optional[str] = None
```

### CloneConfig

```python
@dataclass
class CloneConfig:
    """Git repository cloning configuration."""

    url: str
    local_path: str
    commit: Optional[str] = None
    branch: Optional[str] = None
    subpath: str = "/"
    blob: bool = False
    pat_token: Optional[str] = None
```

## Examples

### Basic Python Usage

```python
from gitingest import ingest

# Analyze current directory
summary, tree, content = ingest(".")
print(f"Summary: {summary}")
print(f"Structure: {tree}")
print(f"Content length: {len(content)} characters")
```

### Advanced Python Usage

```python
from gitingest import ingest_async
import asyncio

async def analyze_repo():
    # Analyze with custom options
    summary, tree, content = await ingest_async(
        source="https://github.com/user/repo",
        include_patterns={"*.py", "*.md"},
        exclude_patterns={"test_*", "*.pyc"},
        output_format="json",
        max_file_size=2 * 1024 * 1024,  # 2MB
        branch="develop"
    )

    # Parse JSON output
    import json
    data = json.loads(summary)
    print(f"Files analyzed: {data.get('files_count', 'N/A')}")

# Run async function
asyncio.run(analyze_repo())
```

### Jupyter Notebook Usage

```python
from gitingest import ingest_async

# Direct await in Jupyter
summary, tree, content = await ingest_async(
    source="https://github.com/user/repo",
    output_format="markdown"
)

# Display results
from IPython.display import Markdown, display
display(Markdown(summary))
```

### CLI Examples

```bash
# Complete analysis with all options
gitingest \
  --output-format markdown \
  --include-pattern "*.py" \
  --include-pattern "*.md" \
  --exclude-pattern "test_*" \
  --max-size 2097152 \
  --output detailed-analysis.md \
  --branch develop \
  --pat-token $GITHUB_TOKEN \
  https://github.com/user/repo

# Quick preview of Python files only
gitingest --dry-run --include-pattern "*.py" .

# Console output for piping
gitingest --print-only --no-include-summary . | grep "def "
```

## Error Handling

### Common Errors

#### Invalid Output Format

```python
# This will raise ValueError
query = IngestionQuery(
    local_path=Path("."),
    slug="test",
    id="123",
    output_format="invalid"  # ❌ Not in ["txt", "json", "markdown"]
)
```

#### Repository Not Found

```python
try:
    result = await ingest_async("https://github.com/nonexistent/repo")
except ValueError as e:
    print(f"Repository error: {e}")
```

#### File Size Limits

```python
# Files larger than max_file_size are automatically skipped
result = await ingest_async(".", max_file_size=1024)  # 1KB limit
```

### Best Practices

#### Error Handling

```python
import asyncio
from gitingest import ingest_async

async def safe_analysis(source: str):
    try:
        summary, tree, content = await ingest_async(source)
        return {"success": True, "data": (summary, tree, content)}
    except ValueError as e:
        return {"success": False, "error": f"Validation error: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}"}

# Usage
result = asyncio.run(safe_analysis("https://github.com/user/repo"))
if result["success"]:
    summary, tree, content = result["data"]
else:
    print(f"Analysis failed: {result['error']}")
```

#### Resource Management

```python
# For large repositories, consider using keep_temp=False (default)
# and appropriate file size limits
result = await ingest_async(
    source="https://github.com/large/repo",
    max_file_size=5 * 1024 * 1024,  # 5MB limit
    keep_temp=False  # Clean up automatically
)
```

#### Security Considerations

```python
import os

# Secure PAT token handling
pat_token = os.getenv("GITHUB_TOKEN")
if not pat_token:
    print("Warning: No GitHub token found, private repos will be inaccessible")

result = await ingest_async(
    source="https://github.com/private/repo",
    pat_token=pat_token
)
```

## Performance Tips

1. **Use appropriate file size limits** to avoid processing large binary files
2. **Use include patterns** to focus on relevant files only
3. **Use exclude patterns** to skip unnecessary directories (logs, caches, etc.)
4. **Consider async interface** for better performance with I/O operations
5. **Use dry-run mode** to preview before processing large repositories

## Support

For additional help:

- Check the [README.md](README.md) for usage examples
- Review the [CHANGELOG.md](CHANGELOG.md) for recent updates
- Open an issue on GitHub for bug reports or feature requests
- Join the Discord community for real-time support

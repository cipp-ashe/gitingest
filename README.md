# Gitingest

[![Image](./docs/frontpage.png "Gitingest main page")](https://gitingest.com)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/cyclotruc/gitingest/blob/main/LICENSE)
[![PyPI version](https://badge.fury.io/py/gitingest.svg)](https://badge.fury.io/py/gitingest)
[![GitHub stars](https://img.shields.io/github/stars/cyclotruc/gitingest?style=social.svg)](https://github.com/cyclotruc/gitingest)
[![Downloads](https://pepy.tech/badge/gitingest)](https://pepy.tech/project/gitingest)

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.com/invite/zerRaGK9EC)](https://discord.com/invite/zerRaGK9EC)

Turn any Git repository into a prompt-friendly text ingest for LLMs.

You can also replace `hub` with `ingest` in any GitHub URL to access the corresponding digest.

[gitingest.com](https://gitingest.com) · [Chrome Extension](https://chromewebstore.google.com/detail/adfjahbijlkjfoicpjkhjicpjpjfaood) · [Firefox Add-on](https://addons.mozilla.org/firefox/addon/gitingest)

## 🚀 Features

- **Easy code context**: Get a text digest from a Git repository URL or a directory
- **Smart Formatting**: Optimized output format for LLM prompts
- **Statistics about**:
  - File and directory structure
  - Size of the extract
  - Token count
- **CLI tool**: Run it as a shell command
- **Python package**: Import it in your code

## 📚 Requirements

- Python 3.7+

### 📦 Installation

Gitingest is available on [PyPI](https://pypi.org/project/gitingest/).
You can install it using `pip`:

```bash
pip install gitingest
```

However, it might be a good idea to use `pipx` to install it.
You can install `pipx` using your preferred package manager.

```bash
brew install pipx
apt install pipx
scoop install pipx
...
```

If you are using pipx for the first time, run:

```bash
pipx ensurepath
```

```bash
# install gitingest
pipx install gitingest
```

## 🧩 Browser Extension Usage

<!-- markdownlint-disable MD033 -->

<a href="https://chromewebstore.google.com/detail/adfjahbijlkjfoicpjkhjicpjpjfaood" target="_blank" title="Get Gitingest Extension from Chrome Web Store"><img height="48" src="https://github.com/user-attachments/assets/20a6e44b-fd46-4e6c-8ea6-aad436035753" alt="Available in the Chrome Web Store" /></a>
<a href="https://addons.mozilla.org/firefox/addon/gitingest" target="_blank" title="Get Gitingest Extension from Firefox Add-ons"><img height="48" src="https://github.com/user-attachments/assets/c0e99e6b-97cf-4af2-9737-099db7d3538b" alt="Get The Add-on for Firefox" /></a>
<a href="https://microsoftedge.microsoft.com/addons/detail/nfobhllgcekbmpifkjlopfdfdmljmipf" target="_blank" title="Get Gitingest Extension from Microsoft Edge Add-ons"><img height="48" src="https://github.com/user-attachments/assets/204157eb-4cae-4c0e-b2cb-db514419fd9e" alt="Get from the Edge Add-ons" /></a>

<!-- markdownlint-enable MD033 -->

The extension is open source at [lcandy2/gitingest-extension](https://github.com/lcandy2/gitingest-extension).

Issues and feature requests are welcome to the repo.

## 💡 Command line usage

The `gitingest` command line tool allows you to analyze codebases and create a text dump of their contents.

### Basic Usage

```bash
# Basic usage - analyze current directory
gitingest .

# Analyze specific directory
gitingest /path/to/directory

# Analyze from GitHub URL
gitingest https://github.com/cyclotruc/gitingest

# Analyze specific branch
gitingest -b main https://github.com/cyclotruc/gitingest
```

### Output Formats

Gitingest supports multiple output formats optimized for different use cases:

```bash
# Text format (default) - optimized for LLM prompts
gitingest --output-format txt .

# JSON format - structured data for programmatic use
gitingest --output-format json .

# Markdown format - human-readable with proper formatting
gitingest --output-format markdown .
```

### Advanced Features

#### 🔍 Dry Run Mode

Preview what would be processed without actually creating files or cloning repositories:

```bash
# See what would be analyzed without processing
gitingest --dry-run https://github.com/user/repo
```

#### 📄 Print-Only Mode

Output directly to console instead of writing files:

```bash
# Print output to console
gitingest --print-only .

# Combine with other options
gitingest --print-only --output-format json --include-pattern "*.py" .
```

#### 🛠️ Debug Mode

Keep temporary directories for debugging (useful for development):

```bash
# Keep temporary files for inspection
gitingest --keep-temp https://github.com/user/repo
```

### Filtering Options

Control what gets included in your analysis:

```bash
# Include only specific file patterns
gitingest --include-pattern "*.py" --include-pattern "*.md" .

# Exclude specific patterns
gitingest --exclude-pattern "*.log" --exclude-pattern "node_modules/*" .

# Control output sections
gitingest --no-include-content .  # Skip file contents
gitingest --no-include-structure .  # Skip directory tree
gitingest --no-include-summary .  # Skip summary
```

### File Size and Output Control

```bash
# Set maximum file size (in bytes)
gitingest --max-size 1048576 .  # 1MB limit

# Custom output file
gitingest --output my-analysis.txt .
```

### 🔐 GitHub Authentication & Repository Access

Gitingest supports both public and private GitHub repositories with automatic authentication detection.

#### Capability Comparison

| Feature                  | Unauthenticated  | Authenticated       |
| ------------------------ | ---------------- | ------------------- |
| **Public Repositories**  | ✅ Full access   | ✅ Full access      |
| **Private Repositories** | ❌ Access denied | ✅ Full access      |
| **Rate Limiting**        | 60 requests/hour | 5,000 requests/hour |
| **Error Messages**       | Basic            | Enhanced details    |

#### Quick Setup

**Option 1: Environment Variable (Recommended)**

```bash
# Set once in your shell profile (.bashrc, .zshrc, etc.)
export GITHUB_TOKEN="your_github_token_here"

# Use normally - token is automatically detected
gitingest https://github.com/private/repo
gitingest https://github.com/organization/private-repo
```

**Option 2: Command Line Flag**

```bash
# Pass token directly (less secure - visible in command history)
gitingest --pat-token your_github_token https://github.com/private/repo
```

#### Creating a GitHub Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Gitingest CLI Access")
4. Select scopes:
   - ✅ `repo` - Full control of private repositories
   - ✅ `read:org` - Read org membership (optional, for organization repos)
5. Set appropriate expiration (30-90 days recommended)
6. Generate and copy the token immediately

#### Authentication Examples

```bash
# Public repository (works without authentication)
gitingest https://github.com/octocat/Hello-World

# Private repository (requires authentication)
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
gitingest https://github.com/myorg/private-repo

# Organization repository with specific branch
gitingest --branch develop https://github.com/myorg/private-project

# High-volume usage (benefits from higher rate limits)
gitingest https://github.com/large/public-repo  # 83x more requests with auth
```

#### Security Best Practices

✅ **Do:**

- Use environment variables for token storage
- Set appropriate token expiration (30-90 days)
- Use minimal required permissions
- Rotate tokens regularly

❌ **Don't:**

- Commit tokens to version control
- Share tokens in chat/email
- Use tokens in URLs
- Log tokens in application output

For comprehensive authentication documentation, see [AUTHENTICATION.md](./AUTHENTICATION.md).

### Complete Example

```bash
# Comprehensive analysis with all options
gitingest \
  --output-format markdown \
  --include-pattern "*.py" \
  --include-pattern "*.md" \
  --exclude-pattern "test_*" \
  --max-size 2097152 \
  --output detailed-analysis.md \
  --branch develop \
  https://github.com/user/repo
```

### Getting Help

```bash
# See all available options
gitingest --help
```

This will write the digest in a text file (default `digest.txt`) in your current working directory unless using `--print-only` mode.

## 🐍 Python package usage

```python
# Synchronous usage
from gitingest import ingest

summary, tree, content = ingest("path/to/directory")

# or from URL
summary, tree, content = ingest("https://github.com/cyclotruc/gitingest")
```

By default, this won't write a file but can be enabled with the `output` argument.

```python
# Asynchronous usage
from gitingest import ingest_async
import asyncio

result = asyncio.run(ingest_async("path/to/directory"))
```

### Authentication in Python

```python
import os
from gitingest import ingest_async

# Automatic token detection from environment
summary, tree, content = await ingest_async("https://github.com/private/repo")

# Or pass token directly
summary, tree, content = await ingest_async(
    source="https://github.com/private/repo",
    pat_token=os.getenv("GITHUB_TOKEN")
)
```

### Jupyter notebook usage

```python
from gitingest import ingest_async

# Use await directly in Jupyter
summary, tree, content = await ingest_async("path/to/directory")

```

This is because Jupyter notebooks are asynchronous by default.

## 🐳 Self-host

1. Build the image:

   ```bash
   docker build -t gitingest .
   ```

2. Run the container:

   ```bash
   docker run -d --name gitingest -p 8000:8000 gitingest
   ```

The application will be available at `http://localhost:8000`.

If you are hosting it on a domain, you can specify the allowed hostnames via env variable `ALLOWED_HOSTS`.

```bash
# Default: "gitingest.com, *.gitingest.com, localhost, 127.0.0.1".
ALLOWED_HOSTS="example.com, localhost, 127.0.0.1"
```

## 🤝 Contributing

### Non-technical ways to contribute

- **Create an Issue**: If you find a bug or have an idea for a new feature, please [create an issue](https://github.com/cyclotruc/gitingest/issues/new) on GitHub. This will help us track and prioritize your request.
- **Spread the Word**: If you like Gitingest, please share it with your friends, colleagues, and on social media. This will help us grow the community and make Gitingest even better.
- **Use Gitingest**: The best feedback comes from real-world usage! If you encounter any issues or have ideas for improvement, please let us know by [creating an issue](https://github.com/cyclotruc/gitingest/issues/new) on GitHub or by reaching out to us on [Discord](https://discord.com/invite/zerRaGK9EC).

### Technical ways to contribute

Gitingest aims to be friendly for first time contributors, with a simple Python and HTML codebase. If you need any help while working with the code, reach out to us on [Discord](https://discord.com/invite/zerRaGK9EC). For detailed instructions on how to make a pull request, see [CONTRIBUTING.md](./CONTRIBUTING.md).

## 🛠️ Stack

- [Tailwind CSS](https://tailwindcss.com) - Frontend
- [FastAPI](https://github.com/fastapi/fastapi) - Backend framework
- [Jinja2](https://jinja.palletsprojects.com) - HTML templating
- [tiktoken](https://github.com/openai/tiktoken) - Token estimation
- [posthog](https://github.com/PostHog/posthog) - Amazing analytics

### Looking for a JavaScript/FileSystemNode package?

Check out the NPM alternative 📦 Repomix: <https://github.com/yamadashy/repomix>

## 🚀 Project Growth

[![Star History Chart](https://api.star-history.com/svg?repos=cyclotruc/gitingest&type=Date)](https://star-history.com/#cyclotruc/gitingest&Date)

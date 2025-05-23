# GitHub Authentication Guide

This guide explains how to use gitingest with GitHub repositories, covering both public (unauthenticated) and private (authenticated) repository access.

## Table of Contents

- [Overview](#overview)
- [Unauthenticated vs Authenticated Access](#unauthenticated-vs-authenticated-access)
- [Setting Up Personal Access Tokens](#setting-up-personal-access-tokens)
- [Using Authentication](#using-authentication)
- [Security Best Practices](#security-best-practices)
- [Rate Limiting](#rate-limiting)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Overview

Gitingest supports two modes of GitHub repository access:

1. **Unauthenticated Access** (default): Works with public repositories only
2. **Authenticated Access**: Works with both public and private repositories using GitHub Personal Access Tokens (PAT)

The system automatically detects whether authentication is available and uses the appropriate method.

## Unauthenticated vs Authenticated Access

### Capability Comparison

| Feature                       | Unauthenticated         | Authenticated                      |
| ----------------------------- | ----------------------- | ---------------------------------- |
| **Public Repositories**       | ✅ Full access          | ✅ Full access                     |
| **Private Repositories**      | ❌ Access denied        | ✅ Full access (if permitted)      |
| **Organization Repositories** | ✅ Public only          | ✅ Public + private (if permitted) |
| **Rate Limiting**             | 60 requests/hour per IP | 5,000 requests/hour per token      |
| **Error Messages**            | Basic                   | Enhanced with detailed information |
| **Repository Validation**     | Basic curl check        | Full GitHub API validation         |
| **User Repository Listing**   | ❌ Not available        | ✅ Available via API               |

### When You Need Authentication

You **must** use authentication for:

- Private repositories
- Private repositories in organizations
- High-volume usage (>60 requests/hour)
- Better error reporting and debugging

You **can** use authentication for:

- Public repositories (for better rate limits and error messages)
- Any scenario where you want enhanced functionality

## Setting Up Personal Access Tokens

### Step 1: Create a Personal Access Token

1. **Go to GitHub Settings**:

   - Visit [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
   - Or navigate: GitHub Profile → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token**:

   - Click "Generate new token" → "Generate new token (classic)"
   - Give your token a descriptive name (e.g., "Gitingest CLI Access")

3. **Set Expiration**:

   - Choose an appropriate expiration (30 days, 90 days, or custom)
   - For security, avoid "No expiration" unless absolutely necessary

4. **Select Scopes**:
   For gitingest, you need these minimum permissions:

   - ✅ `repo` - Full control of private repositories
     - This includes `repo:status`, `repo_deployment`, `public_repo`
   - ✅ `read:org` - Read org and team membership (optional, for organization repos)

   **Note**: The `repo` scope provides access to both public and private repositories. If you only need public repository access with better rate limits, you can use just `public_repo`, but `repo` is recommended for full functionality.

5. **Generate and Copy Token**:
   - Click "Generate token"
   - **Important**: Copy the token immediately - you won't be able to see it again!

### Step 2: Secure Token Storage

#### Option 1: Environment Variable (Recommended)

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export GITHUB_TOKEN="your_token_here"

# Or set for current session
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

#### Option 2: Direct CLI Usage (Less Secure)

```bash
# Use --pat-token flag (token visible in command history)
gitingest --pat-token "your_token_here" https://github.com/private/repo
```

## Using Authentication

### CLI Usage

#### With Environment Variable

```bash
# Set token once
export GITHUB_TOKEN="your_token_here"

# Use normally - token is automatically detected
gitingest https://github.com/private/repo
gitingest https://github.com/organization/private-repo
```

#### With CLI Flag

```bash
# Pass token directly (less secure)
gitingest --pat-token "your_token_here" https://github.com/private/repo
```

### Python API Usage

#### With Environment Variable

```python
import os
from gitingest import ingest_async

# Token automatically detected from environment
summary, tree, content = await ingest_async("https://github.com/private/repo")
```

#### With Direct Token

```python
from gitingest import ingest_async

# Pass token directly
summary, tree, content = await ingest_async(
    source="https://github.com/private/repo",
    pat_token="your_token_here"
)
```

#### Secure Token Handling

```python
import os
from gitingest import ingest_async

# Secure token handling
def get_github_token():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GitHub token not found. Set GITHUB_TOKEN environment variable.")
    return token

# Usage
try:
    token = get_github_token()
    summary, tree, content = await ingest_async(
        source="https://github.com/private/repo",
        pat_token=token
    )
except ValueError as e:
    print(f"Authentication error: {e}")
```

## Security Best Practices

### ✅ Do This

1. **Use Environment Variables**:

   ```bash
   export GITHUB_TOKEN="your_token_here"
   ```

2. **Set Appropriate Token Expiration**:

   - Use 30-90 day expiration for regular use
   - Rotate tokens regularly

3. **Use Minimal Permissions**:

   - Only grant necessary scopes
   - Use `public_repo` if you don't need private repository access

4. **Store Tokens Securely**:

   - Use environment variables
   - Use secure credential managers
   - Never commit tokens to version control

5. **Monitor Token Usage**:
   - Check GitHub's token usage in settings
   - Revoke unused or compromised tokens

### ❌ Don't Do This

1. **Never Commit Tokens**:

   ```bash
   # DON'T DO THIS
   git add .env
   git commit -m "Added GitHub token"  # ❌ Token now in git history
   ```

2. **Don't Log Tokens**:

   ```python
   # DON'T DO THIS
   print(f"Using token: {pat_token}")  # ❌ Token in logs
   ```

3. **Don't Use Tokens in URLs**:

   ```bash
   # DON'T DO THIS
   gitingest https://token:your_token@github.com/user/repo  # ❌ Visible in history
   ```

4. **Don't Share Tokens**:
   - Never share tokens in chat, email, or documentation
   - Each user should have their own token

## Rate Limiting

### Understanding GitHub Rate Limits

#### Unauthenticated Requests

- **Limit**: 60 requests per hour per IP address
- **Scope**: Shared across all applications from your IP
- **Reset**: Every hour at the top of the hour

#### Authenticated Requests

- **Limit**: 5,000 requests per hour per token
- **Scope**: Per token (not shared)
- **Reset**: Every hour from first request

### Rate Limit Headers

GitHub includes rate limit information in response headers:

- `X-RateLimit-Limit`: Maximum requests per hour
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

### Best Practices for Rate Limiting

1. **Use Authentication for High Volume**:

   ```bash
   # 83x more requests with authentication
   export GITHUB_TOKEN="your_token_here"
   ```

2. **Monitor Rate Limit Usage**:

   ```python
   # Check rate limit status
   curl -H "Authorization: token your_token_here" \
        https://api.github.com/rate_limit
   ```

3. **Handle Rate Limit Errors**:
   ```python
   try:
       result = await ingest_async("https://github.com/user/repo")
   except RuntimeError as e:
       if "rate limit" in str(e).lower():
           print("Rate limit exceeded. Try again later or use authentication.")
   ```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Repository not found or access denied"

**Possible Causes**:

- Repository is private and you're not authenticated
- Repository doesn't exist
- Token doesn't have required permissions
- Repository is in an organization with restricted access

**Solutions**:

```bash
# Check if repository exists publicly
curl -I https://github.com/user/repo

# Try with authentication
export GITHUB_TOKEN="your_token_here"
gitingest https://github.com/user/repo

# Verify token permissions
curl -H "Authorization: token your_token_here" \
     https://api.github.com/repos/user/repo
```

#### 2. "GitHub API request failed: 401"

**Cause**: Invalid or expired token

**Solutions**:

```bash
# Test token validity
curl -H "Authorization: token your_token_here" \
     https://api.github.com/user

# Check token scopes
curl -H "Authorization: token your_token_here" \
     -I https://api.github.com/user
# Look for X-OAuth-Scopes header
```

#### 3. "GitHub API request failed: 403"

**Possible Causes**:

- Rate limit exceeded
- Token lacks required permissions
- Repository access restricted

**Solutions**:

```bash
# Check rate limit status
curl -H "Authorization: token your_token_here" \
     https://api.github.com/rate_limit

# Wait for rate limit reset or use authentication
# Check token permissions in GitHub settings
```

#### 4. Token Not Being Detected

**Check Environment Variable**:

```bash
# Verify token is set
echo $GITHUB_TOKEN

# Check if variable is exported
env | grep GITHUB_TOKEN
```

**Restart Shell**:

```bash
# After adding to .bashrc/.zshrc
source ~/.bashrc  # or ~/.zshrc
```

### Debugging Steps

1. **Verify Token**:

   ```bash
   curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
   ```

2. **Check Repository Access**:

   ```bash
   curl -H "Authorization: token $GITHUB_TOKEN" \
        https://api.github.com/repos/owner/repo
   ```

3. **Test with Public Repository**:

   ```bash
   gitingest https://github.com/octocat/Hello-World
   ```

4. **Enable Verbose Output** (if available):
   ```bash
   gitingest --verbose https://github.com/user/repo
   ```

## Examples

### Basic Usage Examples

#### Public Repository (No Authentication)

```bash
# Works without authentication
gitingest https://github.com/octocat/Hello-World
```

#### Private Repository (Requires Authentication)

```bash
# Set up authentication
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Access private repository
gitingest https://github.com/myorg/private-repo
```

### Advanced Usage Examples

#### Organization Repository with Specific Branch

```bash
export GITHUB_TOKEN="your_token_here"
gitingest --branch develop https://github.com/myorg/private-project
```

#### Multiple Repositories with Different Access Levels

```bash
# Public repository (works without auth)
gitingest https://github.com/public/repo

# Private repository (requires auth)
export GITHUB_TOKEN="your_token_here"
gitingest https://github.com/private/repo
```

#### Python API with Error Handling

```python
import os
from gitingest import ingest_async

async def analyze_repository(repo_url: str):
    """Analyze repository with proper authentication handling."""

    # Get token from environment
    token = os.getenv("GITHUB_TOKEN")

    try:
        if token:
            print(f"Using authenticated access for {repo_url}")
            result = await ingest_async(repo_url, pat_token=token)
        else:
            print(f"Using unauthenticated access for {repo_url}")
            print("Note: Private repositories will not be accessible")
            result = await ingest_async(repo_url)

        summary, tree, content = result
        print(f"Analysis complete. Summary: {summary[:100]}...")
        return result

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg or "access denied" in error_msg:
            print("Repository not accessible. Possible reasons:")
            print("- Repository is private and requires authentication")
            print("- Repository doesn't exist")
            print("- Insufficient permissions")
            if not token:
                print("Try setting GITHUB_TOKEN environment variable")
        elif "rate limit" in error_msg:
            print("Rate limit exceeded. Try again later or use authentication")
        else:
            print(f"Unexpected error: {e}")
        raise

# Usage
import asyncio
asyncio.run(analyze_repository("https://github.com/user/repo"))
```

### Batch Processing Example

```python
import os
import asyncio
from gitingest import ingest_async

async def analyze_multiple_repos(repo_urls: list):
    """Analyze multiple repositories efficiently."""

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Warning: No GitHub token found. Private repos will be skipped.")

    results = []
    for url in repo_urls:
        try:
            print(f"Analyzing {url}...")
            result = await ingest_async(url, pat_token=token)
            results.append({"url": url, "success": True, "data": result})
        except Exception as e:
            print(f"Failed to analyze {url}: {e}")
            results.append({"url": url, "success": False, "error": str(e)})

    return results

# Usage
repos = [
    "https://github.com/public/repo1",
    "https://github.com/private/repo2",
    "https://github.com/org/repo3"
]

results = asyncio.run(analyze_multiple_repos(repos))
for result in results:
    if result["success"]:
        print(f"✅ {result['url']}: Success")
    else:
        print(f"❌ {result['url']}: {result['error']}")
```

## Support

For additional help with authentication:

- **GitHub Token Issues**: Check [GitHub's PAT documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- **Gitingest Issues**: Open an issue on the [Gitingest GitHub repository](https://github.com/cyclotruc/gitingest/issues)
- **Community Support**: Join the [Discord community](https://discord.com/invite/zerRaGK9EC)

---

**Security Reminder**: Always keep your GitHub tokens secure and never share them publicly. Rotate tokens regularly and revoke unused tokens.

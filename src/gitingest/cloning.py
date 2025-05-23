"""This module contains functions for cloning a Git repository to a local path."""

import os
import shlex
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, urlunparse

from gitingest.schemas import CloneConfig
from gitingest.utils.git_utils import check_repo_exists, ensure_git_installed, run_command
from gitingest.utils.timeout_wrapper import async_timeout

TIMEOUT: int = 60


def _inject_token_into_url(url: str, token: str) -> str:
    """
    Inject a GitHub Personal Access Token into a repository URL for authentication.
    
    Parameters
    ----------
    url : str
        The original repository URL (e.g., https://github.com/owner/repo.git)
    token : str
        The GitHub Personal Access Token
        
    Returns
    -------
    str
        The authenticated URL (e.g., https://token@github.com/owner/repo.git)
    """
    parsed = urlparse(url)
    
    # Handle GitHub URLs specifically
    if 'github.com' in parsed.netloc:
        # Construct authenticated URL: https://token@github.com/owner/repo.git
        authenticated_netloc = f"{token}@{parsed.netloc}"
        authenticated_url = urlunparse((
            parsed.scheme,
            authenticated_netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        return authenticated_url
    
    # For non-GitHub URLs, return original (could be extended for other Git hosts)
    return url


@async_timeout(TIMEOUT)
async def clone_repo(config: CloneConfig) -> None:
    """
    Clone a repository to a local path based on the provided configuration.

    This function handles the process of cloning a Git repository to the local file system.
    It can clone a specific branch or commit if provided, and it raises exceptions if
    any errors occur during the cloning process.

    Parameters
    ----------
    config : CloneConfig
        The configuration for cloning the repository.

    Raises
    ------
    ValueError
        If the repository is not found or if the provided URL is invalid.
    OSError
        If an error occurs while creating the parent directory for the repository.
    """
    # Extract and validate query parameters
    url: str = config.url
    local_path: str = config.local_path
    commit: Optional[str] = config.commit
    branch: Optional[str] = config.branch
    partial_clone: bool = config.subpath != "/"

    # Create parent directory if it doesn't exist
    parent_dir = Path(local_path).parent
    try:
        os.makedirs(parent_dir, exist_ok=True)
    except OSError as exc:
        raise OSError(f"Failed to create parent directory {parent_dir}: {exc}") from exc

    # Check if the repository exists
    if config.pat_token:
        from gitingest.utils.github_api import check_repo_exists_authenticated
        # Extract owner and repo name from URL
        try:
            # Assuming URL format: https://github.com/owner/repo.git
            parts = url.rstrip(".git").split("/")
            owner = parts[-2]
            repo = parts[-1]
        except Exception:
            raise ValueError("Invalid repository URL format for authenticated check")
        
        try:
            exists = await check_repo_exists_authenticated(owner, repo, config.pat_token)
            if not exists:
                raise ValueError("Repository not found or access denied")
        except Exception as e:
            # If GitHub API check fails (e.g., SSL issues), proceed with clone attempt
            # The git clone will fail with a proper error if the repo doesn't exist
            print(f"Warning: GitHub API check failed ({e}), proceeding with clone attempt...")
    else:
        from gitingest.utils.git_utils import check_repo_exists
        exists = await check_repo_exists(url)
        if not exists:
            raise ValueError("Repository not found or access denied")

    clone_cmd = ["git", "clone", "--single-branch"]
    # TODO re-enable --recurse-submodules

    if partial_clone:
        clone_cmd += ["--filter=blob:none", "--sparse"]

    if not commit:
        clone_cmd += ["--depth=1"]
        if branch and branch.lower() not in ("main", "master"):
            clone_cmd += ["--branch", branch]

    # Use authenticated URL if token is provided
    if config.pat_token:
        authenticated_url = _inject_token_into_url(url, config.pat_token)
        clone_cmd += [authenticated_url, local_path]
    else:
        clone_cmd += [url, local_path]

    # Clone the repository
    await ensure_git_installed()
    await run_command(*clone_cmd)

    if commit or partial_clone:
        checkout_cmd = ["git", "-C", local_path]

        if partial_clone:
            subpath = config.subpath.lstrip("/")
            if config.blob:
                # When ingesting from a file url (blob/branch/path/file.txt), we need to remove the file name.
                subpath = str(Path(subpath).parent.as_posix())

            checkout_cmd += ["sparse-checkout", "set", subpath]

        if commit:
            checkout_cmd += ["checkout", commit]

        # Check out the specific commit and/or subpath
        await run_command(*checkout_cmd)

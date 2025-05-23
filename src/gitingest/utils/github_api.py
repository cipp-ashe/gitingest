import aiohttp
import ssl
from typing import List, Dict, Optional


def _create_ssl_context() -> ssl.SSLContext:
    """
    Create an SSL context that handles certificate verification issues on macOS.
    
    Returns
    -------
    ssl.SSLContext
        SSL context with appropriate certificate handling
    """
    try:
        # Try to create a default SSL context
        ssl_context = ssl.create_default_context()
        return ssl_context
    except Exception:
        # If that fails, create a more permissive context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context


async def fetch_github_user_repos(pat_token: str) -> List[Dict[str, str]]:
    """
    Fetch the authenticated user's GitHub repositories using the provided Personal Access Token (PAT).

    Parameters
    ----------
    pat_token : str
        GitHub Personal Access Token for authentication.

    Returns
    -------
    List[Dict[str, str]]
        A list of repositories with 'name' and 'full_name' keys.

    Raises
    ------
    RuntimeError
        If the API request fails or returns an error.
    """
    headers = {
        "Authorization": f"token {pat_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    repos = []
    url = "https://api.github.com/user/repos?per_page=100"
    ssl_context = _create_ssl_context()
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        while url:
            async with session.get(url) as response:
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(f"GitHub API request failed: {response.status} {text}")
                data = await response.json()
                for repo in data:
                    repos.append({"name": repo["name"], "full_name": repo["full_name"]})
                # Check for pagination
                link = response.headers.get("Link")
                if link and 'rel="next"' in link:
                    # Extract next URL from Link header
                    parts = link.split(",")
                    next_url = None
                    for part in parts:
                        if 'rel="next"' in part:
                            next_url = part[part.find("<")+1:part.find(">")]
                            break
                    url = next_url
                else:
                    url = None
    return repos
async def check_repo_exists_authenticated(owner: str, repo: str, pat_token: str) -> bool:
    """
    Check if a GitHub repository exists using the GitHub API with authentication.

    Parameters
    ----------
    owner : str
        The owner of the repository.
    repo : str
        The repository name.
    pat_token : str
        GitHub Personal Access Token for authentication.

    Returns
    -------
    bool
        True if the repository exists, False otherwise.

    Raises
    ------
    RuntimeError
        If the API request fails with an unexpected status code.
    """
    import aiohttp

    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Authorization": f"token {pat_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    ssl_context = _create_ssl_context()
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        async with session.get(url) as response:
            if response.status == 200:
                return True
            elif response.status == 404:
                return False
            else:
                text = await response.text()
                raise RuntimeError(f"GitHub API request failed: {response.status} {text}")

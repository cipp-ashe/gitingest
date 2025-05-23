"""Process a query by parsing input, cloning a repository, and generating a summary."""

from functools import partial
from typing import Optional
import re

from fastapi import Request
from starlette.templating import _TemplateResponse

from gitingest.cloning import clone_repo
from gitingest.ingestion import ingest_query
from gitingest.query_parsing import IngestionQuery, parse_query
from server.server_config import EXAMPLE_REPOS, MAX_DISPLAY_SIZE, templates
from server.server_utils import Colors, log_slider_to_size


def _detect_saml_sso_error(error_message: str) -> tuple[bool, str, str]:
    """
    Detect SAML SSO authentication errors and extract relevant information.
    
    Parameters
    ----------
    error_message : str
        The error message from git clone operation
        
    Returns
    -------
    tuple[bool, str, str]
        (is_saml_error, organization_name, sso_url)
    """
    # Pattern to match SAML SSO error messages
    saml_pattern = r"The '([^']+)' organization has enabled or enforced SAML SSO"
    url_pattern = r"visit (https://github\.com/enterprises/[^/]+/sso\?[^\s]+)"
    
    saml_match = re.search(saml_pattern, error_message)
    url_match = re.search(url_pattern, error_message)
    
    if saml_match and url_match:
        org_name = saml_match.group(1)
        sso_url = url_match.group(1)
        return True, org_name, sso_url
    
    return False, "", ""


def _create_saml_sso_error_message(org_name: str, sso_url: str) -> str:
    """
    Create a user-friendly error message for SAML SSO authentication.
    
    Parameters
    ----------
    org_name : str
        The organization name requiring SAML SSO
    sso_url : str
        The SSO authentication URL
        
    Returns
    -------
    str
        Formatted error message with HTML for clickable link
    """
    return f"""🔐 SAML SSO Authentication Required

The '{org_name}' organization requires SAML Single Sign-On authentication.

<strong>Steps to access this repository:</strong>

1. <a href="{sso_url}" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">Click here to authenticate with {org_name} SSO</a>
2. Complete the authentication process in the new browser window
3. Return here and try your request again

<div class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
<strong>Note:</strong> Your GitHub token is valid, but the organization requires additional SAML authentication. This is a security feature that ensures only authorized users can access organization resources.
</div>

After completing SSO authentication, you can retry your request with the same GitHub token."""


async def process_query(
    request: Request,
    input_text: str,
    slider_position: int,
    pattern_type: str = "exclude",
    pattern: str = "",
    github_token: Optional[str] = None,
    is_index: bool = False,
) -> _TemplateResponse:
    """
    Process a query by parsing input, cloning a repository, and generating a summary.

    Handle user input, process Git repository data, and prepare
    a response for rendering a template with the processed results or an error message.

    Parameters
    ----------
    request : Request
        The HTTP request object.
    input_text : str
        Input text provided by the user, typically a Git repository URL or slug.
    slider_position : int
        Position of the slider, representing the maximum file size in the query.
    pattern_type : str
        Type of pattern to use, either "include" or "exclude" (default is "exclude").
    pattern : str
        Pattern to include or exclude in the query, depending on the pattern type.
    github_token : Optional[str]
        GitHub Personal Access Token for private repository access, by default None.
    is_index : bool
        Flag indicating whether the request is for the index page (default is False).

    Returns
    -------
    _TemplateResponse
        Rendered template response containing the processed results or an error message.

    Raises
    ------
    ValueError
        If an invalid pattern type is provided.
    """
    if pattern_type == "include":
        include_patterns = pattern
        exclude_patterns = None
    elif pattern_type == "exclude":
        exclude_patterns = pattern
        include_patterns = None
    else:
        raise ValueError(f"Invalid pattern type: {pattern_type}")

    template = "index.jinja" if is_index else "git.jinja"
    template_response = partial(templates.TemplateResponse, name=template)
    max_file_size = log_slider_to_size(slider_position)

    # Clean up empty token strings
    if github_token == "":
        github_token = None

    context = {
        "request": request,
        "repo_url": input_text,
        "examples": EXAMPLE_REPOS if is_index else [],
        "default_file_size": slider_position,
        "pattern_type": pattern_type,
        "pattern": pattern,
        "github_token": github_token,
    }

    try:
        query: IngestionQuery = await parse_query(
            source=input_text,
            max_file_size=max_file_size,
            from_web=True,
            include_patterns=include_patterns,
            ignore_patterns=exclude_patterns,
            pat_token=github_token,
        )
        if not query.url:
            raise ValueError("The 'url' parameter is required.")

        clone_config = query.extract_clone_config()
        await clone_repo(clone_config)
        summary, tree, content = ingest_query(query)
        with open(f"{clone_config.local_path}.txt", "w", encoding="utf-8") as f:
            f.write(tree + "\n" + content)
    except Exception as exc:
        # hack to print error message when query is not defined
        if "query" in locals() and query is not None and isinstance(query, dict):
            _print_error(query["url"], exc, max_file_size, pattern_type, pattern)
        else:
            print(f"{Colors.BROWN}WARN{Colors.END}: {Colors.RED}<-  {Colors.END}", end="")
            print(f"{Colors.RED}{exc}{Colors.END}")

        error_str = str(exc)
        
        # Check for SAML SSO error first
        is_saml_error, org_name, sso_url = _detect_saml_sso_error(error_str)
        if is_saml_error:
            context["error_message"] = _create_saml_sso_error_message(org_name, sso_url)
        elif "405" in error_str:
            context["error_message"] = (
                "Repository not found. Please check the URL and ensure you have access. "
                "For private repositories, provide a GitHub Personal Access Token."
            )
        elif "401" in error_str or "403" in error_str:
            context["error_message"] = (
                "Authentication failed. Please check your GitHub Personal Access Token "
                "and ensure it has the required permissions."
            )
        elif "write access to repository not granted" in error_str.lower():
            context["error_message"] = (
                "Access denied to repository. This error occurs because:\n\n"
                "• Your GitHub token doesn't have access to this specific repository\n"
                "• For organization repositories like 'cyberdrain/cow-frontend', you need:\n"
                "  - The organization owner must grant your token access\n"
                "  - Your token needs 'repo' scope (not just 'public_repo')\n"
                "  - You must be a member of the organization with appropriate permissions\n\n"
                "Note: Even for read-only access, GitHub requires 'repo' scope for private repositories.\n"
                "Contact the repository owner to grant access to your GitHub account."
            )
        elif "Repository not found or access denied" in error_str:
            if github_token:
                context["error_message"] = (
                    "Repository not found or access denied. This could mean:\n"
                    "• The repository doesn't exist\n"
                    "• Your token doesn't have access to this repository\n"
                    "• For organization repositories, ensure your token has organization access\n"
                    "• Check that your token has 'repo' scope permissions"
                )
            else:
                context["error_message"] = (
                    "Repository not found or access denied. This repository may be private. "
                    "Please provide a GitHub Personal Access Token to access private repositories."
                )
        elif "authentication failed" in error_str.lower() or "invalid credentials" in error_str.lower():
            context["error_message"] = (
                "Git authentication failed. Please verify:\n"
                "• Your GitHub Personal Access Token is valid and not expired\n"
                "• The token has 'repo' scope permissions\n"
                "• For organization repositories, the token has organization access"
            )
        else:
            context["error_message"] = f"Error: {exc}"
            
        return template_response(context=context)

    if len(content) > MAX_DISPLAY_SIZE:
        content = (
            f"(Files content cropped to {int(MAX_DISPLAY_SIZE / 1_000)}k characters, "
            "download full ingest to see more)\n" + content[:MAX_DISPLAY_SIZE]
        )

    _print_success(
        url=query.url,
        max_file_size=max_file_size,
        pattern_type=pattern_type,
        pattern=pattern,
        summary=summary,
    )

    context.update(
        {
            "result": True,
            "summary": summary,
            "tree": tree,
            "content": content,
            "ingest_id": query.id,
        }
    )

    return template_response(context=context)


def _print_query(url: str, max_file_size: int, pattern_type: str, pattern: str) -> None:
    """
    Print a formatted summary of the query details, including the URL, file size,
    and pattern information, for easier debugging or logging.

    Parameters
    ----------
    url : str
        The URL associated with the query.
    max_file_size : int
        The maximum file size allowed for the query, in bytes.
    pattern_type : str
        Specifies the type of pattern to use, either "include" or "exclude".
    pattern : str
        The actual pattern string to include or exclude in the query.
    """
    print(f"{Colors.WHITE}{url:<20}{Colors.END}", end="")
    if int(max_file_size / 1024) != 50:
        print(f" | {Colors.YELLOW}Size: {int(max_file_size/1024)}kb{Colors.END}", end="")
    if pattern_type == "include" and pattern != "":
        print(f" | {Colors.YELLOW}Include {pattern}{Colors.END}", end="")
    elif pattern_type == "exclude" and pattern != "":
        print(f" | {Colors.YELLOW}Exclude {pattern}{Colors.END}", end="")


def _print_error(url: str, e: Exception, max_file_size: int, pattern_type: str, pattern: str) -> None:
    """
    Print a formatted error message including the URL, file size, pattern details, and the exception encountered,
    for debugging or logging purposes.

    Parameters
    ----------
    url : str
        The URL associated with the query that caused the error.
    e : Exception
        The exception raised during the query or process.
    max_file_size : int
        The maximum file size allowed for the query, in bytes.
    pattern_type : str
        Specifies the type of pattern to use, either "include" or "exclude".
    pattern : str
        The actual pattern string to include or exclude in the query.
    """
    print(f"{Colors.BROWN}WARN{Colors.END}: {Colors.RED}<-  {Colors.END}", end="")
    _print_query(url, max_file_size, pattern_type, pattern)
    print(f" | {Colors.RED}{e}{Colors.END}")


def _print_success(url: str, max_file_size: int, pattern_type: str, pattern: str, summary: str) -> None:
    """
    Print a formatted success message, including the URL, file size, pattern details, and a summary with estimated
    tokens, for debugging or logging purposes.

    Parameters
    ----------
    url : str
        The URL associated with the successful query.
    max_file_size : int
        The maximum file size allowed for the query, in bytes.
    pattern_type : str
        Specifies the type of pattern to use, either "include" or "exclude".
    pattern : str
        The actual pattern string to include or exclude in the query.
    summary : str
        A summary of the query result, including details like estimated tokens.
    """
    estimated_tokens = summary[summary.index("Estimated tokens:") + len("Estimated ") :]
    print(f"{Colors.GREEN}INFO{Colors.END}: {Colors.GREEN}<-  {Colors.END}", end="")
    _print_query(url, max_file_size, pattern_type, pattern)
    print(f" | {Colors.PURPLE}{estimated_tokens}{Colors.END}")

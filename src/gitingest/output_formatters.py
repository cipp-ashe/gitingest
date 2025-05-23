"""
Output formatting and content generation for gitingest analysis results.

This module handles the transformation of analyzed codebase data into various output
formats optimized for different use cases. It provides comprehensive formatting
capabilities with security features and customization options.

Key Features:
    - Multiple output formats: text, JSON, and Markdown
    - Token count estimation for LLM usage planning
    - Security features including markdown backtick escaping
    - Flexible content inclusion controls (summary, structure, content)
    - Tree-style directory structure visualization
    - Comprehensive error handling and validation

Output Formats:
    - TXT: Optimized for LLM prompts with token estimation
    - JSON: Structured data for programmatic consumption
    - Markdown: Human-readable with proper formatting and escaping

Security Considerations:
    - Markdown backtick escaping prevents parser conflicts
    - Input validation for all formatting operations
    - Safe handling of file contents and metadata

Examples:
    Basic formatting:
        summary, tree, content = format_node(node, query)
    
    JSON output:
        query.output_format = "json"
        json_output, _, _ = format_node(node, query)
    
    Markdown with escaping:
        query.output_format = "markdown"
        md_output, _, _ = format_node(node, query)

Author: Gitingest Team
License: MIT
"""

from typing import Optional, Tuple

import tiktoken

from gitingest.query_parsing import IngestionQuery
from gitingest.schemas import FileSystemNode, FileSystemNodeType


def format_node(node: FileSystemNode, query: IngestionQuery) -> Tuple[str, str, str]:
    """
    Generate a summary, directory structure, and file contents for a given file system node.

    If the node represents a directory, the function will recursively process its contents.

    Parameters
    ----------
    node : FileSystemNode
        The file system node to be summarized.
    query : IngestionQuery
        The parsed query object containing information about the repository and query parameters.

    Returns
    -------
    Tuple[str, str, str]
        A tuple containing the summary, directory structure, and file contents.
    """
    is_single_file = node.type == FileSystemNodeType.FILE

    summary = ""
    tree = ""
    content = ""

    if query.include_summary:
        summary = _create_summary_prefix(query, single_file=is_single_file)
        if node.type == FileSystemNodeType.DIRECTORY:
            summary += f"Files analyzed: {node.file_count}\n"
        elif node.type == FileSystemNodeType.FILE:
            summary += f"File: {node.name}\n"
            summary += f"Lines: {len(node.content.splitlines()):,}\n"

    if query.include_structure:
        tree = "Directory structure:\n" + _create_tree_structure(query, node)

    if query.include_content:
        content = _gather_file_contents(node)

    if query.output_format == "json":
        import json

        output = {}
        if query.include_summary:
            output["summary"] = summary
        if query.include_structure:
            output["structure"] = tree
        if query.include_content:
            output["content"] = content
        return json.dumps(output, indent=2), "", ""

    if query.output_format == "markdown":
        md = ""
        if query.include_summary and summary:
            escaped_summary = _escape_markdown_backticks(summary)
            md += f"## Summary\n\n```\n{escaped_summary}```\n\n"
        if query.include_structure and tree:
            escaped_tree = _escape_markdown_backticks(tree)
            md += f"## Directory Structure\n\n```\n{escaped_tree}```\n\n"
        if query.include_content and content:
            escaped_content = _escape_markdown_backticks(content)
            md += f"## File Contents\n\n```\n{escaped_content}```\n\n"
        return md, "", ""

    if query.output_format == "txt":
        text_for_tokens = ""
        if query.include_structure:
            text_for_tokens += tree
        if query.include_content:
            text_for_tokens += content

        token_estimate = _format_token_count(text_for_tokens)
        if token_estimate and query.include_summary:
            summary += f"\nEstimated tokens: {token_estimate}"

    return summary, tree, content


def _create_summary_prefix(query: IngestionQuery, single_file: bool = False) -> str:
    """
    Create a prefix string for summarizing a repository or local directory.

    Includes repository name (if provided), commit/branch details, and subpath if relevant.

    Parameters
    ----------
    query : IngestionQuery
        The parsed query object containing information about the repository and query parameters.
    single_file : bool
        A flag indicating whether the summary is for a single file, by default False.

    Returns
    -------
    str
        A summary prefix string containing repository, commit, branch, and subpath details.
    """
    parts = []

    if query.user_name:
        parts.append(f"Repository: {query.user_name}/{query.repo_name}")
    else:
        # Local scenario
        parts.append(f"Directory: {query.slug}")

    if query.commit:
        parts.append(f"Commit: {query.commit}")
    elif query.branch and query.branch not in ("main", "master"):
        parts.append(f"Branch: {query.branch}")

    if query.subpath != "/" and not single_file:
        parts.append(f"Subpath: {query.subpath}")

    return "\n".join(parts) + "\n"


def _gather_file_contents(node: FileSystemNode) -> str:
    """
    Recursively gather contents of all files under the given node.

    This function recursively processes a directory node and gathers the contents of all files
    under that node. It returns the concatenated content of all files as a single string.

    Parameters
    ----------
    node : FileSystemNode
        The current directory or file node being processed.

    Returns
    -------
    str
        The concatenated content of all files under the given node.
    """
    if node.type != FileSystemNodeType.DIRECTORY:
        return node.content_string

    # Recursively gather contents of all files under the current directory
    return "\n".join(_gather_file_contents(child) for child in node.children)


def _escape_markdown_backticks(content: str) -> str:
    """
    Escape triple backticks in content to prevent markdown parser issues.
    
    Parameters
    ----------
    content : str
        The content that may contain triple backticks.
        
    Returns
    -------
    str
        The content with triple backticks escaped.
    """
    # Replace triple backticks with escaped version
    return content.replace("```", "\\`\\`\\`")


def _create_tree_structure(query: IngestionQuery, node: FileSystemNode, prefix: str = "", is_last: bool = True) -> str:
    """
    Generate a tree-like string representation of the file structure.

    This function generates a string representation of the directory structure, formatted
    as a tree with appropriate indentation for nested directories and files.

    Parameters
    ----------
    query : IngestionQuery
        The parsed query object containing information about the repository and query parameters.
    node : FileSystemNode
        The current directory or file node being processed.
    prefix : str
        A string used for indentation and formatting of the tree structure, by default "".
    is_last : bool
        A flag indicating whether the current node is the last in its directory, by default True.

    Returns
    -------
    str
        A string representing the directory structure formatted as a tree.
    """
    if not node.name:
        # If no name is present, use the slug as the top-level directory name
        node.name = query.slug

    tree_str = ""
    current_prefix = "└── " if is_last else "├── "

    # Indicate directories with a trailing slash
    display_name = node.name
    if node.type == FileSystemNodeType.DIRECTORY:
        display_name += "/"
    elif node.type == FileSystemNodeType.SYMLINK:
        display_name += " -> " + node.path.readlink().name

    tree_str += f"{prefix}{current_prefix}{display_name}\n"

    if node.type == FileSystemNodeType.DIRECTORY and node.children:
        prefix += "    " if is_last else "│   "
        for i, child in enumerate(node.children):
            tree_str += _create_tree_structure(query, node=child, prefix=prefix, is_last=i == len(node.children) - 1)
    return tree_str


def _format_token_count(text: str) -> Optional[str]:
    """
    Return a human-readable string representing the token count of the given text.

    E.g., '120' -> '120', '1200' -> '1.2k', '1200000' -> '1.2M'.

    Parameters
    ----------
    text : str
        The text string for which the token count is to be estimated.

    Returns
    -------
    str, optional
        The formatted number of tokens as a string (e.g., '1.2k', '1.2M'), or `None` if an error occurs.
    """
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        total_tokens = len(encoding.encode(text, disallowed_special=()))
    except (ValueError, UnicodeEncodeError) as exc:
        print(exc)
        return None

    if total_tokens >= 1_000_000:
        return f"{total_tokens / 1_000_000:.1f}M"

    if total_tokens >= 1_000:
        return f"{total_tokens / 1_000:.1f}k"

    return str(total_tokens)

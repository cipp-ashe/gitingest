"""
Main entry point and orchestration layer for gitingest processing pipeline.

This module serves as the primary interface for the gitingest system, coordinating
the entire analysis workflow from source parsing to output generation. It handles
both synchronous and asynchronous operations, repository cloning, temporary file
management, and comprehensive error handling.

Key Responsibilities:
    - Orchestrate the complete ingestion pipeline
    - Handle repository cloning and cleanup
    - Manage temporary directories with debug support
    - Coordinate between parsing, analysis, and formatting
    - Provide both sync and async interfaces
    - Centralize output file writing with format support

Pipeline Flow:
    1. Parse and validate input source and parameters
    2. Clone repository if needed (with PAT support)
    3. Analyze codebase structure and content
    4. Format output according to specified format
    5. Write results to file or return for console output
    6. Clean up temporary resources (unless debug mode)

Features:
    - Support for local directories and remote repositories
    - Multiple output formats (txt, json, markdown)
    - Advanced filtering and pattern matching
    - Debug mode with temporary directory preservation
    - Comprehensive error handling and logging
    - Private repository access via PAT tokens

Examples:
    Basic usage:
        summary, tree, content = await ingest_async("https://github.com/user/repo")
    
    With custom options:
        result = await ingest_async(
            source=".",
            output_format="json",
            include_patterns={"*.py"},
            keep_temp=True
        )
    
    Synchronous usage:
        summary, tree, content = ingest("/path/to/directory")

Author: Gitingest Team
License: MIT
"""

import asyncio
import inspect
import shutil
from typing import Optional, Set, Tuple, Union

from gitingest.cloning import clone_repo
from gitingest.config import TMP_BASE_PATH
from gitingest.ingestion import ingest_query
from gitingest.query_parsing import IngestionQuery, parse_query


def _write_output_file(output_path: str, summary: str, tree: str, content: str, output_format: str) -> None:
    """
    Write the output to a file in the specified format.
    
    This centralizes output rendering logic to eliminate redundancy.
    
    Parameters
    ----------
    output_path : str
        The path where the output file will be written.
    summary : str
        The summary content.
    tree : str
        The directory structure content.
    content : str
        The file contents.
    output_format : str
        The output format ("txt", "json", "markdown").
    """
    with open(output_path, "w", encoding="utf-8") as f:
        if output_format == "json":
            import json
            output_data = {}
            if summary:
                output_data["summary"] = summary
            if tree:
                output_data["structure"] = tree
            if content:
                output_data["content"] = content
            f.write(json.dumps(output_data, indent=2))
        elif output_format == "markdown":
            if summary:
                f.write(f"## Summary\n\n```\n{summary}```\n\n")
            if tree:
                f.write(f"## Directory Structure\n\n```\n{tree}```\n\n")
            if content:
                f.write(f"## File Contents\n\n```\n{content}```\n\n")
        else:  # txt format
            if tree:
                f.write(tree)
            if content:
                f.write("\n" + content)


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
    Main entry point for ingesting a source and processing its contents.

    This function analyzes a source (URL or local path), clones the corresponding repository (if applicable),
    and processes its files according to the specified query parameters. It returns a summary, a tree-like
    structure of the files, and the content of the files. The results can optionally be written to an output file.

    Parameters
    ----------
    source : str
        The source to analyze, which can be a URL (for a Git repository) or a local directory path.
    max_file_size : int
        Maximum allowed file size for file ingestion. Files larger than this size are ignored, by default
        10*1024*1024 (10 MB).
    include_patterns : Union[str, Set[str]], optional
        Pattern or set of patterns specifying which files to include. If `None`, all files are included.
    exclude_patterns : Union[str, Set[str]], optional
        Pattern or set of patterns specifying which files to exclude. If `None`, no files are excluded.
    branch : str, optional
        The branch to clone and ingest. If `None`, the default branch is used.
    output : str, optional
        File path where the summary and content should be written. If `None`, the results are not written to a file.

    Returns
    -------
    Tuple[str, str, str]
        A tuple containing:
        - A summary string of the analyzed repository or directory.
        - A tree-like string representation of the file structure.
        - The content of the files in the repository or directory.

    Raises
    ------
    TypeError
        If `clone_repo` does not return a coroutine, or if the `source` is of an unsupported type.
    """
    repo_cloned = False

    try:
        query: IngestionQuery = await parse_query(
            source=source,
            max_file_size=max_file_size,
            from_web=False,
            include_patterns=include_patterns,
            ignore_patterns=exclude_patterns,
            include_summary=include_summary,
            include_structure=include_structure,
            include_content=include_content,
            output_format=output_format,
            pat_token=pat_token,
        )

        if query.url:
            selected_branch = branch if branch else query.branch  # prioritize branch argument
            query.branch = selected_branch

            clone_config = query.extract_clone_config()
            clone_coroutine = clone_repo(clone_config)

            if inspect.iscoroutine(clone_coroutine):
                if asyncio.get_event_loop().is_running():
                    await clone_coroutine
                else:
                    asyncio.run(clone_coroutine)
            else:
                raise TypeError("clone_repo did not return a coroutine as expected.")

            repo_cloned = True

        summary, tree, content = ingest_query(query)

        # Centralized output rendering using format_node
        if output is not None:
            _write_output_file(output, summary, tree, content, query.output_format)

        return summary, tree, content
    finally:
        # Clean up the temporary directory if it was created (unless keep_temp is True)
        if repo_cloned and not keep_temp:
            try:
                shutil.rmtree(TMP_BASE_PATH, ignore_errors=True)
            except Exception as e:
                # Log the error but don't fail the entire operation
                print(f"Warning: Failed to clean up temporary directory {TMP_BASE_PATH}: {e}")
        elif repo_cloned and keep_temp:
            print(f"🔧 DEBUG: Temporary directory preserved at: {TMP_BASE_PATH}")


def ingest(
    source: str,
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB
    include_patterns: Optional[Union[str, Set[str]]] = None,
    exclude_patterns: Optional[Union[str, Set[str]]] = None,
    branch: Optional[str] = None,
    output: Optional[str] = None,
) -> Tuple[str, str, str]:
    """
    Synchronous version of ingest_async.

    This function analyzes a source (URL or local path), clones the corresponding repository (if applicable),
    and processes its files according to the specified query parameters. It returns a summary, a tree-like
    structure of the files, and the content of the files. The results can optionally be written to an output file.

    Parameters
    ----------
    source : str
        The source to analyze, which can be a URL (for a Git repository) or a local directory path.
    max_file_size : int
        Maximum allowed file size for file ingestion. Files larger than this size are ignored, by default
        10*1024*1024 (10 MB).
    include_patterns : Union[str, Set[str]], optional
        Pattern or set of patterns specifying which files to include. If `None`, all files are included.
    exclude_patterns : Union[str, Set[str]], optional
        Pattern or set of patterns specifying which files to exclude. If `None`, no files are excluded.
    branch : str, optional
        The branch to clone and ingest. If `None`, the default branch is used.
    output : str, optional
        File path where the summary and content should be written. If `None`, the results are not written to a file.

    Returns
    -------
    Tuple[str, str, str]
        A tuple containing:
        - A summary string of the analyzed repository or directory.
        - A tree-like string representation of the file structure.
        - The content of the files in the repository or directory.

    See Also
    --------
    ingest_async : The asynchronous version of this function.
    """
    return asyncio.run(
        ingest_async(
            source=source,
            max_file_size=max_file_size,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            branch=branch,
            output=output,
        )
    )

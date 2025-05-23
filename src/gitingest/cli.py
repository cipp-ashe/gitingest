"""
Command-line interface for the Gitingest package.

This module provides a comprehensive CLI for analyzing codebases and repositories.
It supports multiple output formats, advanced filtering, debugging features, and
both local directory and remote repository analysis.

Key Features:
    - Multiple output formats (txt, json, markdown)
    - Dry-run mode for preview without processing
    - Print-only mode for console output
    - Debug mode with temporary directory preservation
    - Advanced filtering with include/exclude patterns
    - Private repository access via PAT tokens
    - Comprehensive error handling and user feedback

Examples:
    Basic usage:
        $ gitingest .
        $ gitingest https://github.com/user/repo
    
    Advanced usage:
        $ gitingest --dry-run --output-format json --include-pattern "*.py" .
        $ gitingest --print-only --keep-temp https://github.com/user/repo
        
    Filtering:
        $ gitingest --include-pattern "*.py" --exclude-pattern "test_*" .
        
    Private repos:
        $ gitingest --pat-token TOKEN https://github.com/private/repo

Author: Gitingest Team
License: MIT
"""

# pylint: disable=no-value-for-parameter

import asyncio
from typing import Optional, Tuple

import click

from gitingest.config import MAX_FILE_SIZE, OUTPUT_FILE_NAME
from gitingest.entrypoint import ingest_async


@click.command()
@click.argument("source", type=str, default=".")
@click.option("--output", "-o", default=None, help="Output file path (default: <repo_name>.txt in current directory)")
@click.option("--max-size", "-s", default=MAX_FILE_SIZE, help="Maximum file size to process in bytes")
@click.option("--exclude-pattern", "-e", multiple=True, help="Patterns to exclude")
@click.option("--include-pattern", "-i", multiple=True, help="Patterns to include")
@click.option("--branch", "-b", default=None, help="Branch to clone and ingest")
@click.option("--include-summary/--no-include-summary", default=True, help="Include summary in export")
@click.option("--include-structure/--no-include-structure", default=True, help="Include directory structure in export")
@click.option("--include-content/--no-include-content", default=True, help="Include file contents in export")
@click.option("--output-format", type=click.Choice(["txt", "json", "markdown"]), default="txt", help="Output format for export")
@click.option("--pat-token", default=None, help="GitHub Personal Access Token for private repo access")
@click.option("--dry-run", is_flag=True, help="Analyze and show what would be processed without writing files")
@click.option("--print-only", is_flag=True, help="Print output to console instead of writing to file")
@click.option("--keep-temp", is_flag=True, help="Keep temporary directories for debugging (useful for development)")
def main(
    source: str,
    output: Optional[str],
    max_size: int,
    exclude_pattern: Tuple[str, ...],
    include_pattern: Tuple[str, ...],
    branch: Optional[str],
    include_summary: bool,
    include_structure: bool,
    include_content: bool,
    output_format: str,
    pat_token: Optional[str],
    dry_run: bool,
    print_only: bool,
    keep_temp: bool,
):
    """
     Main entry point for the CLI. This function is called when the CLI is run as a script.

    It calls the async main function to run the command.

    Parameters
    ----------
    source : str
        The source directory or repository to analyze.
    output : str, optional
        The path where the output file will be written. If not specified, the output will be written
        to a file named `<repo_name>.txt` in the current directory.
    max_size : int
        The maximum file size to process, in bytes. Files larger than this size will be ignored.
    exclude_pattern : Tuple[str, ...]
        A tuple of patterns to exclude during the analysis. Files matching these patterns will be ignored.
    include_pattern : Tuple[str, ...]
        A tuple of patterns to include during the analysis. Only files matching these patterns will be processed.
    branch : str, optional
        The branch to clone (optional).
    """
    # Main entry point for the CLI. This function is called when the CLI is run as a script.
    asyncio.run(_async_main(source, output, max_size, exclude_pattern, include_pattern, branch, include_summary, include_structure, include_content, output_format, pat_token, dry_run, print_only, keep_temp))

async def _async_main(
    source: str,
    output: Optional[str],
    max_size: int,
    exclude_pattern: Tuple[str, ...],
    include_pattern: Tuple[str, ...],
    branch: Optional[str],
    include_summary: bool,
    include_structure: bool,
    include_content: bool,
    output_format: str,
    pat_token: Optional[str],
    dry_run: bool,
    print_only: bool,
    keep_temp: bool,
) -> None:
    """
    Analyze a directory or repository and create a text dump of its contents.

    This command analyzes the contents of a specified source directory or repository, applies custom include and
    exclude patterns, and generates a text summary of the analysis which is then written to an output file.

    Parameters
    ----------
    source : str
        The source directory or repository to analyze.
    output : str, optional
        The path where the output file will be written. If not specified, the output will be written
        to a file named `<repo_name>.txt` in the current directory.
    max_size : int
        The maximum file size to process, in bytes. Files larger than this size will be ignored.
    exclude_pattern : Tuple[str, ...]
        A tuple of patterns to exclude during the analysis. Files matching these patterns will be ignored.
    include_pattern : Tuple[str, ...]
        A tuple of patterns to include during the analysis. Only files matching these patterns will be processed.
    branch : str, optional
        The branch to clone (optional).

    Raises
    ------
    Abort
        If there is an error during the execution of the command, this exception is raised to abort the process.
    """
    try:
        # Combine default and custom ignore patterns
        exclude_patterns = set(exclude_pattern)
        include_patterns = set(include_pattern)

        # Handle dry-run mode
        if dry_run:
            click.echo("🔍 DRY RUN MODE - Analyzing what would be processed...")
            click.echo(f"Source: {source}")
            click.echo(f"Max file size: {max_size:,} bytes")
            click.echo(f"Include patterns: {include_patterns if include_patterns else 'None'}")
            click.echo(f"Exclude patterns: {exclude_patterns if exclude_patterns else 'Default patterns only'}")
            click.echo(f"Output format: {output_format}")
            click.echo(f"Branch: {branch if branch else 'Default'}")
            click.echo("No files will be written or repositories cloned.")
            return

        # Determine output handling
        output_file = None if print_only else (output or OUTPUT_FILE_NAME)
        
        summary, tree, content = await ingest_async(
            source, 
            max_size, 
            include_patterns, 
            exclude_patterns, 
            branch, 
            output=output_file, 
            include_summary=include_summary, 
            include_structure=include_structure, 
            include_content=include_content, 
            output_format=output_format, 
            pat_token=pat_token,
            keep_temp=keep_temp
        )

        # Handle print-only mode
        if print_only:
            click.echo("📄 PRINT-ONLY MODE - Output to console:")
            click.echo("=" * 50)
            if include_summary and summary:
                click.echo(summary)
                click.echo("-" * 30)
            if include_structure and tree:
                click.echo(tree)
                click.echo("-" * 30)
            if include_content and content:
                click.echo(content)
        else:
            click.echo(f"✅ Analysis complete! Output written to: {output_file}")
            click.echo("\nSummary:")
            click.echo(summary)

    except Exception as exc:
        click.echo(f"❌ Error: {exc}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()

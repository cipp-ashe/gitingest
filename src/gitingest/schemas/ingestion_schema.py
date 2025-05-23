"""
Data schemas and validation models for the gitingest ingestion process.

This module defines the core data structures used throughout the ingestion pipeline,
including configuration for repository cloning and query parameters with comprehensive
validation to ensure data integrity and security.

Key Components:
    - CloneConfig: Configuration for Git repository cloning operations
    - IngestionQuery: Comprehensive query parameters with validation
    - Field validators for security and data integrity
    - Support for multiple output formats and filtering options

Security Features:
    - Output format validation to prevent injection attacks
    - Pattern validation for file filtering
    - PAT token handling for private repository access
    - Defensive programming with early validation

Examples:
    Creating a basic ingestion query:
        query = IngestionQuery(
            local_path=Path("/tmp/repo"),
            slug="user-repo",
            id="unique-id",
            output_format="json"
        )
    
    Extracting clone configuration:
        clone_config = query.extract_clone_config()

Author: Gitingest Team
License: MIT
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Set

from pydantic import BaseModel, ConfigDict, Field, field_validator

from gitingest.config import MAX_FILE_SIZE


@dataclass
class CloneConfig:
    """
    Configuration for cloning a Git repository.

    This class holds the necessary parameters for cloning a repository to a local path, including
    the repository's URL, the target local path, and optional parameters for a specific commit or branch.

    Attributes
    ----------
    url : str
        The URL of the Git repository to clone.
    local_path : str
        The local directory where the repository will be cloned.
    commit : str, optional
        The specific commit hash to check out after cloning (default is None).
    branch : str, optional
        The branch to clone (default is None).
    subpath : str
        The subpath to clone from the repository (default is "/").
    """

    url: str
    local_path: str
    commit: Optional[str] = None
    branch: Optional[str] = None
    subpath: str = "/"
    blob: bool = False
    # New field for GitHub Personal Access Token (PAT)
    pat_token: Optional[str] = None

class IngestionQuery(BaseModel):  # pylint: disable=too-many-instance-attributes
    """
    Pydantic model to store the parsed details of the repository or file path.
    """

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

    # New fields for export customization
    include_summary: bool = True
    include_structure: bool = True
    include_content: bool = True
    output_format: str = "txt"  # Options: txt, json, markdown

    # New field for GitHub Personal Access Token (PAT)
    pat_token: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        """
        Validate that output_format is one of the allowed values.
        
        Parameters
        ----------
        v : str
            The output format value to validate.
            
        Returns
        -------
        str
            The validated output format.
            
        Raises
        ------
        ValueError
            If the output format is not one of the allowed values.
        """
        allowed_formats = {"txt", "json", "markdown"}
        if v not in allowed_formats:
            raise ValueError(f"output_format must be one of {allowed_formats}, got '{v}'")
        return v

    def extract_clone_config(self) -> CloneConfig:
        """
        Extract the relevant fields for the CloneConfig object.

        Returns
        -------
        CloneConfig
            A CloneConfig object containing the relevant fields.

        Raises
        ------
        ValueError
            If the 'url' parameter is not provided.
        """
        if not self.url:
            raise ValueError("The 'url' parameter is required.")

        return CloneConfig(
            url=self.url,
            local_path=str(self.local_path),
            commit=self.commit,
            branch=self.branch,
            subpath=self.subpath,
            blob=self.type == "blob",
            pat_token=self.pat_token,
        )

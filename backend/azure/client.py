"""
Azure DevOps API Client

This module provides the main client for Azure DevOps API interactions.
It uses composition to organize functionality into domain-specific resources.
"""

import sys
import os

# Add the parent directory to sys.path to allow relative imports
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Local imports
from backend.azure.base_client import BaseAzureClient
from backend.azure.work_items import WorkItemsResource
from backend.azure.git import GitResource
from backend.azure.projects import ProjectsResource


class AzureDevOpsClient:
    """
    Main client for interacting with Azure DevOps API.
    Uses composition to provide access to different API resources.
    """

    def __init__(self):
        """Initialize the Azure DevOps client with resource handlers."""
        self._base_client = BaseAzureClient()
        self._work_items = None
        self._git = None
        self._projects = None

    @property
    def work_items(self) -> WorkItemsResource:
        """
        Get the work items resource handler.

        Returns:
            WorkItemsResource: Handler for work item operations
        """
        if self._work_items is None:
            self._work_items = WorkItemsResource(self._base_client)
        return self._work_items

    @property
    def git(self) -> GitResource:
        """
        Get the git resource handler.

        Returns:
            GitResource: Handler for git repository operations
        """
        if self._git is None:
            self._git = GitResource(self._base_client)
        return self._git

    @property
    def projects(self) -> ProjectsResource:
        """
        Get the projects resource handler.

        Returns:
            ProjectsResource: Handler for project operations
        """
        if self._projects is None:
            self._projects = ProjectsResource(self._base_client)
        return self._projects

    # Convenience method to make direct requests when needed
    def make_request(self, method, endpoint, api_version="6.0", data=None, params=None):
        """
        Make a direct request to the Azure DevOps API.

        This is a convenience method for cases where the specialized
        resource handlers don't provide the needed functionality.

        Args:
            method (str): HTTP method (GET, POST, PATCH, DELETE)
            endpoint (str): API endpoint (without organization URL)
            api_version (str, optional): API version. Defaults to "6.0".
            data (Optional[Dict], optional): Request body. Defaults to None.
            params (Optional[Dict], optional): Query parameters. Defaults to None.

        Returns:
            Dict: Response data as dictionary
        """
        return self._base_client._make_request(
            method, endpoint, api_version, data, params
        )

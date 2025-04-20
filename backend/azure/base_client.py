"""
Base Azure DevOps API Client

This module provides the base client for Azure DevOps API interactions.
It handles authentication and common request functionality.
"""

import requests
import base64
import json
import os
from typing import Dict, List, Optional, Any, Union

from backend.settings import organization_url, personal_access_token


class BaseAzureClient:
    """
    Base client for interacting with Azure DevOps API.
    Provides core functionality used by all specialized clients.
    """

    def __init__(self):
        """Initialize the base Azure DevOps client with settings from config."""
        self.organization_url = organization_url
        self.personal_access_token = personal_access_token
        self.headers = self._get_auth_headers()

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Create authentication headers using personal access token.

        Returns:
            Dict[str, str]: Headers with authentication information
        """
        encoded_pat = base64.b64encode(
            f":{self.personal_access_token}".encode()
        ).decode()
        return {
            "Authorization": f"Basic {encoded_pat}",
            "Content-Type": "application/json",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        api_version: str = "6.0",
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        content_type: Optional[str] = None,
    ) -> Any:
        """
        Make a request to the Azure DevOps API.

        Args:
            method (str): HTTP method (GET, POST, PATCH, DELETE)
            endpoint (str): API endpoint (without organization URL)
            api_version (str, optional): API version. Defaults to "6.0".
            data (Optional[Dict], optional): Request body. Defaults to None.
            params (Optional[Dict], optional): Query parameters. Defaults to None.
            content_type (Optional[str], optional): Custom content type. Defaults to None.

        Returns:
            Any: Response data as dictionary or raw content

        Raises:
            Exception: If the request fails
        """
        url = f"{self.organization_url}{endpoint}"

        # Add API version to params
        if params is None:
            params = {}
        params["api-version"] = api_version

        # Convert data to JSON if provided
        json_data = json.dumps(data) if data else None

        # Create headers with optional custom content type
        headers = self.headers.copy()
        if content_type:
            headers["Content-Type"] = content_type

        # Make the request
        response = requests.request(
            method=method, url=url, headers=headers, params=params, data=json_data
        )

        # Check if request was successful
        if response.status_code >= 200 and response.status_code < 300:
            try:
                return response.json() if response.content else {}
            except json.JSONDecodeError:
                return response.content
        else:
            error_message = f"Request failed with status code {response.status_code}: {response.text}"
            raise Exception(error_message)

"""
Work Items Resource

This module provides a specialized resource handler for Azure DevOps work item operations.
"""

from typing import Dict, List, Any, Optional


class WorkItemsResource:
    """
    Resource handler for Azure DevOps work item operations.
    """

    def __init__(self, base_client):
        """
        Initialize the work items resource handler.

        Args:
            base_client: The base Azure client for making API requests
        """
        self._client = base_client

    def get(self, work_item_id: int) -> Dict:
        """
        Get a work item by ID.

        Args:
            work_item_id (int): ID of the work item

        Returns:
            Dict: Work item data
        """
        endpoint = f"/_apis/wit/workitems/{work_item_id}"
        return self._client._make_request("GET", endpoint)

    def create(self, project: str, work_item_type: str, fields: Dict[str, Any]) -> Dict:
        """
        Create a new work item.

        Args:
            project (str): Project name or ID
            work_item_type (str): Type of work item (Bug, Task, etc.)
            fields (Dict[str, Any]): Fields to set on the work item

        Returns:
            Dict: Created work item data
        """
        endpoint = f"/{project}/_apis/wit/workitems/${work_item_type}"

        # Format the fields as Azure DevOps API expects
        operations = []
        for field_name, field_value in fields.items():
            operations.append(
                {"op": "add", "path": f"/fields/{field_name}", "value": field_value}
            )

        # Azure DevOps API requires application/json-patch+json content type for work item operations
        return self._client._make_request(
            "POST",
            endpoint,
            data=operations,
            content_type="application/json-patch+json",
        )

    def update(
        self, work_item_id: int, project: str, updates: List[Dict[str, Any]]
    ) -> Dict:
        """
        Update an existing work item.

        Args:
            work_item_id (int): ID of the work item to update
            project (str): Project name or ID
            updates (List[Dict[str, Any]]): List of update operations in the format:
                [
                    {"op": "add", "path": "/fields/System.Title", "value": "New Title"},
                    {"op": "remove", "path": "/fields/System.Reason"}
                ]

        Returns:
            Dict: Updated work item data
        """
        endpoint = f"/{project}/_apis/wit/workitems/{work_item_id}"
        # Azure DevOps API requires application/json-patch+json content type for PATCH operations
        return self._client._make_request(
            "PATCH", endpoint, data=updates, content_type="application/json-patch+json"
        )

    def query(
        self, project: str, query_text: str, top: Optional[int] = None
    ) -> List[Dict]:
        """
        Query work items using WIQL.

        Args:
            project (str): Project name or ID
            query_text (str): WIQL query text
            top (Optional[int], optional): Maximum number of items to return. Defaults to None.

        Returns:
            List[Dict]: List of work items matching the query
        """
        endpoint = f"/{project}/_apis/wit/wiql"

        data = {"query": query_text}

        params = {}
        if top is not None:
            params["$top"] = top

        response = self._client._make_request(
            "POST", endpoint, data=data, params=params
        )

        # The response contains work item references, not the full work items
        # We need to get the full work items separately
        work_item_refs = response.get("workItems", [])

        if not work_item_refs:
            return []

        # Get the IDs of the work items
        work_item_ids = [item["id"] for item in work_item_refs]

        # Get the full work items
        # Azure DevOps API allows getting multiple work items in a single request
        ids_str = ",".join(map(str, work_item_ids))
        endpoint = f"/_apis/wit/workitems?ids={ids_str}"

        full_response = self._client._make_request("GET", endpoint)
        return full_response.get("value", [])

    def get_work_item_types(self, project: str) -> List[Dict]:
        """
        Get all work item types in a project.

        Args:
            project (str): Project name or ID

        Returns:
            List[Dict]: List of work item types
        """
        endpoint = f"/{project}/_apis/wit/workitemtypes"
        response = self._client._make_request("GET", endpoint)
        return response.get("value", [])

    def get_work_item_states(self, project: str, work_item_type: str) -> List[Dict]:
        """
        Get all states for a work item type.

        Args:
            project (str): Project name or ID
            work_item_type (str): Type of work item (Bug, Task, etc.)

        Returns:
            List[Dict]: List of work item states
        """
        endpoint = f"/{project}/_apis/wit/workitemtypes/{work_item_type}/states"
        response = self._client._make_request("GET", endpoint)
        return response.get("value", [])

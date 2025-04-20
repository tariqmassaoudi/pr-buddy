"""
Work Items Module

This module provides functions for working with Azure DevOps work items.
It uses the AzureDevOpsClient for all API interactions.
"""

import sys
import os
from typing import Dict, List, Optional

# Add the parent directory to sys.path to enable relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the AzureDevOpsClient from the azure module
from azure.client import AzureDevOpsClient


def get_projects() -> List[Dict]:
    """Get all projects in the organization.

    Returns:
        List of projects in the Azure DevOps organization
    """
    try:
        print("hello")
        client = AzureDevOpsClient()
        return client.projects.get_all()
    except Exception as e:
        print(f"Error retrieving projects: {str(e)}")
        return []


def get_work_items(
    project: str, query_text: str, top: Optional[int] = None
) -> List[Dict]:
    """Query work items using WIQL (Work Item Query Language).

    Args:
        project: Project name or ID
        query_text: WIQL query text iclude a where clause for the project, example: WHERE [System.TeamProject] = 'Power to X'
        top: Maximum number of items to return

    Returns:
        List of work items matching the query
    """
    try:
        client = AzureDevOpsClient()
        return client.work_items.query(project, query_text, top)
    except Exception as e:
        print(f"Error querying work items: {str(e)}")
        return []


def get_work_item(work_item_id: int) -> Dict:
    """Get a work item by ID.

    Args:
        work_item_id: ID of the work item

    Returns:
        Work item data
    """
    try:
        client = AzureDevOpsClient()
        return client.work_items.get(work_item_id)
    except Exception as e:
        print(f"Error retrieving work item {work_item_id}: {str(e)}")
        return {}


def update_work_item(work_item_id: int, project: str, updates: list) -> Dict:
    """Update an existing work item, you can change the title, description, assigned to, state, add comments and link the work item to a PR.

    Args:
        work_item_id: ID of the work item to update
        project: Project name or ID
        updates: List of update operations in the format: [{"op": "add", "path": "/fields/System.Title", "value": "New Title"}]

    Returns:
        Updated work item data
    """
    try:
        client = AzureDevOpsClient()
        return client.work_items.update(work_item_id, project, updates)
    except Exception as e:
        print(f"Error updating work item {work_item_id}: {str(e)}")
        return {}


def create_work_item(
    project: str,
    work_item_type: str,
    title: str,
    description: Optional[str] = None,
    assigned_to: Optional[str] = None,
    **fields,
) -> Dict:
    """Create a new work item.

    Args:
        project: Project name or ID
        work_item_type: Type of work item (Bug, Task, etc.)
        title: Title of the work item
        description: Description of the work item
        assigned_to: User to assign the work item to
        **fields: Additional fields to set on the work item

    Returns:
        Created work item data
    """
    try:
        client = AzureDevOpsClient()

        # Prepare fields
        work_item_fields = {"System.Title": title, **fields}

        if description:
            work_item_fields["System.Description"] = description

        if assigned_to:
            work_item_fields["System.AssignedTo"] = assigned_to

        return client.work_items.create(project, work_item_type, work_item_fields)
    except Exception as e:
        print(f"Error creating work item: {str(e)}")
        return {}


# Example usage
if __name__ == "__main__":
    # Get all projects
    projects = get_projects()
    if projects:
        print("List of projects:")
        for project in projects:
            print(f"- {project['name']} (ID: {project['id']})")

        # Example: query work items from the first project
        if projects:
            first_project = projects[0]["name"]
            query = (
                "SELECT [System.Id], [System.Title] FROM WorkItems WHERE [System.TeamProject] = '"
                + first_project
                + "'"
            )
            print(f"\nQuerying work items in {first_project}:")
            work_items = get_work_items(first_project, query, top=5)

            if work_items:
                for item in work_items:
                    print(
                        f"- Work Item #{item.get('id')}: {item.get('fields', {}).get('System.Title', 'No Title')}"
                    )

                # Example: get details of the first work item
                if work_items:
                    first_item_id = work_items[0].get("id")
                    print(f"\nGetting details for Work Item #{first_item_id}:")
                    details = get_work_item(first_item_id)
                    print(f"Title: {details.get('fields', {}).get('System.Title')}")
                    print(f"State: {details.get('fields', {}).get('System.State')}")
            else:
                print(f"No work items found in {first_project}")

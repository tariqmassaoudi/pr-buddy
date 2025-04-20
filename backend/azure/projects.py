"""
Projects Resource

This module provides a specialized resource handler for Azure DevOps project operations.
"""

from typing import Dict, List, Any, Optional


class ProjectsResource:
    """
    Resource handler for Azure DevOps project operations.
    """

    def __init__(self, base_client):
        """
        Initialize the Projects resource handler.

        Args:
            base_client: The base Azure client for making API requests
        """
        self._client = base_client

    def get_all(
        self, state: Optional[str] = None, top: Optional[int] = None
    ) -> List[Dict]:
        """
        Get all projects in the organization.

        Args:
            state (Optional[str]): Filter projects by state (wellFormed, createPending, etc.)
            top (Optional[int]): Maximum number of projects to return

        Returns:
            List[Dict]: List of projects
        """
        endpoint = "/_apis/projects"

        params = {}
        if state:
            params["stateFilter"] = state
        if top:
            params["$top"] = top

        response = self._client._make_request("GET", endpoint, params=params)
        return response.get("value", [])

    def get(self, project_id_or_name: str) -> Dict:
        """
        Get a project by ID or name.

        Args:
            project_id_or_name (str): ID or name of the project

        Returns:
            Dict: Project data
        """
        endpoint = f"/_apis/projects/{project_id_or_name}"
        return self._client._make_request("GET", endpoint)

    def get_team_members(
        self, project_id_or_name: str, team_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get team members of a project or specific team.

        Args:
            project_id_or_name (str): ID or name of the project
            team_id (Optional[str]): ID of the team. If not provided, gets members of the default team.

        Returns:
            List[Dict]: List of team members
        """
        if team_id:
            endpoint = f"/_apis/projects/{project_id_or_name}/teams/{team_id}/members"
        else:
            endpoint = f"/_apis/projects/{project_id_or_name}/teams/default/members"

        response = self._client._make_request("GET", endpoint)
        return response.get("value", [])

    def get_teams(self, project_id_or_name: str) -> List[Dict]:
        """
        Get all teams in a project.

        Args:
            project_id_or_name (str): ID or name of the project

        Returns:
            List[Dict]: List of teams
        """
        endpoint = f"/_apis/projects/{project_id_or_name}/teams"

        response = self._client._make_request("GET", endpoint)
        return response.get("value", [])

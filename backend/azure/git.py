"""
Git Resource

This module provides a specialized resource handler for Azure DevOps Git repository operations.
"""

from typing import Dict, List, Any, Optional


class GitResource:
    """
    Resource handler for Azure DevOps Git repository operations.
    """

    def __init__(self, base_client):
        """
        Initialize the Git resource handler.

        Args:
            base_client: The base Azure client for making API requests
        """
        self._client = base_client

    def get_repositories(self, project: Optional[str] = None) -> List[Dict]:
        """
        Get all Git repositories in the organization or in a specific project.

        Args:
            project (Optional[str]): Project name or ID. If provided, only repositories
                                    in this project will be returned.

        Returns:
            List[Dict]: List of repositories
        """
        if project:
            # Get repositories for a specific project
            endpoint = f"/{project}/_apis/git/repositories"
        else:
            # Get all repositories in the organization
            endpoint = "/_apis/git/repositories"

        response = self._client._make_request("GET", endpoint)
        return response.get("value", [])

    def get_file_content(self, repository_id: str, ref: str, path: str) -> str:
        """
        Get the content of a file in a Git repository.

        Args:
            repository_id (str): ID of the repository
            ref (str): Reference (branch, tag, commit) for the file
            path (str): Path to the file

        Returns:
            str: File content
        """
        endpoint = f"/_apis/git/repositories/{repository_id}/items/{path}?versionType=Branch&version={ref}"

        response = self._client._make_request("GET", endpoint)
        return response

    def get_branch_diff(
        self, repository_id: str, base_version: str, target_version: str
    ) -> Dict:
        """
        Get the diff between two branches in a repository

        Args:
            repository_id (str): ID of the Git repository
            base_version (str): Base branch name (e.g., 'develop')
            target_version (str): Target branch name (e.g., 'master')

        Returns:
            Dict: JSON response containing the diff information
        """
        endpoint = f"/_apis/git/repositories/{repository_id}/diffs/commits"
        params = {"baseVersion": base_version, "targetVersion": target_version}
        diffs = self._client._make_request("GET", endpoint, params=params)
        return diffs

    def get_repository(self, repository_id: str) -> Dict:
        """
        Get a Git repository by ID.

        Args:
            repository_id (str): ID of the repository

        Returns:
            Dict: Repository data
        """
        endpoint = f"/_apis/git/repositories/{repository_id}"
        return self._client._make_request("GET", endpoint)

    def get_branches(
        self, repository_id: str, filter_prefix: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all branches in a Git repository.

        Args:
            repository_id (str): ID of the repository
            filter_prefix (Optional[str]): Filter branches by prefix

        Returns:
            List[Dict]: List of branches
        """
        endpoint = f"/_apis/git/repositories/{repository_id}/refs"

        params = {}
        if filter_prefix:
            params["filter"] = filter_prefix
        else:
            params["filter"] = "heads/"

        response = self._client._make_request("GET", endpoint, params=params)
        return response.get("value", [])

    def get_commits(
        self,
        repository_id: str,
        branch: Optional[str] = None,
        top: Optional[int] = None,
    ) -> List[Dict]:
        """
        Get commits in a Git repository.

        Args:
            repository_id (str): ID of the repository
            branch (Optional[str]): Branch name to get commits from
            top (Optional[int]): Maximum number of commits to return

        Returns:
            List[Dict]: List of commits
        """
        endpoint = f"/_apis/git/repositories/{repository_id}/commits"

        params = {}
        if branch:
            params["searchCriteria.itemVersion.version"] = branch
        if top:
            params["$top"] = top

        response = self._client._make_request("GET", endpoint, params=params)
        return response.get("value", [])

    def get_project_pull_requests(
        self,
        project_id: str,
        status: Optional[str] = "active",
        top: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> List[Dict]:
        """
        Get pull requests for a specific project.

        Args:
            project_id (str): Project ID or name
            status (Optional[str]): Filter by PR status ("active", "completed", "abandoned", or "all")
            top (Optional[int]): Maximum number of pull requests to retrieve
            skip (Optional[int]): Number of pull requests to skip (for pagination)

        Returns:
            List[Dict]: List of pull requests with their details
        """
        # Build search criteria
        search_criteria = {}
        if status and status.lower() != "all":
            search_criteria["status"] = status

        # Build parameters
        params = {}
        if top is not None:
            params["$top"] = top
        if skip is not None:
            params["$skip"] = skip

        # Get pull requests using the Git resource handler
        endpoint = f"/{project_id}/_apis/git/pullrequests"

        # Add search criteria to params
        for key, value in search_criteria.items():
            params[f"searchCriteria.{key}"] = value

        response = self._client._make_request("GET", endpoint, params=params)
        return response.get("value", [])

    def get_pull_requests(
        self, repository_id: str, status: Optional[str] = "active"
    ) -> List[Dict]:
        """
        Get pull requests in a Git repository.

        Args:
            repository_id (str): ID of the repository
            status (Optional[str]): Status of pull requests to get
                                   (active, abandoned, completed, all)

        Returns:
            List[Dict]: List of pull requests
        """
        endpoint = f"/_apis/git/repositories/{repository_id}/pullrequests"

        params = {}
        if status:
            params["searchCriteria.status"] = status

        response = self._client._make_request("GET", endpoint, params=params)
        return response.get("value", [])

    def get_pull_request_details(
        self,
        pull_request_id: int,
        include_commits: bool = False,
        include_work_items: bool = False,
    ) -> Dict:
        """
        Get detailed information about a specific pull request.

        Args:
            pull_request_id (int): The ID of the pull request to retrieve
            include_commits (bool): If true, the pull request will be returned with the associated commits
            include_work_items (bool): If true, the pull request will be returned with the associated work item references

        Returns:
            Dict: Pull request details including metadata, commits (if requested), and work items (if requested)
        """
        # Build the endpoint URL
        endpoint = f"/_apis/git/pullrequests/{pull_request_id}"

        # Add optional parameters
        params = {}
        if include_commits:
            params["includeCommits"] = "true"
        if include_work_items:
            params["includeWorkItemRefs"] = "true"

        # Get the PR details
        return self._client._make_request("GET", endpoint, params=params)

    def create_pull_request(
        self,
        repository_id: str,
        source_branch: str,
        target_branch: str,
        title: str,
        description: Optional[str] = None,
        reviewers: Optional[List[str]] = None,
    ) -> Dict:
        """
        Create a pull request.

        Args:
            repository_id (str): ID of the repository
            source_branch (str): Source branch name
            target_branch (str): Target branch name
            title (str): Title of the pull request
            description (Optional[str]): Description of the pull request
            reviewers (Optional[List[str]]): List of reviewer IDs

        Returns:
            Dict: Created pull request data
        """
        endpoint = f"/_apis/git/repositories/{repository_id}/pullrequests"

        data = {
            "sourceRefName": f"refs/heads/{source_branch}",
            "targetRefName": f"refs/heads/{target_branch}",
            "title": title,
        }

        if description:
            data["description"] = description

        if reviewers:
            data["reviewers"] = [{"id": reviewer_id} for reviewer_id in reviewers]

        return self._client._make_request("POST", endpoint, data=data)

    def update_pull_request(
        self,
        repository_id: str,
        pull_request_id: int,
        project_id: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        target_ref_name: Optional[str] = None,
        completion_options: Optional[Dict[str, Any]] = None,
        merge_options: Optional[Dict[str, Any]] = None,
        auto_complete_set_by_id: Optional[str] = None,
    ) -> Dict:
        """
        Update a pull request with new information.

        Args:
            repository_id (str): The repository ID of the pull request's target branch
            pull_request_id (int): ID of the pull request to update
            project_id (Optional[str]): Project ID or project name. Can be omitted for some repositories.
            title (Optional[str]): New title for the pull request
            description (Optional[str]): New description for the pull request (up to 4000 characters)
            status (Optional[str]): New status for the pull request ('active', 'abandoned', 'completed')
            target_ref_name (Optional[str]): New target branch (when PR retargeting feature is enabled)
            completion_options (Optional[Dict[str, Any]]): Options affecting PR completion, like:
                - mergeStrategy: 'noFastForward', 'rebase', 'rebaseMerge', 'squash'
                - deleteSourceBranch: True/False
                - mergeCommitMessage: Custom commit message
            merge_options (Optional[Dict[str, Any]]): Options used when PR merge runs
            auto_complete_set_by_id (Optional[str]): ID of the user enabling auto-complete

        Returns:
            Dict: Updated pull request data
        """
        # Build the endpoint URL
        if project_id:
            endpoint = f"/{project_id}/_apis/git/repositories/{repository_id}/pullrequests/{pull_request_id}"
        else:
            endpoint = f"/_apis/git/repositories/{repository_id}/pullrequests/{pull_request_id}"

        # Build the update data
        data = {}

        # Add the fields that are being updated
        if title is not None:
            data["title"] = title

        if description is not None:
            data["description"] = description

        if status is not None:
            data["status"] = status

        if target_ref_name is not None:
            data["targetRefName"] = (
                f"refs/heads/{target_ref_name}"
                if not target_ref_name.startswith("refs/")
                else target_ref_name
            )

        if completion_options is not None:
            data["completionOptions"] = completion_options

        if merge_options is not None:
            data["mergeOptions"] = merge_options

        if auto_complete_set_by_id is not None:
            data["autoCompleteSetBy"] = {"id": auto_complete_set_by_id}

        # Make the PATCH request to update the pull request
        return self._client._make_request(
            "PATCH", endpoint, data=data, api_version="7.2-preview.2"
        )

    def create_pull_request_thread(
        self,
        repository_id: str,
        pull_request_id: int,
        content: str,
        status: str = "active",
        comment_type: str = "text",
        project_id: Optional[str] = None,
        file_path: Optional[str] = None,
        right_file_start: Optional[Dict[str, int]] = None,
        right_file_end: Optional[Dict[str, int]] = None,
        iteration_context: Optional[Dict[str, int]] = None,
        parent_comment_id: int = 0,
    ) -> Dict:
        """
        Create a comment thread on a pull request.

        Args:
            repository_id (str): ID of the repository
            pull_request_id (int): ID of the pull request to comment on
            content (str): Content of the comment
            status (str): Status of the thread ('active', 'closed', 'fixed', etc.)
            comment_type (str): Type of comment ('text', 'codeChange', 'system')
            project_id (Optional[str]): Project ID or name
            file_path (Optional[str]): Path to the file being commented on
            right_file_start (Optional[Dict[str, int]]): Start position in the file {"line": line_num, "offset": offset}
            right_file_end (Optional[Dict[str, int]]): End position in the file {"line": line_num, "offset": offset}
            iteration_context (Optional[Dict[str, int]]): Iteration context for the comment
            parent_comment_id (int): ID of the parent comment (for replies)

        Returns:
            Dict: Created comment thread data
        """
        # Map the status string to numeric value
        status_map = {
            "active": 1,
            "fixed": 2,
            "wontFix": 3,
            "closed": 4,
            "byDesign": 5,
            "pending": 6,
        }
        numeric_status = status_map.get(status, 1)  # Default to active if not found

        # Map the comment type string to numeric value
        comment_type_map = {
            "text": 1,
            "codeChange": 2,
            "system": 3,
        }
        numeric_comment_type = comment_type_map.get(
            comment_type, 1
        )  # Default to text if not found

        # Build the endpoint URL
        if project_id:
            endpoint = f"/{project_id}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/threads"
        else:
            endpoint = f"/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/threads"

        # Build the comment data
        comment = {
            "parentCommentId": parent_comment_id,
            "content": content,
            "commentType": numeric_comment_type,
        }

        data = {"comments": [comment], "status": numeric_status}

        # Add thread context if we're commenting on a specific file
        if file_path:
            thread_context = {"filePath": file_path}

            if right_file_start:
                thread_context["rightFileStart"] = right_file_start

            if right_file_end:
                thread_context["rightFileEnd"] = right_file_end

            data["threadContext"] = thread_context

        # Add pull request thread context for iteration-specific comments
        if iteration_context:
            data["pullRequestThreadContext"] = {"iterationContext": iteration_context}

        # Make the POST request to create the comment thread
        return self._client._make_request(
            "POST", endpoint, data=data, api_version="7.2-preview.1"
        )

    def get_pull_request_threads(
        self,
        repository_id: str,
        pull_request_id: int,
        project_id: Optional[str] = None,
        include_comments: bool = True,
        thread_id: Optional[int] = None,
    ) -> Dict:
        """
        Get comment threads for a pull request.

        Args:
            repository_id (str): ID of the repository
            pull_request_id (int): ID of the pull request
            project_id (Optional[str]): Project ID or name
            include_comments (bool): Whether to include the comments in the threads
            thread_id (Optional[int]): Specific thread ID to retrieve. If provided, only this thread is returned.

        Returns:
            Dict: Pull request comment threads
        """
        # Build the endpoint URL
        if project_id:
            if thread_id:
                endpoint = f"/{project_id}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/threads/{thread_id}"
            else:
                endpoint = f"/{project_id}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/threads"
        else:
            if thread_id:
                endpoint = f"/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/threads/{thread_id}"
            else:
                endpoint = f"/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/threads"

        # Add query parameters
        params = {}
        if include_comments:
            params["$expand"] = "comments"

        # Make the GET request to retrieve comment threads
        return self._client._make_request(
            "GET", endpoint, params=params, api_version="7.2-preview.1"
        )

    def delete_pull_request_comment(
        self, repository_id: str, pull_request_id: int, thread_id: int, comment_id: int
    ) -> Dict:
        """
        Delete a comment associated with a specific thread in a pull request.

        Args:
            repository_id (str): The repository ID of the pull request's target branch
            pull_request_id (int): ID of the pull request
            thread_id (int): ID of the thread that contains the comment
            comment_id (int): ID of the comment to delete

        Returns:
            Dict: Response indicating success or failure
        """
        # Build the endpoint URL
        endpoint = f"/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/threads/{thread_id}/comments/{comment_id}"

        # Make the DELETE request to remove the comment
        return self._client._make_request(
            "DELETE", endpoint, api_version="7.2-preview.1"
        )

    def update_pull_request_comment(
        self,
        repository_id: str,
        pull_request_id: int,
        thread_id: int,
        comment_id: int,
        content: str,
    ) -> Dict:
        """
        Update a comment associated with a specific thread in a pull request.

        Args:
            repository_id (str): The repository ID of the pull request's target branch
            pull_request_id (int): ID of the pull request
            thread_id (int): ID of the thread that contains the comment
            comment_id (int): ID of the comment to update
            content (str): The new content for the comment

        Returns:
            Dict: Updated comment information
        """
        # Build the endpoint URL
        endpoint = f"/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/threads/{thread_id}/comments/{comment_id}"

        # Prepare the request body with the updated content
        request_body = {"content": content}

        # Make the PATCH request to update the comment
        return self._client._make_request(
            "PATCH", endpoint, data=request_body, api_version="7.2-preview.1"
        )

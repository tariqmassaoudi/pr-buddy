"""
Git Repositories Module

This module provides functions for working with Azure DevOps Git repositories.
It uses the AzureDevOpsClient for all API interactions.
"""

import sys
import os
import difflib
from typing import Optional, List, Dict, Any

# Add the parent directory to sys.path to allow relative imports
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from backend.azure.client import AzureDevOpsClient


def get_repositories(project: Optional[str] = None) -> List[Dict]:
    """
    Get all Git repositories in the organization or in a specific project.

    Args:
        project: Project name or ID. If provided, only repositories in this project will be returned.

    Returns:
        List of repositories or None if the request fails
    """
    try:
        client = AzureDevOpsClient()
        response = client.git.get_repositories(project)
        return response
    except Exception as e:
        print(f"Error retrieving repositories: {str(e)}")
        return None


def get_repository(repository_id: str) -> Optional[Dict]:
    """
    Get a Git repository by ID.

    Args:
        repository_id (str): ID of the repository

    Returns:
        Dict: Repository data or None if the request fails
    """
    try:
        client = AzureDevOpsClient()
        endpoint = f"/_apis/git/repositories/{repository_id}"
        return client._make_request("GET", endpoint)
    except Exception as e:
        print(f"Error retrieving repository {repository_id}: {str(e)}")
        return None


def generate_git_style_diff(previous_content: str, current_content: str) -> str:
    """
    Generate a git-style diff with line numbers from two versions of file content.
    Shows all lines including unchanged ones, with proper indicators for additions and removals.

    Args:
        previous_content: Content of the file before changes
        current_content: Content of the file after changes

    Returns:
        A formatted string showing the diff with line numbers
    """
    # Handle cases where content might not be strings
    if not isinstance(previous_content, str):
        previous_content = str(previous_content)
    if not isinstance(current_content, str):
        current_content = str(current_content)

    # Split content into lines
    previous_lines = previous_content.splitlines()
    current_lines = current_content.splitlines()

    # Use SequenceMatcher to identify matching and differing blocks
    matcher = difflib.SequenceMatcher(None, previous_lines, current_lines)

    # Build the complete diff including all lines
    formatted_diff = []
    old_line_num = 1
    new_line_num = 1

    # Process each operation from the matcher
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            # Unchanged lines - include all of them
            for i, line in enumerate(previous_lines[i1:i2]):
                formatted_diff.append(
                    f"{old_line_num + i:4d} {new_line_num + i:4d}  {line}"
                )
            old_line_num += i2 - i1
            new_line_num += j2 - j1

        elif op == "delete":
            # Lines removed - show with '-' prefix
            for i, line in enumerate(previous_lines[i1:i2]):
                formatted_diff.append(f"{old_line_num + i:4d}      - {line}")
            old_line_num += i2 - i1

        elif op == "insert":
            # Lines added - show with '+' prefix
            for i, line in enumerate(current_lines[j1:j2]):
                formatted_diff.append(f"     {new_line_num + i:4d} + {line}")
            new_line_num += j2 - j1

        elif op == "replace":
            # Lines replaced - show both old and new versions
            for i, line in enumerate(previous_lines[i1:i2]):
                formatted_diff.append(f"{old_line_num + i:4d}      - {line}")
            old_line_num += i2 - i1

            for i, line in enumerate(current_lines[j1:j2]):
                formatted_diff.append(f"     {new_line_num + i:4d} + {line}")
            new_line_num += j2 - j1

    return "\n".join(formatted_diff)


def get_pr_changes(
    repository_id: str,
    source_branch: str,
    target_branch: str,
    max_files: int = 20,
) -> Dict[str, Any]:
    """
    Get changes between two branches for pull request creation with file content analysis.

    Retrieves the diff between source and target branches, collects the content of modified files,
    and formats the information in a way that's easy for an LLM to understand and generate a PR description.

    Args:
        repository_id: ID of the Git repository
        source_branch: The source branch containing the changes (e.g., 'feature/new-feature')
        target_branch: The target branch for the PR (e.g., 'main', 'develop')
        max_files: Maximum number of files to include in the analysis to avoid overloading the LLM

    Returns:
        Dictionary with structured information about the changes, including:
        - summary statistics (number of files changed, types of changes)
        - file changes with their content (before and after for modifications)
    """
    try:
        client = AzureDevOpsClient()

        # Get the diff between branches
        raw_diff = client.git.get_branch_diff(
            repository_id, target_branch, source_branch
        )

        # Filter out folder changes
        diff = raw_diff.copy()
        filtered_changes = [
            change
            for change in raw_diff.get("changes", [])
            if not change.get("item", {}).get("isFolder", False)
        ]
        diff["changes"] = filtered_changes

        # Recalculate change counts
        change_counts = {}
        for change in filtered_changes:
            change_type = change.get("changeType", "").capitalize()
            change_counts[change_type] = change_counts.get(change_type, 0) + 1

        diff["changeCounts"] = change_counts

        # Extract basic information
        result = {
            "summary": {
                "total_files_changed": sum(diff.get("changeCounts", {}).values()),
                "change_types": diff.get("changeCounts", {}),
            },
            "files": [],
        }

        # Get detailed file changes (limit to max_files)
        changes = diff.get("changes", [])
        file_count = 0

        for change in changes:
            if file_count >= max_files:
                break

            item = change.get("item", {})
            change_type = change.get("changeType", "").lower()

            # Skip folders, only process files
            if item.get("isFolder", False):
                continue

            file_path = item.get("path", "")

            # Skip certain files that would be less useful for PR description
            if file_path.endswith((".lock", ".pyc", ".svg", ".ico", ".woff", ".ttf")):
                continue

            file_info = {
                "path": file_path,
                "change_type": change_type,
            }

            # Check if file is a package-related file
            is_package_file = any(
                [
                    file_path.endswith(
                        (
                            "package.json",
                            "package-lock.json",
                            "requirements.txt",
                            "Pipfile",
                            "Pipfile.lock",
                            "poetry.lock",
                            "yarn.lock",
                            "composer.json",
                            "composer.lock",
                            "Gemfile",
                            "Gemfile.lock",
                        )
                    ),
                    "package" in file_path.lower(),
                    "dependencies" in file_path.lower(),
                    "requirements" in file_path.lower(),
                ]
            )

            # If it's a file modification, get both versions
            if change_type == "edit":
                try:
                    # Get current version from source branch
                    current_content = client.git.get_file_content(
                        repository_id, source_branch, file_path.lstrip("/")
                    )

                    # Get previous version from target branch
                    previous_content = client.git.get_file_content(
                        repository_id, target_branch, file_path.lstrip("/")
                    )

                    # Convert to string if needed
                    if not isinstance(current_content, str) and hasattr(
                        current_content, "decode"
                    ):
                        try:
                            current_content = current_content.decode("utf-8")
                        except UnicodeDecodeError:
                            current_content = (
                                f"[Binary content - {len(current_content)} bytes]"
                            )

                    if not isinstance(previous_content, str) and hasattr(
                        previous_content, "decode"
                    ):
                        try:
                            previous_content = previous_content.decode("utf-8")
                        except UnicodeDecodeError:
                            previous_content = (
                                f"[Binary content - {len(previous_content)} bytes]"
                            )

                    # Generate git-style diff with line numbers
                    file_info["diff"] = generate_git_style_diff(
                        previous_content, current_content
                    )

                except Exception as e:
                    # If we can't get content, note the error but continue
                    file_info["content_error"] = str(e)

            # For new files, just get the new content
            elif change_type == "add":
                try:
                    content = client.git.get_file_content(
                        repository_id, source_branch, file_path.lstrip("/")
                    )

                    # Convert to string if needed
                    if not isinstance(content, str) and hasattr(content, "decode"):
                        try:
                            content = content.decode("utf-8")
                        except UnicodeDecodeError:
                            content = f"[Binary content - {len(content)} bytes]"

                    # For new files, the diff is just the whole file with + prefixes
                    file_lines = (
                        content.splitlines()
                        if isinstance(content, str)
                        else str(content).splitlines()
                    )
                    diff_lines = ["@@ -0,0 +1,{} @@".format(len(file_lines))]
                    for i, line in enumerate(file_lines, 1):
                        diff_lines.append(f"{i:4d} +{line}")
                    file_info["diff"] = "\n".join(diff_lines)

                except Exception as e:
                    file_info["content_error"] = str(e)

            # Add the file info to our results
            result["files"].append(file_info)
            file_count += 1

        # Add a note if we hit the file limit
        if file_count >= max_files and len(changes) > max_files:
            result["summary"][
                "note"
            ] = f"Only showing {max_files} of {len(changes)} changed files."

        return result
    except Exception as e:
        print(f"Error retrieving PR changes: {str(e)}")
        return {"error": str(e)}


def get_pull_request_comments(
    repository_id: str,
    pull_request_id: int,
    project_id: Optional[str] = None,
    thread_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get comments on a pull request, either all comments or from a specific thread.

    This function retrieves comment threads from a pull request, providing a structured view of
    the conversation history including general comments and file-specific feedback.

    Args:
        repository_id: ID of the repository containing the pull request
        pull_request_id: ID of the pull request to retrieve comments from
        project_id: Optional project ID or name
        thread_id: Optional specific thread ID to retrieve

    Returns:
        Dictionary containing:
        - threads: List of comment threads with their IDs, status, and content
        - file_comments: Comments grouped by filename (if any)
        - general_comments: Comments not attached to specific files
    """
    try:
        client = AzureDevOpsClient()

        # Get the comment threads
        thread_data = client.git.get_pull_request_threads(
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            project_id=project_id,
            thread_id=thread_id,
        )

        result = {"threads": [], "file_comments": {}, "general_comments": []}

        # If we requested a specific thread, the response structure is different
        if thread_id:
            threads = [thread_data]  # Single thread in a different format
        else:
            threads = thread_data.get("value", [])

        # Process each thread
        for thread in threads:
            thread_info = {
                "id": thread.get("id"),
                "status": thread.get("status"),
                "created_date": thread.get("publishedDate"),
                "last_updated": thread.get("lastUpdatedDate"),
                "comments": [],
            }

            # Add comments from the thread
            for comment in thread.get("comments", []):
                comment_info = {
                    "id": comment.get("id"),
                    "content": comment.get("content"),
                    "author": comment.get("author", {}).get("displayName"),
                    "created_date": comment.get("publishedDate"),
                    "last_updated": comment.get("lastUpdatedDate"),
                    "comment_type": comment.get("commentType"),
                    "parent_id": comment.get("parentCommentId"),
                }
                thread_info["comments"].append(comment_info)

            # Add to the appropriate category
            result["threads"].append(thread_info)

            # Check if this is a file comment
            file_path = thread.get("threadContext", {}).get("filePath")
            if file_path:
                if file_path not in result["file_comments"]:
                    result["file_comments"][file_path] = []

                # Add position information if available
                file_comment = dict(thread_info)  # Copy the thread info
                if "rightFileStart" in thread.get("threadContext", {}):
                    file_comment["line"] = (
                        thread.get("threadContext", {})
                        .get("rightFileStart", {})
                        .get("line")
                    )

                result["file_comments"][file_path].append(file_comment)
            else:
                # This is a general comment on the PR
                result["general_comments"].append(thread_info)

        return result

    except Exception as e:
        print(f"Error retrieving pull request comments: {str(e)}")
        return {"error": str(e)}


def add_pull_request_comment(
    repository_id: str,
    pull_request_id: int,
    comment_content: str,
    file_path: str = None,
    line_number: int = None,
    status: str = "active",
    reply_to_comment_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Add a comment to a pull request, either as a general comment or on a specific file and line.

    This function allows adding different types of comments to pull requests:
    1) General PR comments by only providing the required parameters
    2) File-specific comments by providing file_path
    3) Line-specific comments by providing both file_path and line_number
    4) Replies to existing comments by providing reply_to_comment_id

    Args:
        repository_id: ID of the repository containing the pull request
        pull_request_id: ID of the pull request to comment on
        comment_content: The text content of the comment (supports markdown)
        file_path: path to file being commented on (for file-specific comments)
        line_number: line number in file (for line-specific comments)
        status: Status of the comment thread ('active', 'closed', 'fixed', 'wontFix', 'pending', 'byDesign')
        reply_to_comment_id: ID of an existing comment to reply to

    Returns:
        Dict with information about the created comment thread including its ID and status
    """
    try:
        client = AzureDevOpsClient()

        # Set up file positions if commenting on a specific line
        right_file_start = None
        right_file_end = None
        if file_path and line_number is not None:
            # Start at beginning of the line
            right_file_start = {"line": line_number, "offset": 1}
            # End at character 80 or a reasonable position if specific character not known
            right_file_end = {"line": line_number, "offset": 80}

        # Create the comment thread
        parent_comment_id = (
            reply_to_comment_id if reply_to_comment_id is not None else 0
        )

        thread = client.git.create_pull_request_thread(
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            content=comment_content,
            status=status,
            file_path=file_path,
            right_file_start=right_file_start,
            right_file_end=right_file_end,
            parent_comment_id=parent_comment_id,
        )

        # Format the response in a more LLM-friendly way
        if not thread:
            return {"error": "Failed to create comment thread"}
        print(thread)

        result = {
            "thread_id": thread.get("id"),
            "status": thread.get("status"),
            "comment_id": (
                thread.get("comments", [{}])[0].get("id")
                if thread.get("comments")
                else None
            ),
            "created_date": thread.get("publishedDate"),
            "has_file_context": False,  # Default to False, will update if threadContext exists
        }

        # Check if threadContext exists and has filePath
        thread_context = thread.get("threadContext")
        if thread_context is not None:
            result["has_file_context"] = thread_context.get("filePath") is not None
            result["file_path"] = thread_context.get("filePath")

            # Check for line number in rightFileStart
            right_file_start = thread_context.get("rightFileStart")
            if right_file_start is not None:
                result["line_number"] = right_file_start.get("line")

        print(result)
        return result

    except Exception as e:
        print(f"Error adding pull request comment: {str(e)}")
        return {"error": str(e)}


def delete_pull_request_comment(
    repository_id: str, pull_request_id: int, thread_id: int, comment_id: int
) -> Dict:
    """
    Delete a comment associated with a specific thread in a pull request.

    This function removes a specific comment from a pull request thread. This is useful for
    removing outdated or incorrect comments during code review processes.

    Args:
        repository_id: The repository ID of the pull request's target branch
        pull_request_id: ID of the pull request
        thread_id: ID of the thread that contains the comment
        comment_id: ID of the comment to delete

    Returns:
        A dictionary indicating success or containing error information
    """
    try:
        client = AzureDevOpsClient()

        # Delete the comment using the Git resource handler
        response = client.git.delete_pull_request_comment(
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            thread_id=thread_id,
            comment_id=comment_id,
        )

        # If we get here without an exception, the deletion was successful
        return {
            "success": True,
            "message": f"Successfully deleted comment {comment_id} from thread {thread_id} in PR {pull_request_id}",
        }

    except Exception as e:
        print(f"Error deleting pull request comment: {str(e)}")
        return {"success": False, "error": str(e)}


def update_pull_request_comment(
    repository_id: str,
    pull_request_id: int,
    thread_id: int,
    comment_id: int,
    content: str,
) -> Dict:
    """
    Update a comment associated with a specific thread in a pull request.

    This function modifies the content of an existing comment in a pull request thread.
    It's useful for correcting or enhancing feedback during code review processes.

    Args:
        repository_id: The repository ID of the pull request's target branch
        pull_request_id: ID of the pull request
        thread_id: ID of the thread that contains the comment
        comment_id: ID of the comment to update
        content: The new content for the comment

    Returns:
        A dictionary containing the updated comment information or error details
    """
    try:
        client = AzureDevOpsClient()

        # Update the comment using the Git resource handler
        response = client.git.update_pull_request_comment(
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            thread_id=thread_id,
            comment_id=comment_id,
            content=content,
        )

        # Process the response to make it more LLM-friendly
        result = {
            "id": response.get("id"),
            "content": response.get("content"),
            "author": response.get("author", {}).get("displayName"),
            "thread_id": thread_id,
            "pull_request_id": pull_request_id,
        }

        return result

    except Exception as e:
        print(f"Error updating pull request comment: {str(e)}")
        return {"error": str(e)}


def get_pull_request_details(
    pull_request_id: int,
    include_commits: bool = True,
    include_work_items: bool = False,
    include_work_item_details: bool = False,
) -> Dict:
    """
    Get detailed information about a specific pull request.

    Retrieves comprehensive information about a pull request including its metadata,
    associated commits (optional), and linked work items (optional). This is useful for
    analyzing specific PRs in detail, including their changes and relationships to work items.

    Args:
        pull_request_id: The ID of the pull request to retrieve
        include_commits: Whether to include commit information
        include_work_items: Whether to include associated work items
        include_work_item_details: Whether to include detailed work item information (title, description, acceptance criteria, etc.)

    Returns:
        Detailed information about the pull request including metadata and relationships
    """
    try:
        client = AzureDevOpsClient()

        # Get detailed PR information using the Git resource handler
        pr = client.git.get_pull_request_details(
            pull_request_id,
            include_commits,
            include_work_items,
        )

        # Process the PR details to make them more LLM-friendly
        if not pr:
            return {"error": "Pull request not found"}

        # Format the response in a LLM-friendly way
        result = {
            "id": pr.get("pullRequestId"),
            "title": pr.get("title"),
            "description": pr.get("description"),
            "created_by": pr.get("createdBy", {}).get("displayName"),
            "source_branch": pr.get("sourceRefName", "").replace("refs/heads/", ""),
            "target_branch": pr.get("targetRefName", "").replace("refs/heads/", ""),
            "repository": {
                "id": pr.get("repository", {}).get("id"),
                "name": pr.get("repository", {}).get("name"),
            },
        }

        # Add commits if included and available
        if include_commits and "commits" in pr:
            result["commits"] = [
                {
                    "commit_id": commit.get("commitId"),
                    "comment": commit.get("comment"),
                }
                for commit in pr.get("commits", [])
            ]

        # Add work items if included and available
        if include_work_items:
            try:
                # Extract the repository project ID which we might need
                project_id = pr.get("repository", {}).get("project", {}).get("id")

                if "artifactId" in pr:

                    artifact_parts = pr["artifactId"].split("/")
                    if len(artifact_parts) >= 3:
                        # Construct a direct endpoint to get work items
                        pr_id_part = artifact_parts[-1]
                        repo_id_part = artifact_parts[-2].replace("%2f", "/")

                        # Use this endpoint to fetch work items
                        try:
                            repository_id = pr.get("repository", {}).get("id")
                            endpoint = f"/{project_id}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/workitems"
                            work_items_response = client.git._client._make_request(
                                "GET", endpoint
                            )
                            work_item_refs = work_items_response.get("value", [])
                        except Exception as e:
                            print(
                                f"Could not fetch work items using direct endpoint: {str(e)}"
                            )
                            work_item_refs = []
                if not work_item_refs:
                    result["work_items"] = []
                    return result

                # Basic work item references (just IDs and URLs)
                if not include_work_item_details:
                    result["work_items"] = [
                        {"id": work_item.get("id"), "url": work_item.get("url")}
                        for work_item in work_item_refs
                    ]
                    return result

                # Enhanced work item details
                detailed_work_items = []

                for work_item_ref in work_item_refs:
                    work_item_id = work_item_ref.get("id")
                    if not work_item_id:
                        continue
                    try:
                        work_item_details = client.work_items.get(int(work_item_id))
                        fields = work_item_details.get("fields", {})

                        work_item_info = {
                            "title": fields.get("System.Title"),
                            "type": fields.get("System.WorkItemType"),
                            "state": fields.get("System.State"),
                        }

                        # Add description if available
                        if "System.Description" in fields:
                            work_item_info["description"] = fields.get(
                                "System.Description"
                            )
                        assigned_to = fields.get("System.AssignedTo")
                        if assigned_to:
                            if isinstance(assigned_to, dict):
                                work_item_info["assigned_to"] = assigned_to.get(
                                    "displayName"
                                )
                            else:
                                work_item_info["assigned_to"] = assigned_to

                        # Add acceptance criteria if available (for user stories)
                        if "Microsoft.VSTS.Common.AcceptanceCriteria" in fields:
                            work_item_info["acceptance_criteria"] = fields.get(
                                "Microsoft.VSTS.Common.AcceptanceCriteria"
                            )

                        # Add repro steps if available (for bugs)
                        if "Microsoft.VSTS.TCM.ReproSteps" in fields:
                            work_item_info["repro_steps"] = fields.get(
                                "Microsoft.VSTS.TCM.ReproSteps"
                            )

                        detailed_work_items.append(work_item_info)
                    except Exception as e:
                        # Just include the ID and error if we can't get details
                        detailed_work_items.append(
                            {
                                "id": work_item_id,
                                "error": f"Could not retrieve details: {str(e)}",
                            }
                        )

                result["work_items"] = detailed_work_items
            except Exception as e:
                print(f"Error handling work items: {str(e)}")
                result["work_items"] = []

        return result

    except Exception as e:
        print(
            f"Error retrieving PR details for PR {pull_request_id} in repository {repository_id}: {str(e)}"
        )
        return {"error": str(e)}


def get_project_pull_requests(
    project_id: str,
    status: str = "active",
    top: Optional[int] = None,
    skip: Optional[int] = None,
) -> List[Dict]:
    """
    Get pull requests for a specific project.

    Retrieves all pull requests for a given project matching the specified criteria.
    This is useful for getting an overview of ongoing work or reviewing recent PRs.

    Args:
        project_id: Project ID or name
        status: Filter by PR status ("active", "completed", "abandoned", or "all")
        top: Maximum number of pull requests to retrieve
        skip: Number of pull requests to skip (for pagination)

    Returns:
        List of pull requests with their details including title, description, creator, status, and related work items
    """
    try:
        client = AzureDevOpsClient()

        # Get pull requests using the Git resource handler
        pull_requests = client.git.get_project_pull_requests(
            project_id, status, top, skip
        )

        # Process the pull requests to make them more LLM-friendly
        result = []
        for pr in pull_requests:
            # Extract the most relevant information
            pr_info = {
                "id": pr.get("pullRequestId"),
                "title": pr.get("title"),
                "description": pr.get("description"),
                "status": pr.get("status"),
                "created_by": pr.get("createdBy", {}).get("displayName"),
                "creation_date": pr.get("creationDate"),
                "source_branch": pr.get("sourceRefName", "").replace("refs/heads/", ""),
                "target_branch": pr.get("targetRefName", "").replace("refs/heads/", ""),
                "repository": {
                    "id": pr.get("repository", {}).get("id"),
                    "name": pr.get("repository", {}).get("name"),
                },
                "url": pr.get("url"),
            }
            result.append(pr_info)

        return result
    except Exception as e:
        print(f"Error retrieving pull requests for project {project_id}: {str(e)}")
        return []


def update_pull_request(
    repository_id: str,
    pull_request_id: int,
    project_id: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    target_branch: Optional[str] = None,
    auto_complete: Optional[bool] = None,
    auto_complete_user_id: Optional[str] = None,
    delete_source_branch: Optional[bool] = None,
    merge_strategy: Optional[str] = None,
    merge_commit_message: Optional[str] = None,
) -> Dict:
    """
    Update an existing pull request with new information.

    This function allows you to modify various aspects of a pull request including its title,
    description, status, and completion options. It's useful for programmatically updating
    pull requests as they progress through the review cycle.

    Args:
        repository_id: The repository ID containing the pull request
        pull_request_id: ID of the pull request to update
        project_id: Optional project ID or name (can be omitted for some repositories)
        title: New title for the pull request
        description: New description for the pull request (max 4000 characters)
        status: New status ('active', 'abandoned', 'completed')
        target_branch: New target branch name (requires PR retargeting to be enabled)
        auto_complete: Whether to enable auto-complete for the PR
        auto_complete_user_id: ID of the user enabling auto-complete
        delete_source_branch: Whether to delete the source branch after completion
        merge_strategy: Strategy for merging the PR ('noFastForward', 'rebase', 'rebaseMerge', 'squash')
        merge_commit_message: Custom commit message for the merge



    Returns:
        Updated pull request information with status and any new changes applied
    """
    try:
        client = AzureDevOpsClient()

        # Set up completion options if any are provided
        completion_options = None
        if any(
            [
                delete_source_branch is not None,
                merge_strategy is not None,
                merge_commit_message is not None,
            ]
        ):
            completion_options = {}

            if delete_source_branch is not None:
                completion_options["deleteSourceBranch"] = delete_source_branch

            if merge_strategy is not None:
                completion_options["mergeStrategy"] = merge_strategy

            if merge_commit_message is not None:
                completion_options["mergeCommitMessage"] = merge_commit_message

        # Update the pull request using the Git resource handler
        updated_pr = client.git.update_pull_request(
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            project_id=project_id,
            title=title,
            description=description,
            status=status,
            target_ref_name=target_branch,
            completion_options=completion_options,
            auto_complete_set_by_id=auto_complete_user_id if auto_complete else None,
        )

        # Format the response in a more LLM-friendly way
        if not updated_pr:
            return {"error": "Failed to update pull request"}

        result = {
            "id": updated_pr.get("pullRequestId"),
            "title": updated_pr.get("title"),
            "description": updated_pr.get("description"),
            "status": updated_pr.get("status"),
            "source_branch": updated_pr.get("sourceRefName", "").replace(
                "refs/heads/", ""
            ),
            "target_branch": updated_pr.get("targetRefName", "").replace(
                "refs/heads/", ""
            ),
            "created_by": updated_pr.get("createdBy", {}).get("displayName"),
            "merge_status": updated_pr.get("mergeStatus"),
            "url": updated_pr.get("url"),
            "is_auto_complete": updated_pr.get("autoCompleteSetBy") is not None,
        }

        # Add completion options if present
        if "completionOptions" in updated_pr:
            result["completion_options"] = updated_pr.get("completionOptions")

        return result

    except Exception as e:
        print(f"Error updating pull request {pull_request_id}: {str(e)}")
        return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    repositories = get_repositories()
    if repositories:
        print("List of repositories:")
        for repo in repositories:
            print(f"- {repo['name']} (ID: {repo['id']})")

            # Get branches for this repository
            branches = get_repository_branches(repo["id"])
            if branches:
                print("  Branches:")
                for branch in branches:
                    # Extract branch name from the ref (e.g., "refs/heads/main" -> "main")
                    branch_name = branch["name"].replace("refs/heads/", "")
                    print(f"  - {branch_name}")

from langchain_core.messages import SystemMessage

from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode

import sys
import os

# Add the parent directory to sys.path to enable relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from tools.git_repositories import (
    get_pr_changes,
    get_pull_request_details,
    add_pull_request_comment,
    delete_pull_request_comment,
    update_pull_request_comment,
)


# Define the tools
tools = [
    get_pr_changes,
    add_pull_request_comment,
    get_pull_request_details,
    delete_pull_request_comment,
    update_pull_request_comment,
]

# Define LLM with bound tools
from langchain_openai import AzureChatOpenAI

from settings import AZURE_CONFIG

# Initialize the LLM
llm = AzureChatOpenAI(
    model=AZURE_CONFIG["model"],
    api_version=AZURE_CONFIG["api_version"],
    azure_deployment=AZURE_CONFIG["azure_deployment"],
    azure_endpoint=AZURE_CONFIG["azure_endpoint"],
    openai_api_key=AZURE_CONFIG["openai_api_key"],
)

llm_with_tools = llm.bind_tools(tools)

# System message
sys_msg = SystemMessage(
    content="""You are a senior software engineer responsible for conducting thorough code reviews on Azure DevOps pull requests.

When the user provides you with a PR ID, follow this process:

1. First use get_pull_request_details to retrieve the current PR information and most importantly the ID of the repository with include_work_items=True and include_work_item_details=True to understand the context of the changes

2. Then use get_pr_changes to analyze the code modifications in detail, examining:
   - File additions, modifications, and deletions
   - Changes in functionality and architecture
   - Potential impacts on existing code
   - Code quality and adherence to best practices

3. Act as a senior software engineer reviewer by adding precise, actionable comments directly on specific lines of code using add_pull_request_comment, focusing on:
   - Code quality issues (readability, maintainability)
   - Potential bugs or edge cases
   - Performance considerations
   - Security vulnerabilities
   - Documentation needs
   - Architecture and design patterns

Your comments should be:
- Specific and actionable (avoid vague feedback)
- Educational (explain why an approach is problematic)
- Constructive (suggest better alternatives)
- Respectful and professional (focus on the code, not the author)
- Brief but clear (no need for excessive explanation)

Attach comments to specific files and line numbers. For each issue, create a separate comment targeted to the exact line rather than bundling multiple issues into one comment.

Also provide general feedback on the overall PR quality as a general comment on the PR itself with a score between 0 and 10.

Ask the user for PR ID if they haven't provided them.

When you are done reviewing the PR, the user might ask for deleting a comment or updating a comment.

If the user asks for deleting a comment, use delete_pull_request_comment to delete the comment.

If the user asks for updating a comment, use update_pull_request_comment to update the comment.
"""
)


def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")

# Compile graph
graph = builder.compile()

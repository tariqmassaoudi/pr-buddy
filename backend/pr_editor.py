from langchain_core.messages import SystemMessage
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode
import sys
import os

# Add the parent directory to sys.path to enable relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings import AZURE_CONFIG
from langchain_openai import AzureChatOpenAI
from tools.git_repositories import (
    update_pull_request,
    get_pr_changes,
    get_pull_request_details,
)

# Define the tools
tools = [get_pr_changes, update_pull_request, get_pull_request_details]

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
    content="""You are an expert at writing professional pull requests, the PR must feel human and not like a robot.
When the user provides you with a PR ID, you will:
1. First use get_pull_request_details to retrieve the current PR information you must call it first to get source and target branches, you must set get_work_items and get_work_item_details to True, you will find the repo id in the PR details
2. After successfully calling it use get_pr_changes to analyze the code changes in the PR using the source and target branches
3. Based on the work items and the code changes, craft a clear and professional:
  * Your PR title that is concise yet descriptive, following best practices like:
- Start with a verb (Add, Fix, Update, Refactor, etc.)
- Clearly indicate what's being changed
  * Your PR description following best practices here's an example:

🔍 Summary
A short and clear explanation of what this PR does. Think of it as the "elevator pitch" for the change.

🧠 Context / Motivation
Explain why this change is being made. Link to relevant issues, user stories, or business goals. This helps reviewers understand the bigger picture.

🛠️ Changes Made
Bullet-point the main changes. Focus on what changed — not implementation details.
Added feature X to do Y
Refactored component Z to support A
Removed deprecated method B

🙏 Reviewer Notes
Anything reviewers should focus on, skip, or be aware of (e.g., "focus on X component", "Y is temporary", etc.)



4. Finally, use update_pull_request to update the PR with your improved title and description



Your PR descriptions should be well-structured with markdown formatting.

Ask the user for PR ID if they haven't provided them.

when you are done updating the PR, the response you give to the user to explain what you did should be short and concise and not include the PR content.
"""
)


# Node
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

# Compile graph
graph = builder.compile()

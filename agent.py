import os
import requests
import base64
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.genai import types


class GitHubClientError(Exception):
    """Custom exception for GitHub client errors"""
    pass


class GitHubAPIClient:
    """Enhanced GitHub API client with better error handling and logging"""
    
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('REPO_OWNER')
        self.repo_name = os.getenv('REPO_NAME')
        
        if not all([self.token, self.repo_owner, self.repo_name]):
            raise GitHubClientError(
                "Missing required environment variables. Please set GITHUB_TOKEN, REPO_OWNER, and REPO_NAME"
            )
        
        self.api_base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with consistent error handling"""
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            raise GitHubClientError(f"Request failed: {e}")
    
    def get_branch_sha(self, branch: str) -> str:
        """Gets the latest commit SHA of a given branch"""
        url = f"{self.api_base_url}/git/ref/heads/{branch}"
        response = self._make_request("GET", url)
        
        if response.status_code == 404:
            raise GitHubClientError(f"Branch '{branch}' not found")
        
        response.raise_for_status()
        return response.json()['object']['sha']


# Initialize GitHub client (with error handling for missing env vars)
try:
    github_client = GitHubAPIClient()
    CLIENT_INITIALIZED = True
except GitHubClientError as e:
    print(f"Warning: GitHub client initialization failed: {e}")
    github_client = None
    CLIENT_INITIALIZED = False


# Tool Functions for the AI Agent (Simplified for ADK compatibility)
def get_repository_info() -> str:
    """Get basic information about the configured repository"""
    if not CLIENT_INITIALIZED:
        return "Error: GitHub client not properly initialized. Please check your environment variables."
    
    try:
        url = github_client.api_base_url
        response = github_client._make_request("GET", url)
        response.raise_for_status()
        
        repo_data = response.json()
        info = {
            "name": repo_data.get("name"),
            "full_name": repo_data.get("full_name"),
            "description": repo_data.get("description"),
            "language": repo_data.get("language"),
            "stars": repo_data.get("stargazers_count"),
            "forks": repo_data.get("forks_count"),
            "default_branch": repo_data.get("default_branch")
        }
        
        return f"Repository Information: {json.dumps(info, indent=2)}"
    except Exception as e:
        return f"Error getting repository info: {str(e)}"


def create_new_branch(branch_name: str, base_branch: str) -> str:
    """Create a new branch from a base branch"""
    if not CLIENT_INITIALIZED:
        return "Error: GitHub client not properly initialized."
    
    try:
        base_sha = github_client.get_branch_sha(base_branch)
        
        url = f"{github_client.api_base_url}/git/refs"
        payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha
        }
        
        response = github_client._make_request("POST", url, json=payload)
        
        if response.status_code == 422:
            return f"Branch '{branch_name}' already exists or there was a validation error"
        
        response.raise_for_status()
        return f"Successfully created branch '{branch_name}' from '{base_branch}'"
        
    except Exception as e:
        return f"Error creating branch: {str(e)}"


def create_file_in_repository(file_path: str, content: str, branch: str) -> str:
    """Create a new file in the repository"""
    if not CLIENT_INITIALIZED:
        return "Error: GitHub client not properly initialized."
    
    try:
        commit_message = f"feat: Create {file_path}"
        
        url = f"{github_client.api_base_url}/contents/{file_path}"
        payload = {
            "message": commit_message,
            "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            "branch": branch
        }
        
        response = github_client._make_request("PUT", url, json=payload)
        response.raise_for_status()
        
        return f"Successfully created file '{file_path}' in branch '{branch}'"
        
    except Exception as e:
        return f"Error creating file: {str(e)}"


def create_file_with_custom_message(file_path: str, content: str, branch: str, commit_message: str) -> str:
    """Create a new file in the repository with a custom commit message"""
    if not CLIENT_INITIALIZED:
        return "Error: GitHub client not properly initialized."
    
    try:
        url = f"{github_client.api_base_url}/contents/{file_path}"
        payload = {
            "message": commit_message,
            "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            "branch": branch
        }
        
        response = github_client._make_request("PUT", url, json=payload)
        response.raise_for_status()
        
        return f"Successfully created file '{file_path}' in branch '{branch}' with message: {commit_message}"
        
    except Exception as e:
        return f"Error creating file: {str(e)}"


def update_file_in_repository(file_path: str, content: str, branch: str) -> str:
    """Update an existing file in the repository"""
    if not CLIENT_INITIALIZED:
        return "Error: GitHub client not properly initialized."
    
    try:
        commit_message = f"fix: Update {file_path}"
        
        # Get current file info
        url = f"{github_client.api_base_url}/contents/{file_path}"
        params = {'ref': branch}
        response = github_client._make_request("GET", url, params=params)
        
        if response.status_code == 404:
            return f"File '{file_path}' not found in branch '{branch}'"
        
        response.raise_for_status()
        current_sha = response.json()['sha']
        
        # Update file
        payload = {
            "message": commit_message,
            "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            "sha": current_sha,
            "branch": branch
        }
        
        update_response = github_client._make_request("PUT", url, json=payload)
        update_response.raise_for_status()
        
        return f"Successfully updated file '{file_path}' in branch '{branch}'"
        
    except Exception as e:
        return f"Error updating file: {str(e)}"


def update_file_with_custom_message(file_path: str, content: str, branch: str, commit_message: str) -> str:
    """Update an existing file in the repository with a custom commit message"""
    if not CLIENT_INITIALIZED:
        return "Error: GitHub client not properly initialized."
    
    try:
        # Get current file info
        url = f"{github_client.api_base_url}/contents/{file_path}"
        params = {'ref': branch}
        response = github_client._make_request("GET", url, params=params)
        
        if response.status_code == 404:
            return f"File '{file_path}' not found in branch '{branch}'"
        
        response.raise_for_status()
        current_sha = response.json()['sha']
        
        # Update file
        payload = {
            "message": commit_message,
            "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            "sha": current_sha,
            "branch": branch
        }
        
        update_response = github_client._make_request("PUT", url, json=payload)
        update_response.raise_for_status()
        
        return f"Successfully updated file '{file_path}' in branch '{branch}' with message: {commit_message}"
        
    except Exception as e:
        return f"Error updating file: {str(e)}"


def delete_file_from_repository(file_path: str, branch: str) -> str:
    """Delete a file from the repository"""
    if not CLIENT_INITIALIZED:
        return "Error: GitHub client not properly initialized."
    
    try:
        commit_message = f"refactor: Delete {file_path}"
        
        # Get current file info
        url = f"{github_client.api_base_url}/contents/{file_path}"
        params = {'ref': branch}
        response = github_client._make_request("GET", url, params=params)
        
        if response.status_code == 404:
            return f"File '{file_path}' not found in branch '{branch}'"
        
        response.raise_for_status()
        current_sha = response.json()['sha']
        
        # Delete file
        payload = {
            "message": commit_message,
            "sha": current_sha,
            "branch": branch
        }
        
        delete_response = github_client._make_request("DELETE", url, json=payload)
        delete_response.raise_for_status()
        
        return f"Successfully deleted file '{file_path}' from branch '{branch}'"
        
    except Exception as e:
        return f"Error deleting file: {str(e)}"


def read_file_content(file_path: str, branch: str) -> str:
    """Read the content of a file from the repository"""
    if not CLIENT_INITIALIZED:
        return "Error: GitHub client not properly initialized."
    
    try:
        url = f"{github_client.api_base_url}/contents/{file_path}"
        params = {'ref': branch}
        response = github_client._make_request("GET", url, params=params)
        
        if response.status_code == 404:
            return f"File '{file_path}' not found in branch '{branch}'"
        
        response.raise_for_status()
        
        file_data = response.json()
        if isinstance(file_data, list):
            return f"'{file_path}' is a directory, not a file"
        
        content = base64.b64decode(file_data['content']).decode('utf-8')
        return f"Content of '{file_path}':\n\n{content}"
        
    except Exception as e:
        return f"Error reading file: {str(e)}"


def create_pull_request(head_branch: str, base_branch: str, title: str, body: str) -> str:
    """Create a pull request"""
    if not CLIENT_INITIALIZED:
        return "Error: GitHub client not properly initialized."
    
    try:
        url = f"{github_client.api_base_url}/pulls"
        payload = {
            "title": title,
            "head": head_branch,
            "base": base_branch,
            "body": body
        }
        
        response = github_client._make_request("POST", url, json=payload)
        
        if response.status_code == 422:
            return f"Could not create PR. A PR from '{head_branch}' to '{base_branch}' may already exist or there's a validation error"
        
        response.raise_for_status()
        
        pr_data = response.json()
        pr_url = pr_data.get('html_url')
        pr_number = pr_data.get('number')
        
        return f"Successfully created Pull Request #{pr_number}: {pr_url}"
        
    except Exception as e:
        return f"Error creating pull request: {str(e)}"


def list_repository_branches() -> str:
    """List all branches in the repository"""
    if not CLIENT_INITIALIZED:
        return "Error: GitHub client not properly initialized."
    
    try:
        url = f"{github_client.api_base_url}/branches"
        response = github_client._make_request("GET", url)
        response.raise_for_status()
        
        branches = response.json()
        branch_names = [branch['name'] for branch in branches]
        
        return f"Repository branches: {', '.join(branch_names)}"
        
    except Exception as e:
        return f"Error listing branches: {str(e)}"


def get_commit_history(branch: str, limit: int) -> str:
    """Get recent commit history for a branch"""
    if not CLIENT_INITIALIZED:
        return "Error: GitHub client not properly initialized."
    
    try:
        url = f"{github_client.api_base_url}/commits"
        params = {
            'sha': branch,
            'per_page': min(limit, 50)  # Limit to max 50
        }
        response = github_client._make_request("GET", url, params=params)
        response.raise_for_status()
        
        commits = response.json()
        commit_info = []
        
        for commit in commits:
            commit_data = {
                "sha": commit['sha'][:7],
                "message": commit['commit']['message'].split('\n')[0][:60],
                "author": commit['commit']['author']['name'],
                "date": commit['commit']['author']['date']
            }
            commit_info.append(commit_data)
        
        return f"Recent commits in '{branch}':\n" + json.dumps(commit_info, indent=2)
        
    except Exception as e:
        return f"Error getting commit history: {str(e)}"


# Simple greeting function
def say_hello() -> str:
    """Simple greeting function"""
    return "Hello! I'm your GitHub Operations Agent. I can help you manage your GitHub repository. What would you like to do today?"


# Load model from environment
MODEL_NAME = os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp")

# Create the root_agent (this is what ADK is looking for!)
root_agent = Agent(
    name="github_operations_agent",
    model=MODEL_NAME,
    instruction="""
    You are GitHub Operations Agent, an AI-powered assistant that helps users manage GitHub repositories efficiently.
    
    You can perform the following operations:
    - Get repository information and statistics
    - Create, read, update, and delete files in repositories
    - Create and manage branches
    - Create pull requests
    - View commit history and branch information
    
    Always provide clear, informative responses about the operations performed.
    When working with files, ensure proper commit messages that follow conventional commit standards.
    For any errors, provide helpful guidance on how to resolve them.
    
    When users greet you, respond warmly and offer to help with GitHub operations.
    """,
    global_instruction=f"""
    You are GitHub Operations Agent - the ultimate GitHub repository management assistant.
    Current date: {datetime.now().strftime("%Y-%m-%d")}
    
    Environment Configuration Status: {"✅ Connected" if CLIENT_INITIALIZED else "❌ Not Connected"}
    {f"Repository: {github_client.repo_owner}/{github_client.repo_name}" if CLIENT_INITIALIZED else "Repository: Not configured"}
    
    Always be helpful, precise, and provide actionable information.
    If the GitHub client is not initialized, guide the user to check their environment variables.
    """,
    tools=[
        FunctionTool(say_hello),
        FunctionTool(get_repository_info),
        FunctionTool(create_new_branch),
        FunctionTool(create_file_in_repository),
        FunctionTool(create_file_with_custom_message),
        FunctionTool(update_file_in_repository),
        FunctionTool(update_file_with_custom_message),
        FunctionTool(delete_file_from_repository),
        FunctionTool(read_file_content),
        FunctionTool(create_pull_request),
        FunctionTool(list_repository_branches),
        FunctionTool(get_commit_history),
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,
        max_output_tokens=8192,
        top_p=0.8,
        top_k=40
    ),
)

# For backwards compatibility, also expose as github_operations_agent
github_operations_agent = root_agent

# Example usage and testing
if __name__ == "__main__":
    print("GitHub Operations Agent initialized successfully!")
    if CLIENT_INITIALIZED:
        print(f"Connected to repository: {github_client.repo_owner}/{github_client.repo_name}")
    else:
        print("Warning: GitHub client not initialized. Please check environment variables.")
    
    # Test the agent
    print("\nAgent ready for deployment with ADK!")
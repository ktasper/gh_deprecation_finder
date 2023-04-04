"""
Deals with Github Action (workflow) files
"""

from github import UnknownObjectException, Repository, GithubException


def has_workflow(repo: Repository) -> list:
    """
    Determine if we have a workflow directory in the repo
    """
    try:
        repo_workflows = repo.get_contents(".github/workflows")
    except UnknownObjectException:
        repo_workflows = None
    except GithubException as ex:
        print(f"Error accessing {repo.full_name}: {str(ex)}")
        repo_workflows = None
    return repo_workflows

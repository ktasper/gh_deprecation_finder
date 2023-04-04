"""
Deals with fetching repos
"""
import logging
import os
from rich import print as rprint
from github import Github, BadCredentialsException, UnknownObjectException, Repository
from .workflows import has_workflow
from .deprecations import find_deprecations


def get_workflows(
    repo_name: str,
    org_name: str,
    github: Github,
    config_file: str,
    logger: logging.Logger,
) -> list[dict]:
    """
    Retrieves all the workflows in '.github/workflows
    As long as they have yaml or yml file extension and passes
    them to the find_deprecations function.

    Returns a list of dicts of each deprecation if found.
    """
    # Initialize a PyGithub object with your access token
    repo: Repository = get_repo(repo_name=repo_name, org_name=org_name, github=github)
    results = []
    if repo:
        logger.debug("Repo Full Name: %s", repo.full_name)
        # Check if it has workflows
        workflows: list = has_workflow(repo=repo)
        if workflows:
            for contents in workflows:
                # Check all the files in the workflow folder
                if contents.name.endswith(".yml") or contents.name.endswith(".yaml"):
                    # Print all the yaml files we have found
                    logger.debug("File found %s", contents.path)
                    # Set a path to write the temp files
                    workflow_path: str = os.path.join(os.getcwd(), "temp-workflow.yml")
                    with open(workflow_path, "w", encoding="utf-8") as file:
                        logger.debug(f"Writing {contents.path} to {workflow_path}")
                        file.write(contents.decoded_content.decode())
                    # Run find_deprecations on the saved file
                    deprecations = find_deprecations(
                        file_path="temp-workflow.yml",
                        workflow_name=contents.name,
                        config_file=config_file,
                        logger=logger,
                    )
                    results.append(deprecations)
    return results


def get_repo(repo_name: str, org_name: str, github: Github) -> Repository:
    """
    Checks we can access the github repo and fetches it
    """
    # Attempt to get the repo from the org
    try:
        logging.debug("Checking access to %s", repo_name)
        repo_to_check = github.get_organization(org_name).get_repo(repo_name)
    except BadCredentialsException:
        logging.debug("Access to %s: BadCredentials", repo_name)
        rprint("[red]Invalid Credentials [/red] :cross_mark:")
        repo_to_check = None
    except UnknownObjectException:
        logging.debug("Other Error, probably cant find the repo")
        rprint(
            """
            [red]Cannot find repo:
            Please check the given org is correct
            and you have the right repo [/red] :cross_mark:
            """
        )
        repo_to_check = None
    return repo_to_check


def get_all_repos(org_name: str, github: Github) -> list:
    """
    Checks we can access all repos in the org and fetches it
    """
    try:
        logging.debug("Checking access to %s", org_name)
        org = github.get_organization(org_name)
        repos = list(org.get_repos())
    except BadCredentialsException:
        logging.debug("Access to %s: BadCredentials", org_name)
        rprint("[red]Invalid Credentials [/red] :cross_mark:")
        repos = None
    except UnknownObjectException:
        logging.debug("Other Error, probably cant find the repo")
        rprint(
            """
            [red]Cannot find repo:
            Please check the given org is correct
            and you have the right repo [/red] :cross_mark:
            """
        )
        repos = None
    return repos

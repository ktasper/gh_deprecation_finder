"""
The main entry point to the app
"""
import logging
import sys
import typer
from github import Github
from rich import print as rprint
from rich.table import Table
from .repo import get_workflows, get_all_repos


# Setup Typer App
app = typer.Typer()
# Create a logger
logger = logging.getLogger(__name__)


def setup_logger(log_level: str):
    """
    Sets up a logger to be passed into the typer callback
    """
    logger.setLevel(getattr(logging, log_level.upper()))

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@app.callback()
def callback(
    ctx: typer.Context,
    log_level: str = typer.Option(
        "INFO", "--log-level", "-l", help="Set logging level"
    ),
):
    """
    Callback Function
    """
    setup_logger(log_level)
    ctx.obj = {"logger": logger}


@app.command()
def find(
    ctx: typer.Context,
    access_token: str = typer.Option("", envvar="GH_ACCESS_TOKEN"),
    org_name: str = typer.Option("", envvar="GH_ORG_NAME"),
    config_file: str = typer.Option("config.ini"),
    repo_name: str = typer.Argument(...),
):
    """
    Finds github actions with deprecated items
    """
    ctx_logger = ctx.obj["logger"]
    ctx_logger.debug("Access Token = %s", {access_token})
    ctx_logger.debug("Org Name = %s", org_name)
    # Setup Github Access
    github: Github = Github(access_token)
    # Create a list to store all the repo deprecations
    all_deprecations = []
    # Create a dict with the repo name to store the repos deprecations
    repo_deprecations = {}
    workflow_deprecations = get_workflows(
        repo_name=repo_name,
        org_name=org_name,
        github=github,
        config_file=config_file,
        logger=ctx_logger,
    )
    repo_deprecations[repo_name] = workflow_deprecations
    # Add the dict with the repo deprecations to a the main list
    all_deprecations.append(repo_deprecations)

    pretty_print(all_deprecations)


@app.command()
def find_all(
    ctx: typer.Context,
    access_token: str = typer.Option("", envvar="GH_ACCESS_TOKEN"),
    org_name: str = typer.Option("", envvar="GH_ORG_NAME"),
    config_file: str = typer.Option("config.ini"),
):
    """
    Finds all github actions with deprecated items from ALL repos in the org
    """
    # Logging Config
    ctx_logger = ctx.obj["logger"]
    ctx_logger.debug("Access Token = %s", {access_token})
    ctx_logger.debug("Org Name = %s", org_name)
    # Setup Github Access
    github: Github = Github(access_token)
    # Get all the repos from the org
    repos = get_all_repos(org_name=org_name, github=github)
    repo_list: list = [repo.full_name.replace(f"{org_name}/", "") for repo in repos]
    # Create a list to store all the deprecations we find
    all_deprecations = []
    for repo in repo_list:
        # Create a dict with the repo name to store the repos deprecations
        repo_deprecations = {}
        workflow_deprecations = get_workflows(
            repo_name=repo,
            org_name=org_name,
            github=github,
            config_file=config_file,
            logger=ctx_logger,
        )
        repo_deprecations[repo] = workflow_deprecations
        # Add the dict with the repo deprecations to a the main list
        all_deprecations.append(repo_deprecations)
    pretty_print(all_deprecations)


def pretty_print(all_deprecations: list):
    """
    Prints out single repo deprecations in a nice format
    """
    table = Table(title="List of Deprecated Github Actions")
    table.add_column("Repo")
    table.add_column("File Name")
    table.add_column("Deprecated Item Type")
    table.add_column("Command(s)")

    for repo_data in all_deprecations:
        for repo, deprecations in repo_data.items():
            for item in deprecations:
                for file_name, file_data in item.items():
                    table.add_row(
                        repo,
                        file_name,
                        file_data["deprecated_item_type"],
                        file_data["command"],
                    )
    rprint(table)

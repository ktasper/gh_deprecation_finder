"""
Implements the deprecation finder logic
"""
import logging
import configparser
import yaml


def find_deprecations(
    file_path: str, workflow_name: str, config_file: str, logger: logging.Logger
) -> dict:
    """
    Finds deprecations or run commands that we wish to be notified about,
    returns a dict containing the file_name, deprecated item type, command that is causing it
    """
    config = configparser.ConfigParser()
    logger.debug("Reading %s", config_file)
    config.read(config_file)
    deprecated_actions = config.get("actions", "deprecated").split(",")
    command_list = config.get("commands", "list").split(",")
    deprecations = {}
    workflow = None
    with open(file_path, "r", encoding="utf-8") as stream:
        try:
            workflow = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logging.debug(exc)
    if workflow:
        logger.debug("Workflow contains valid yaml")
        # Typical format is a workflow can have many jobs each containing
        # multiple steps, so lets loop over the jobs, steps.
        # Some steps will have a "run" or a "uses" we want to check both.
        for job in workflow.get("jobs", {}).values():
            for step in job.get("steps", []):
                if "run" in step:
                    for line in step["run"].split("\n"):
                        if any(cmd in line for cmd in command_list):
                            logger.debug(f"Deprecated `command` Found {line}")
                            deprecations[workflow_name] = {
                                "deprecated_item_type": "run",
                                "command": line,
                            }
                if "uses" in step:
                    if any(action in step["uses"] for action in deprecated_actions):
                        logger.debug(f'Deprecated `uses` Found {step["uses"]}')
                        deprecations[workflow_name] = {
                            "deprecated_item_type": "uses",
                            "command": step["uses"],
                        }
    return deprecations

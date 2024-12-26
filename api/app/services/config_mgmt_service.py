"""
Module: config_loader
======================
This module provides functionality for loading application configuration
from a JSON file. The configuration file contains application-specific
settings such as database connection strings, logging directories, 
and other parameters.

Constants:
----------
CONFIG_FILE : str
    The name of the configuration file to be loaded.
"""

import json
import os

def load_config(scope_name: str):
    """
    Dynamically load configuration for a given scope.

    This function retrieves configuration settings from a JSON file based on the specified scope name.
    The configuration files are expected to follow the naming convention <scope_name>_config.json and 
    reside in a `config` directory relative to the script's location.

    Args:
    -----
    scope_name : str
        The name of the configuration scope (e.g., 'base', 'admin', 'log', 'features', etc.).

    Raises:
    -------
    FileNotFoundError
        If the configuration file for the given scope does not exist.
    JSONDecodeError
        If the configuration file contains invalid JSON.

    Returns:
    --------
    dict
        A dictionary containing the parsed configuration settings.

    Example:
    --------
    To load the base configuration:
        config = load_config("base")

    Expected file structure:
    ------------------------
    - config/
        - base_config.json
        - admin_config.json
        - log_config.json
        - features_config.json

    Notes:
    ------
    - Ensure that all configuration files follow the naming convention <scope_name>_config.json.
    - This function does not validate the structure or contents of the configuration file. For validation, 
      consider using a schema validation library such as `jsonschema` or `pydantic`.
    """
    config_file = f"{scope_name}_config.json"
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", config_file)
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file '{config_file}' not found in 'config' directory.")
    
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)

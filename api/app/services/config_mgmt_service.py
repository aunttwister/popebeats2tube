"""
Module: config_loader
======================
This module provides functionality for loading and caching the application's configuration
settings. The configuration is loaded from a JSON file and made globally accessible to 
prevent redundant file reads and improve performance.

Features:
---------
- Load application configuration from a JSON file.
- Cache the configuration after the first load to ensure it is only read from disk once.

Global Variables:
-----------------
_config : dict or None
    A cached dictionary containing the application configuration settings. This is initially
    set to None and populated when the `load_config` function is called.

Notes:
------
- The configuration file must be named `config.json` and reside in a `config` directory 
  one level above the module's location.
- If the configuration file is missing or contains invalid JSON, appropriate exceptions 
  will be raised.
"""

import json
import os

_config = None  # Global variable to cache the configuration

def load_config():
    """
    Load the application configuration once and cache it.

    This function loads the application's configuration settings from a JSON file located in the 
    `config` directory. The configuration is cached in a global variable to prevent redundant 
    file reads and ensure consistent settings across the application.

    Returns:
    --------
    dict
        A dictionary containing the parsed configuration settings.

    Raises:
    -------
    FileNotFoundError
        If the configuration file is not found in the `config` directory.
    JSONDecodeError
        If the configuration file contains invalid JSON.

    Notes:
    ------
    - The configuration file must be named `config.json` and reside in a directory named `config`
      located one level above the module's location.
    - Subsequent calls to this function will return the cached configuration.

    Example:
    --------
    >>> config = load_config()
    >>> print(config["database"]["connection_string"])
    """
    global _config
    if _config is not None:
        return _config

    config_file = "config.json"
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", config_file)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file '{config_file}' not found in 'config' directory.")

    with open(config_path, "r", encoding="utf-8") as file:
        _config = json.load(file)

    return _config

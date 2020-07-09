"""
config.py - mcadminbot configuration handling.

load_config is executed by the entrypoint to load defaults.yaml and then either:
    1. If a config path is passed via --config, merge it and return.
    2. Load and merge config from CONFIG_LOCATIONS in order of importance, then return.

Config is stored in the module variable CONFIG which can be accessed via config.CONFIG
    in other modules.
"""

import pathlib
from yaml import load, FullLoader


class McadminbotConfigPermissionsError(Exception):
    """Thrown when a config file cannot be opened to read."""

    def __init__(self, message):
        """
        Instantiate an instance of McadminbotConfigPermissionsError.

        Args:
            message: The exception message.
        """
        self.message = message
        super().__init__(self.message)


CONFIG_LOCATIONS = [
    pathlib.Path('/etc/mcadminbot/mcadminbot.yaml'),
    pathlib.Path(pathlib.Path.home() / 'mcadminbot.yaml')
]

CONFIG = {}


def load_config(config_path: str = None) -> None:
    """
    Load and merge the config for mcadminbot.

    Args:
        config_path: The user-supplied path to a config file.

    Raises:
        McadminbotConfigPermissionsError: No read permissions on file.
        FileNotFoundError: File does not exist at user-supplied path.
    """
    global CONFIG

    # Load the defaults first to ensure no missing config values
    parent_dir = pathlib.Path(__file__).parent
    default_path = parent_dir / 'defaults.yaml'
    try:
        with default_path.open('r') as default_config_file:
            CONFIG = load(default_config_file.read(), Loader=FullLoader)
    except PermissionError as error:
        raise McadminbotConfigPermissionsError(
            f"No read permissions to default config file [{default_path.absolute()}].") from error

    # Merge a config file specified on the command line and return
    if config_path:
        path = pathlib.Path(config_path)
        if path.exists():
            try:
                with path.open('r') as config_file:
                    to_merge = load(config_file.read(), Loader=FullLoader)
                CONFIG.update(to_merge)
            except PermissionError as error:
                raise McadminbotConfigPermissionsError(
                    f"No read permissions to config file [{path}].") from error
            return
        else:
            raise FileNotFoundError(
                f"No config file found at {config_path.absolute()}")

    # Merge config files in order of importance
    for path in CONFIG_LOCATIONS:
        if path.exists():
            try:
                with path.open('r') as config_file:
                    to_merge = load(config_file.read(), Loader=FullLoader)
                CONFIG.update(to_merge)
            except PermissionError as error:
                raise McadminbotConfigPermissionsError(
                    f"No read permissions to config file [{path.absolute()}].") from error

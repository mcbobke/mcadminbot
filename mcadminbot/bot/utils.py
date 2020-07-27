"""
bot/utils.py - common utility functions used by other bot-related modules
"""

import mctools
import re
from loguru import logger
from typing import List

import mcadminbot.config as config
from . import exceptions

# https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python


def ansi_escape(dirty_string: str) -> str:
    """
    Uses a regex to remove any ANSI escape sequence characters from a string.

    Args:
        dirty_string: The string to clean.

    Returns:
        The cleaned string.
    """
    ansi_escape_regex = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape_regex.sub('', dirty_string)


def rcon_command(command: str) -> str:
    """
    Connects to the configured Minecraft server's RCON server and executes the provided command.

    Args:
        command: The command to run on the Minecraft server.

    Returns:
        The response from the RCON server or a notification of connection failure.
    """
    rcon = mctools.RCONClient(
        config.CONFIG['server_address'], config.CONFIG['rcon_port'])

    try:
        success = rcon.login(config.CONFIG['rcon_password'])
    except ConnectionResetError:
        response = 'The RCON server is unreachable.'
        logger.error(response)
        rcon.stop()
        return response

    if success:
        response = ansi_escape(rcon.command(command))
    else:
        response = 'RCON authentication failed. Please check your RCON password in your config.'
        logger.error(response)
    rcon.stop()
    return response


def is_admin(username: str, user_roles: List[str]) -> bool:
    """
    Checks to see if a Discord user is configured as an administrator
    of the configured Minecraft server targeted by a command.

    Admin status is granted by the username being included in the
    'admin_users' list or if one of the user's roles is included
    in the 'admin_roles' list.

    Args:
        username: The Discord username that ran a command.
        user_roles: The roles of the Discord user that ran a command.

    Returns:
        True if the user is an admin, False if not.
    """
    if 'ALL' in config.CONFIG['admin_users'] or 'ALL' in config.CONFIG['admin_roles']:
        return True
    elif username in config.CONFIG['admin_users']:
        return True
    else:
        return not set(user_roles).isdisjoint(set(config.CONFIG['admin_roles']))

def permission_check(ctx) -> bool:
    """
    Checks the module config for permissions granted to a user based on
    username or their roles.

    Returns:
        True or False for permission granted or denied in the config file.

    Raises:
        McadminbotCommandPermissionsError: The user that tried to run
            the command does not have permission to do so.
    """
    if is_admin(ctx.author.name, ctx.author.roles):
        return True

    if ctx.invoked_subcommand:
        # Top-level command check returned true, so permission granted
        return True
    else:
        if 'ALL' in config.CONFIG[f"{ctx.command}_allowed_users"]:
            return True
        elif 'ALL' in config.CONFIG[f"{ctx.command}_allowed_roles"]:
            return True
        elif ctx.author.name in config.CONFIG[f"{ctx.command}_allowed_users"]:
            return True
        elif not set(ctx.author.roles).isdisjoint(
                set(config.CONFIG[f"{ctx.command}_allowed_users"])
        ):
            return True
        else:
            logger.warning(
                f"{ctx.author.name} does not have permission to run [{ctx.command}]")
            raise exceptions.McadminbotCommandPermissionsError(
                f"{ctx.author.name} does not have permission to run that command.")

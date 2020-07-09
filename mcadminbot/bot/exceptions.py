"""
bot/exceptions.py - Contains all core mcadminbot exceptions.
"""

from discord.ext import commands

class McadminbotConfigError(Exception):
    """Thrown when an error occurs because of a config value."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class McadminbotCommandPermissionsError(commands.CheckFailure):
    """Thrown when a user does not have permission to run a command."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

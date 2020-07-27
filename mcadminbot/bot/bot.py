"""
bot/bot.py - The core module of Mcadminbot.

run_bot instantiates an instance of Mcadminbot and runs the bot.
"""

import discord
from discord.ext import commands
from loguru import logger

import mcadminbot.config as config
from . import exceptions
from . import minecraftcommands
from . import systemcommands

class McadminbotHelp(commands.help.DefaultHelpCommand):
    """
    A subclass of discord.ext.commands.help.DefaultHelpCommand
    that disables checks for commands when asking for help.
    """

    def __init__(self):
        """
        Ensures that the verify_checks attribute of the parent
        DefaultHelpCommand is False.
        """
        super().__init__(verify_checks=False)

class Mcadminbot(commands.Bot):
    """A subclass of discord.ext.commands.Bot that is the core bot."""

    def __init__(self):
        """
        Instantiates an instance of Mcadminbot.

        Loads any accompanying cogs.

        Raises:
            McadminbotConfigError: A command prefix was not specified.
        """
        try:
            super().__init__(
                command_prefix=config.CONFIG['command_prefix'],
                help_command=McadminbotHelp()
                )
        except KeyError as error:
            raise exceptions.McadminbotConfigError(
                "'command_prefix' not specified in the config.") from error

        self.add_cog(minecraftcommands.MinecraftCommands(self))
        self.add_cog(systemcommands.SystemCommands(self))

    async def on_ready(self) -> None:
        """
        Overrides the discord.ext.commands.Bot on_ready method.

        Logs a message on successful connection to Discord.
        """
        logger.info(f"{self.user.name} has connected to Discord!")
        activity = discord.Activity(
            name='Minecraft commands',
            type=discord.ActivityType.listening
        )
        await self.change_presence(activity=activity)


def run_bot() -> None:
    """
    Creates and starts an instance of Mcadminbot.

    Raises:
        McadminbotConfigError: An invalid Discord token was provided.
    """
    bot = Mcadminbot()

    try:
        bot.run(config.CONFIG['token'])
    except discord.LoginFailure as error:
        raise exceptions.McadminbotConfigError(
            f"Your Discord token [{config.CONFIG['token']}] is invalid") from error

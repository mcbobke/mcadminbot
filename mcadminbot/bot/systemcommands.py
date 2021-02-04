"""
bot/systemcommands.py - Implements a discord.ext.commands.Cog to organize and
    expose system commands to users of the bot.
"""

import subprocess
from discord.ext import commands
from loguru import logger

import mcadminbot.config as config
from . import exceptions
from . import utils
from . import __version__


class SystemCommands(commands.Cog):
    """A subclass of discord.ext.commands.Cog that implements system commands."""

    def __init__(self, bot: commands.Bot):
        """
        Instantiates an instance of this cog to be used by Mcadminbot.

        Args:
            bot: An instance of discord.ext.commands.Bot.
        """
        self.bot = bot
        self.restarting = False
        self.restarting_user = None

    def cog_check(self, ctx) -> bool:
        """
        Overrides discord.ext.commands.Cog.cog_check.

        Provides a global check in this cog for permission to run a command.

        Returns:
            True or False for permission granted or denied.
        """
        return utils.permission_check(ctx)

    # Global cog command error handler for general errors
    async def cog_command_error(self, ctx, error: Exception) -> None:
        """
        Overrides discord.ext.commands.Cog.cog_command_error.

        Provides a global command error handler in this cog for any errors thrown
        inside a command or check.

        Args:
            error: The Exception that was thrown by the cog command.
        """
        if isinstance(error, exceptions.McadminbotCommandPermissionsError):
            await ctx.send(error)

    @commands.command(
        name='show-bot-info',
        help='Send bot information to the Discord channel it was requested from.'
    )
    async def show_bot_info(self, ctx) -> None:
        """
        Sends bot information to the Discord channel it was requested from.
        """
        logger.info(f"Bot info requested by user [{ctx.author.name}]")
        await ctx.send(f"mcadminbot version {__version__}")

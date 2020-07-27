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
        name='restart-docker-server',
        help='Restart the Docker container running the Minecraft server'
    )
    async def restart_docker_server(self, ctx) -> None:
        """
        Restarts the configured Docker container that is running the configured Minecraft server.
        """
        logger.info(
            f"restart-docker-server command received from user [{ctx.author.name}]")
        if not self.restarting:
            self.restarting = True
            self.restarting_user = ctx.author.name
            logger.info(
                "restart-docker-server command from user "
                f"[{self.restarting_user}] being processed now"
            )
            await ctx.send(
                f"Restarting the server per instruction of user [{self.restarting_user}].")
        else:
            logger.warning(
                "restart-docker-server aborted, "
                f"[{self.restarting_user}] is already running that command"
            )
            await ctx.send(f"User [{self.restarting_user}] is already running that command.")
            return

        async with ctx.typing():
            try:
                stop_result = subprocess.run(
                    ['docker', 'container', 'stop', config.CONFIG['docker_container_name']],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except OSError as error:
                logger.error(
                    f"os error during 'docker container stop' ({error})")
                await ctx.send(
                    f"The command [{' '.join(stop_result.args)}] could not be run: {error}")
                self.restarting = False
                self.restarting_user = None
                return

            if stop_result.returncode == 0:
                logger.info(
                    f"container [{config.CONFIG['docker_container_name']}] stopped")
                await ctx.send('The Minecraft server was stopped.')

                try:
                    start_result = subprocess.run(
                        ['docker', 'container', 'start', config.CONFIG['docker_container_name']],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except OSError as error:
                    logger.error(
                        f"os error during 'docker container start' ({error})")
                    await ctx.send(
                        f"The command [{' '.join(stop_result.args)}] could not be run: {error}")
                    self.restarting = False
                    self.restarting_user = None
                    return

                if start_result.returncode == 0:
                    logger.info(
                        f"container [{config.CONFIG['docker_container_name']}] started")
                    await ctx.send('The Minecraft server was started.')
                else:
                    logger.error(
                        f"failed to start container [{config.CONFIG['docker_container_name']}] "
                        f"({start_result.stderr})"
                    )
                    await ctx.send(
                        "Something went wrong starting the Minecraft server: "
                        f"{start_result.stderr}.")
            else:
                logger.error(
                    f"failed to stop container [{config.CONFIG['docker_container_name']}] "
                    f"({stop_result.stderr})"
                )
                await ctx.send(
                    "Something went wrong stopping the Minecraft server: "
                    f"{stop_result.stderr}."
                )

        self.restarting = False
        self.restarting_user = None

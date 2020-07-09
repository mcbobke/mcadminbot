"""
bot/systemcommands.py - Implements a discord.ext.commands.Cog to organize and
    expose system commands to users of the bot.
"""

import subprocess
from typing import List
from discord.ext import commands
from loguru import logger

from . import exceptions
import mcadminbot.config as config


def _is_admin(username: str, user_roles: List[str]) -> bool:
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

        Raises:
            McadminbotCommandPermissionsError: The user that tried to run
                the command does not have permission to do so.
        """
        if _is_admin(ctx.author.name, ctx.author.roles):
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
                logger.warning(f"{ctx.author.name} does not have permission to run [{ctx.command}]")
                raise exceptions.McadminbotCommandPermissionsError(
                    f"{ctx.author.name} does not have permission to run that command.")

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
                logger.error(f"os error during 'docker container stop' ({error})")
                await ctx.send(
                    f"The command [{' '.join(stop_result.args)}] could not be run: {error}")
                self.restarting = False
                self.restarting_user = None
                return

            if stop_result.returncode == 0:
                logger.info(f"container [{config.CONFIG['docker_container_name']}] stopped")
                await ctx.send('The Minecraft server was stopped.')

                try:
                    start_result = subprocess.run(
                        ['docker', 'container', 'start', config.CONFIG['docker_container_name']],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except OSError as error:
                    logger.error(f"os error during 'docker container start' ({error})")
                    await ctx.send(
                        f"The command [{' '.join(stop_result.args)}] could not be run: {error}")
                    self.restarting = False
                    self.restarting_user = None
                    return

                if start_result.returncode == 0:
                    logger.info(f"container [{config.CONFIG['docker_container_name']}] started")
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

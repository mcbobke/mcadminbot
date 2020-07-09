"""
bot/botcommands.py - Implements a discord.ext.commands.Cog to organize and
    expose Minecraft RCON commands to users of the bot.
"""

import mctools
import re
from discord.ext import commands
from typing import List
from loguru import logger

import mcadminbot.config as config
from . import exceptions

# Helper functions

# https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python


def _ansi_escape(dirty_string: str) -> str:
    """
    Uses a regex to remove any ANSI escape sequence characters from a string.

    Args:
        dirty_string: The string to clean.

    Returns:
        The cleaned string.
    """
    ansi_escape_regex = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape_regex.sub('', dirty_string)


def _rcon_command(command: str) -> str:
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
        response = _ansi_escape(rcon.command(command))
    else:
        response = 'RCON authentication failed. Please check your RCON password in your config.'
        logger.error(response)
    rcon.stop()
    return response


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


# Command Checks

# Anything defined here must be a coroutine and only have ctx as a parameter
# Register it with a command below using @commands.check(check_method_name)


# async def list_allowed(ctx):
#     if is_admin(ctx.author.name, ctx.author.roles):
#         return True
#     elif ctx.author.name in config.CONFIG[f"{ctx.command}_allowed_users"]:
#         return True
#     elif not set(ctx.author.roles).isdisjoint(set(config.CONFIG[f"{ctx.command}_allowed_users"])):
#         return True
#     else:
#         raise exceptions.McadminbotCommandPermissionsError(
#             f"{ctx.author.name} does not have permission to run that command.")


class McadminbotCommands(commands.Cog):
    """A subclass of discord.ext.commands.Cog that implements Minecraft RCON commands."""

    def __init__(self, bot: commands.Bot):
        """
        Instantiates an instance of this cog to be used by Mcadminbot.

        Args:
            bot: An instance of discord.ext.commands.Bot.
        """
        self.bot = bot

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

    @commands.command(help='List all online players')
    async def list(self, ctx) -> None:
        """Lists all players logged in to the configured Minecraft server."""
        logger.info(f"[{ctx.author.name}] is listing connected players")
        response = _rcon_command('list')
        await ctx.send(response)

    @commands.command(
        help='Send a message to every online player (surround the message with double quotes)'
    )
    async def say(self, ctx, message: str) -> None:
        """
        Broadcasts a message to all players logged in to the configured Minecraft server.

        Args:
            message: The message to send to players.
        """
        logger.info(f"[{ctx.author.name}] is broadcasting message [{message}]")
        _rcon_command(f"say {message}")
        await ctx.send(f"Message [{message}] sent")

    @commands.command(
        help='Send a private message to an online player (surround the message with double quotes)',
        aliases=['msg', 'w']
    )
    async def tell(self, ctx, username: str, message: str) -> None:
        """
        Sends a private message to a single player logged in to the configured Minecraft server.

        Args:
            username: The user to send a message to.
            message: The message to send.
        """
        logger.info(f"[{ctx.author.name}] is sending message [{message}] to player [{username}]")
        _rcon_command(f"tell {username} {message}")
        await ctx.send(f"Message [{message}] sent to player [{username}]")

    @commands.group(help='Whitelist commands')
    async def whitelist(self, ctx) -> None:
        """Top-level whitelist command that depends on subcommands."""
        if ctx.invoked_subcommand is None:
            if ctx.subcommand_passed:
                await ctx.send(f"Wrong subcommand: {ctx.subcommand_passed}")
            else:
                await ctx.send("See help for 'whitelist' command for list of valid subcommands")

    @whitelist.command(name='list', help='List players on the whitelist')
    async def whitelist_list(self, ctx) -> None:
        """List all players whitelisted on the configured Minecraft server."""
        logger.info(f"[{ctx.author.name}] is listing whitelisted players")
        response = _rcon_command('whitelist list')
        await ctx.send(response)

    @whitelist.command(name='add', help='Add a player to the whitelist')
    async def whitelist_add(self, ctx, username: str) -> None:
        """
        Add a player to the whitelist of the configured Minecraft server.

        Args:
            username: The Minecraft username of the player to whitelist.
        """
        logger.info(f"[{ctx.author.name}] is whitelisting Minecraft player [{username}]")
        response = _rcon_command(f"whitelist add {username}")
        await ctx.send(response)

    @whitelist.command(name='off', help='Turn the whitelist off')
    async def whitelist_off(self, ctx) -> None:
        """Turns off the whitelist for the configured Minecraft server."""
        logger.info(f"[{ctx.author.name}] is turning off the whitelist")
        response = _rcon_command('whitelist off')
        await ctx.send(response)

    @whitelist.command(name='on', help='Turn the whitelist on')
    async def whitelist_on(self, ctx) -> None:
        """Turns on the whitelist for the configured Minecraft server."""
        logger.info(f"[{ctx.author.name}] is turning on the whitelist")
        response = _rcon_command('whitelist on')
        await ctx.send(response)

    @whitelist.command(name='reload', help='Reloads the whitelist')
    async def whitelist_reload(self, ctx) -> None:
        """Reloads the whitelist for the configured Minecraft server."""
        logger.info(f"[{ctx.author.name}] is reloading the whitelist")
        response = _rcon_command('whitelist reload')
        await ctx.send(response)

    @whitelist.command(name='remove', help='Removes a player from the whitelist')
    async def whitelist_remove(self, ctx, username: str) -> None:
        """
        Removes a player from the whitelist for the configured Minecraft server.

        Args:
            username: The Minecraft username of the player to remove.
        """
        logger.info(
            f"[{ctx.author.name}] is removing Minecraft player [{username}] from the whitelist"
            )
        response = _rcon_command(f"whitelist remove {username}")
        await ctx.send(response)

    @commands.command(help='Ban a player from the server (surround the reason in double quotes)')
    async def ban(self, ctx, username: str, reason: str) -> None:
        """
        Bans a player from the configured Minecraft server.

        Args:
            username: The Minecraft username of the player to ban.
            reason: The reason that the player is being banned.
        """
        logger.info(
            f"[{ctx.author.name}] is banning Minecraft player [{username}] because [{reason}]"
            )
        response = _rcon_command(f"ban {username} {reason}")
        await ctx.send(response)

    @commands.command(
        name='ban-ip',
        help="""
        Ban an IP address from the server (surround the reason in double quotes)
        You can also submit a player username to ban their connected IP
        """
        )
    async def ban_ip(self, ctx, ip_address: str, reason: str) -> None:
        """
        Bans an IP address from the configured Minecraft server.

        Args:
            ip_address: The IP address to ban.
            reason: The reason that the IP address is being banned.
        """
        logger.info(f"[{ctx.author.name}] is banning IP address [{ip_address}] because [{reason}]")
        response = _rcon_command(f"ban-ip {ip_address} {reason}")
        await ctx.send(response)

    @commands.command(help='Display the list of banned players and IP addresses')
    async def banlist(self, ctx) -> None:
        """Displays the banlist of the configured Minecraft server."""
        logger.info(f"[{ctx.author.name}] is getting the banlist")
        response = _rcon_command('banlist')
        await ctx.send(response)

    @commands.command(help='Kick a player off of the server (surround the reason in double quotes)')
    async def kick(self, ctx, username: str, reason: str) -> None:
        """
        Kick a player off of the configured Minecraft server.

        Args:
            username: The Minecraft username of the player to kick.
            reason: The reason that the player is being kicked.
        """
        logger.info(
            f"[{ctx.author.name}] is kicking Minecraft player [{username}] because [{reason}]"
            )
        response = _rcon_command(f"kick {username} {reason}")
        await ctx.send(response)

    @commands.command(help='Pardon (unban) a player from the server')
    async def pardon(self, ctx, username: str) -> None:
        """
        Pardon a player from the configured Minecraft server.

        Args:
            username: The Minecraft username of the player to pardon.
        """
        logger.info(f"[{ctx.author.name}] is pardoning Minecraft player [{username}]")
        response = _rcon_command(f"pardon {username}")
        await ctx.send(response)

    @commands.command(name='pardon-ip', help='Pardon (unban) an IP address from the server')
    async def pardon_ip(self, ctx, ip_address: str) -> None:
        """
        Pardon an IP address from the configured Minecraft server.

        Args:
            ip_address: The IP address to pardon.
        """
        logger.info(f"[{ctx.author.name}] is pardoning IP address [{ip_address}]")
        response = _rcon_command(f"pardon-ip {ip_address}")
        await ctx.send(response)

    @commands.command(help='Grant OP status to a player')
    async def op(self, ctx, username: str) -> None:
        """
        Grant OP status to a Minecraft user on the configured Minecraft server.

        Args:
            username: The Minecraft username of the player to grant OP status.
        """
        logger.info(f"[{ctx.author.name}] is granting OP status to Minecraft player [{username}]")
        response = _rcon_command(f"op {username}")
        await ctx.send(response)

    @commands.command(help='Revoke OP status from a player')
    async def deop(self, ctx, username: str) -> None:
        """
        Revoke OP status from a Minecraft user on the configured Minecraft server.

        Args:
            username: The Minecraft username of the player to revoke OP status from.
        """
        logger.info(f"[{ctx.author.name}] is revoking OP status from Minecraft player [{username}]")
        response = _rcon_command(f"deop {username}")
        await ctx.send(response)

    # Granular Command Error Handling
    # @list.error
    # async def list_error(self, ctx, error):
    #     if isinstance(error, exceptions.McadminbotCommandPermissionsError):
    #         await ctx.send(error)

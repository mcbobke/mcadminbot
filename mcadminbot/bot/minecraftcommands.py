"""
bot/minecraftcommands.py - Implements a discord.ext.commands.Cog to organize and
    expose Minecraft RCON commands to users of the bot.
"""

from discord.ext import commands
from loguru import logger

from . import exceptions
from . import utils


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


class MinecraftCommands(commands.Cog):
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

    @commands.command(help='List all online players')
    async def list(self, ctx) -> None:
        """Lists all players logged in to the configured Minecraft server."""
        logger.info(f"[{ctx.author.name}] is listing connected players")
        response = utils.rcon_command('list')
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
        utils.rcon_command(f"say {message}")
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
        logger.info(
            f"[{ctx.author.name}] is sending message [{message}] to player [{username}]")
        utils.rcon_command(f"tell {username} {message}")
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
        response = utils.rcon_command('whitelist list')
        await ctx.send(response)

    @whitelist.command(name='add', help='Add a player to the whitelist')
    async def whitelist_add(self, ctx, username: str) -> None:
        """
        Add a player to the whitelist of the configured Minecraft server.

        Args:
            username: The Minecraft username of the player to whitelist.
        """
        logger.info(
            f"[{ctx.author.name}] is whitelisting Minecraft player [{username}]")
        response = utils.rcon_command(f"whitelist add {username}")
        await ctx.send(response)

    @whitelist.command(name='off', help='Turn the whitelist off')
    async def whitelist_off(self, ctx) -> None:
        """Turns off the whitelist for the configured Minecraft server."""
        logger.info(f"[{ctx.author.name}] is turning off the whitelist")
        response = utils.rcon_command('whitelist off')
        await ctx.send(response)

    @whitelist.command(name='on', help='Turn the whitelist on')
    async def whitelist_on(self, ctx) -> None:
        """Turns on the whitelist for the configured Minecraft server."""
        logger.info(f"[{ctx.author.name}] is turning on the whitelist")
        response = utils.rcon_command('whitelist on')
        await ctx.send(response)

    @whitelist.command(name='reload', help='Reloads the whitelist')
    async def whitelist_reload(self, ctx) -> None:
        """Reloads the whitelist for the configured Minecraft server."""
        logger.info(f"[{ctx.author.name}] is reloading the whitelist")
        response = utils.rcon_command('whitelist reload')
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
        response = utils.rcon_command(f"whitelist remove {username}")
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
        response = utils.rcon_command(f"ban {username} {reason}")
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
        logger.info(
            f"[{ctx.author.name}] is banning IP address [{ip_address}] because [{reason}]")
        response = utils.rcon_command(f"ban-ip {ip_address} {reason}")
        await ctx.send(response)

    @commands.command(help='Display the list of banned players and IP addresses')
    async def banlist(self, ctx) -> None:
        """Displays the banlist of the configured Minecraft server."""
        logger.info(f"[{ctx.author.name}] is getting the banlist")
        response = utils.rcon_command('banlist')
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
        response = utils.rcon_command(f"kick {username} {reason}")
        await ctx.send(response)

    @commands.command(help='Pardon (unban) a player from the server')
    async def pardon(self, ctx, username: str) -> None:
        """
        Pardon a player from the configured Minecraft server.

        Args:
            username: The Minecraft username of the player to pardon.
        """
        logger.info(
            f"[{ctx.author.name}] is pardoning Minecraft player [{username}]")
        response = utils.rcon_command(f"pardon {username}")
        await ctx.send(response)

    @commands.command(name='pardon-ip', help='Pardon (unban) an IP address from the server')
    async def pardon_ip(self, ctx, ip_address: str) -> None:
        """
        Pardon an IP address from the configured Minecraft server.

        Args:
            ip_address: The IP address to pardon.
        """
        logger.info(
            f"[{ctx.author.name}] is pardoning IP address [{ip_address}]")
        response = utils.rcon_command(f"pardon-ip {ip_address}")
        await ctx.send(response)

    @commands.command(help='Grant OP status to a player')
    async def op(self, ctx, username: str) -> None:
        """
        Grant OP status to a Minecraft user on the configured Minecraft server.

        Args:
            username: The Minecraft username of the player to grant OP status.
        """
        logger.info(
            f"[{ctx.author.name}] is granting OP status to Minecraft player [{username}]")
        response = utils.rcon_command(f"op {username}")
        await ctx.send(response)

    @commands.command(help='Revoke OP status from a player')
    async def deop(self, ctx, username: str) -> None:
        """
        Revoke OP status from a Minecraft user on the configured Minecraft server.

        Args:
            username: The Minecraft username of the player to revoke OP status from.
        """
        logger.info(
            f"[{ctx.author.name}] is revoking OP status from Minecraft player [{username}]")
        response = utils.rcon_command(f"deop {username}")
        await ctx.send(response)

    # Granular Command Error Handling
    # @list.error
    # async def list_error(self, ctx, error):
    #     if isinstance(error, exceptions.McadminbotCommandPermissionsError):
    #         await ctx.send(error)

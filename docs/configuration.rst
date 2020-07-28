Configuration
=============

Config File Format
------------------

Please see `the default YAML config file <https://github.com/mcbobke/mcadminbot/blob/master/mcadminbot/defaults.yaml>`_ to see all of the available config keys.

* ``token`` is a string containing your bot's token (NOT your client secret)
* ``command_prefix`` is a string containing the character that all mcadminbot commands must start with in messages
* ``server_address`` is a string containing the IP address or domain name that your Minecraft server is hosted from
* ``rcon_port`` is an integer containing the port that the Minecraft server's RCON server is bound to
* ``rcon_password`` is a string containing the password used to connect to the RCON server
* ``docker_container_name`` is a string containing the name of the Docker container that is running your Minecraft server (optional)

The rest of the config keys must contain a list of only one of the following types of items:

1. A single string ``ALL`` that grants all users or roles, depending on the key, access to that key's matching command/subcommands.
2. A single string ``NONE`` that denies all users or roles, depending on the key, access to that key's matching command/subcommands.
3. One or more strings containing specific Discord usernames or roles, depending on the key, that grants those entities access to that key's matching command/subcommands.

**Special note about admin_users/admin_roles:** Any users/roles specified here, respectively, will be granted access to every command supported by the bot.

Config File Location and Loading
--------------------------------

mcadminbot exposes the shell parameter ``-c|--config`` which takes a path to your desired config file. If specified, the default config is loaded first and then your specified config is merged on top to override with your custom values. Configuration is then complete and the bot starts. Be sure to edit the systemd service file shown above to include this parameter if desired.

If a desired config file is not specified with ``-c|--config``, mcadminbot loads the default config and then looks for config files in two places:

1. ``/etc/mcadminbot/mcadminbot.yaml``
2. ``/home/$USER/mcadminbot.yaml`` (the home directory of the user running the process)

mcadminbot will load these files in this order; any conflicting keys specified in ``/home/$USER/mcadminbot.yaml`` will override the values found in ``/etc/mcadminbot/mcadminbot.yaml``. Configuration is then complete and the bot starts.

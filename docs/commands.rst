Supported Commands
==================

Please visit the `official Minecraft wiki <https://minecraft.gamepedia.com/Commands>`_ for detailed command help.

You can also run the ``help`` command in Discord to see each command's syntax.

Minecraft Commands
------------------

.. code-block:: shell

    list
    say
    tell
    whitelist (and all subcommands)
    ban
    ban-ip
    banlist
    kick
    pardon
    pardon-ip
    op
    deop

System Commands
---------------

.. code-block:: shell

    restart-docker-server


The ``restart-docker-server`` command allows permitted users and roles to restart a Docker container that is running the Minecraft server. In its current state, this will only work if the bot is running on the same server as the Docker container and therefore ``server_address`` is ``localhost``. Be sure to set ``docker_container_name`` in the config.
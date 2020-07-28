Requirements
============

Basic Requirements
------------------

* Linux
* Python 3.6 (likely works with higher versions but it has not yet been tested)
* A Discord Bot Account and its accompanying token, see `the discord.py documentation <https://discordpy.readthedocs.io/en/latest/discord.html>`_
* A Minecraft server with the RCON server enabled on an accessible interface and port

Bot Permissions
---------------

When generating the invitation link to add your bot to your Discord server, select the following permissions:

* View Channels
* Send Messages

Installing mcadminbot
---------------------

I highly recommend creating a virtual environment for this so that the required modules are isolated away from your system modules.

1. Install the systemd development headers.

    Debian:

    .. code-block:: shell

        sudo apt-get install build-essential \
            libsystemd-journal-dev \
            libsystemd-daemon-dev \
            libsystemd-dev

    CentOS/RHEL:

    .. code-block:: shell
    
        sudo yum install gcc systemd-devel

2. ``cd`` to your desired virtual environment location.
3. Create the virtual environment.

    ``python3 -m venv mcadminbot_env``

4. Activate your virtual environment.

    ``source mcadminbot_env/bin/activate``

5. Install mcadminbot from the Python Package Index.

    ``pip install mcadminbot``

To run mcadminbot from the shell:

``mcadminbot_env/bin/mcadminbot``

Here is the usage text from ``mcadminbot -h|--help``:

.. code-block:: shell

    usage: mcadminbot [-h] [-d {start,stop,restart}] [-c CONFIG_PATH]

    optional arguments:
    -h, --help            show this help message and exit
    -d {start,stop,restart}, --daemon {start,stop,restart}
                            manage mcadminbot as a daemon
    -c CONFIG_PATH, --config CONFIG_PATH
                            path to mcadminbot.yaml

**Note**: You could also use `pipx <https://packaging.python.org/guides/installing-stand-alone-command-line-tools/>`_ to accomplish this.

Systemd Service Setup
---------------------

This portion is optional but very recommended for ease of use.

1. Create the file ``/etc/systemd/system/mcadminbot.service`` with the following contents, replacing paths where needed:

    .. code-block:: shell

        [Unit]
        Description=mcadminbot - A Minecraft Discord bot

        [Service]
        Type=forking
        PIDFile=/run/mcadminbot.pid
        ExecStart=/path/to/mcadminbot_env/bin/mcadminbot -d start
        ExecReload=/path/to/mcadminbot_env/bin/mcadminbot -d restart
        ExecStop=/path/to/mcadminbot_env/bin/mcadminbot -d stop
        User=root
        Group=root

        [Install]
        WantedBy=multi-user.target

2. Reload systemd.

    ``sudo systemctl daemon-reload``

3. Enable mcadminbot to run on startup.

    ``sudo systemctl enable mcadminbot``

Now, once you've followed the Configuration section, you can use the following commands to control the bot service:

.. code-block:: shell

    sudo systemctl start mcadminbot
    sudo systemctl stop mcadminbot
    sudo systemctl restart mcadminbot

Requirements
============

* Linux
* Python 3.6 (likely works with higher versions but it has not yet been tested)
* A Discord Bot Account and its accompanying token, see `the discord.py documentation <https://discordpy.readthedocs.io/en/latest/discord.html>`_
* A Minecraft server with the RCON server enabled on an accessible interface and port

Bot Permissions
===============

When generating the invitation link to add your bot to your Discord server, select the following permissions:

* View Channels
* Send Messages

Installing mcadminbot
=====================

I highly recommend creating a virtual environment for this so that the required modules are isolated away from your system modules.

1. Install the systemd development headers.

    Debian:

    .. code-block:: bash
        sudo apt-get install build-essential \
            libsystemd-journal-dev \
            libsystemd-daemon-dev \
            libsystemd-dev

    CentOS/RHEL:

    `sudo yum install gcc systemd-devel`

2. `cd` to your desired virtual environment location.
3. Create the virtual environment.

    `python3 -m venv mcadminbot_env`

4. Activate your virtual environment.

    `source mcadminbot_env/bin/activate`

5. Install mcadminbot from the Python Package Index.

    `pip install mcadminbot`

To run mcadminbot from the shell:

`mcadminbot_env/bin/mcadminbot`

Here is the usage text from `mcadminbot -h|--help`:

```shell
usage: mcadminbot [-h] [-d {start,stop,restart}] [-c CONFIG_PATH]

optional arguments:
  -h, --help            show this help message and exit
  -d {start,stop,restart}, --daemon {start,stop,restart}
                        manage mcadminbot as a daemon
  -c CONFIG_PATH, --config CONFIG_PATH
                        path to mcadminbot.yaml
```

__Note__: You could also use [pipx](https://packaging.python.org/guides/installing-stand-alone-command-line-tools/) to accomplish this.
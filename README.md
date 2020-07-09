# mcadminbot

A Discord bot that allows permitted server members and roles to administrate a Minecraft server over RCON through chat messages.

## Requirements

* Linux
* Python 3.6 (likely works with higher versions but it has not yet been tested)
* A Discord Bot Account and its accompanying token, see [the discord.py documentation](https://discordpy.readthedocs.io/en/latest/discord.html)
* A Minecraft server with the RCON server enabled on an accessible interface and port
* systemd development headers (see Installation)

## Bot Permissions

When generating the invitation link to add your bot to your Discord server, select the following permissions:

* View Channels
* Send Messages

## Installation

I highly recommend creating a virtual environment for this so that the required modules are isolated away from your system modules.

1. Install the systemd development headers.

    Debian:

    ```shell
    sudo apt-get install build-essential \
        libsystemd-journal-dev \
        libsystemd-daemon-dev \
        libsystemd-dev
    ```

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

### Systemd Service Setup

This portion is optional but very recommended for ease of use.

1. Create the file `/etc/systemd/system/mcadminbot.service` with the following contents, replacing paths where needed:

    ```shell
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
    ```

2. Reload systemd.

    `sudo systemctl daemon-reload`

3. Enable mcadminbot to run on startup.

    `sudo systemctl enable mcadminbot`

Now, once you've followed the Configuration section, you can use the following commands to control the bot service:

```shell
sudo systemctl start mcadminbot
sudo systemctl stop mcadminbot
sudo systemctl restart mcadminbot
```

## Configuration

### Config File Format

Please view [the default YAML config file](./mcadminbot/defaults.yaml) to see all of the available config keys.

* `token` is a string containing your bot's token (NOT your client secret)
* `command_prefix` is a string containing the character that all mcadminbot commands must start with in messages
* `server_address` is a string containing the IP address or domain name that your Minecraft server is hosted from
* `rcon_port` is an integer containing the port that the Minecraft server's RCON server is bound to
* `rcon_password` is a string containing the password used to connect to the RCON server
* `docker_container_name` is a string containing the name of the Docker container that is running your Minecraft server (optional, see the `restart-docker-server` command notes in Supported Commands)

The rest of the config keys must contain a list of only one of the following types of items:

1. A single string `ALL` that grants all users or roles, depending on the key, access to that key's matching command/subcommands.
2. A single string `NONE` that denies all users or roles, depending on the key, access to that key's matching command/subcommands.
3. One or more strings containing specific Discord usernames or roles, depending on the key, that grants those entities access to that key's matching command/subcommands.

__Special note about admin_users/admin_roles:__ Any users/roles specified here, respectively, will be granted access to every command supported by the bot.

### Config File Location and Loading

mcadminbot exposes the shell parameter `-c|--config` which takes a path to your desired config file. If specified, the default config is loaded first and then your specified config is merged on top to override with your custom values. Configuration is then complete and the bot starts. Be sure to edit the systemd service file shown above to include this parameter if desired.

If a desired config file is not specified with `-c|--config`, mcadminbot loads the default config and then looks for config files in two places:

1. `/etc/mcadminbot/mcadminbot.yaml`
2. `/home/$USER/mcadminbot.yaml` (the home directory of the user running the process)

mcadminbot will load these files in this order; any conflicting keys specified in `/home/$USER/mcadminbot.yaml` will override the values found in `/etc/mcadminbot/mcadminbot.yaml`. Configuration is then complete and the bot starts.

## Supported Commands

Please visit the [official Minecraft wiki's reference for Minecraft command syntax](https://minecraft.gamepedia.com/Commands).

Currently supported Minecraft commands:

```shell
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
```

Currently supported system commands:

```shell
restart-docker-server
```

The `restart-docker-server` command allows permitted users and roles to restart a Docker container that is running the Minecraft server. In its current state, this will only work if the bot is running on the same server as the Docker container and therefore `server_address` is `localhost`. Be sure to set `docker_container_name` in the config.

## Contributing

Pull requests are happily welcomed for any additions or improvements!

## Todo

* [ ] Implement more Minecraft commands
* [ ] Write tests and implement automated testing of branches
* [ ] Implement proper semantic versioning and CI/CD

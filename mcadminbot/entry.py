"""
entry.py - Entrypoint for mcadminbot, parses command line arguments, handles daemonization.

An interface to _main is created when installing the package through pip.
In your virtualenv directory, you will find this script at bin/mcadminbot.
"""

import os
import sys
import atexit
import signal
import argparse
import pathlib
from loguru import logger
from cysystemd.journal import JournaldLogHandler

import mcadminbot.config as config
from mcadminbot.bot.bot import run_bot

PIDFILE = pathlib.Path('/run/mcadminbot.pid')


def _run(config_path: str) -> None:
    config.load_config(config_path)
    logger.info('mcadminbot config has been loaded')
    run_bot()


def _daemonize(stdin_path: str = '/dev/null', stdout_path: str = '/dev/null',
               stderr_path: str = '/dev/null') -> None:
    if PIDFILE.exists():
        raise RuntimeError('Already running')

    # First fork (detaches from parent)
    try:
        if os.fork() > 0:
            raise SystemExit(0)  # Parent exit
    except OSError:
        raise RuntimeError('fork #1 failed.')

    os.chdir('/')
    os.umask(0)
    os.setsid()
    # Second fork (relinquish session leadership)
    try:
        if os.fork() > 0:
            raise SystemExit(0)
    except OSError:
        raise RuntimeError('fork #2 failed.')

    # Flush I/O buffers
    sys.stdout.flush()
    sys.stderr.flush()

    # Replace file descriptors for stdin, stdout, and stderr
    with open(stdin_path, 'rb', 0) as daemon_stdin:
        os.dup2(daemon_stdin.fileno(), sys.stdin.fileno())
    with open(stdout_path, 'ab', 0) as daemon_stdout:
        os.dup2(daemon_stdout.fileno(), sys.stdout.fileno())
    with open(stderr_path, 'ab', 0) as daemon_stderr:
        os.dup2(daemon_stderr.fileno(), sys.stderr.fileno())

    # Write the PID file
    with PIDFILE.open('w') as pidfile:
        pidfile.write(f"{os.getpid()}")

    # Arrange to have the PID file removed on exit/signal
    atexit.register(lambda: os.remove(PIDFILE))

    # Signal handler for termination (required)
    def sigterm_handler(signo, frame):
        raise SystemExit(1)

    signal.signal(signal.SIGTERM, sigterm_handler)


def _start_daemon(config_path: str) -> None:
    try:
        _daemonize(stdin_path='/dev/null', stdout_path='/dev/null', stderr_path='/dev/null')
    except RuntimeError as error:
        logger.error(error)
        raise SystemExit(1)
    logger.info('mcadminbot daemon is started')
    _run(config_path)


def _stop_daemon():
    if PIDFILE.exists():
        with PIDFILE.open('r') as pidfile:
            os.kill(int(pidfile.read()), signal.SIGTERM)
        while PIDFILE.exists():
            pass
        logger.info('mcadminbot daemon is stopped')
    else:
        logger.error('mcadminbot is not running - it cannot be stopped')
        raise SystemExit(1)


def _generate_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--daemon', help='manage %(prog)s as a daemon',
                        dest='daemon', action='store', choices=['start', 'stop', 'restart'])
    parser.add_argument('-c', '--config', help='path to mcadminbot.yaml',
                        dest='config_path', action='store')
    return parser


def _main():
    parser = _generate_arg_parser()
    args = parser.parse_args()

    # Remove the default log handler for stderr before starting
    logger.remove()

    logger.add(
        sink='/tmp/mcadminbot.log',
        level='DEBUG',
        format='{level} - {time} - {module} - {message}',
        rotation='100 MB',
        compression='tar.gz'
        )

    if args.daemon:
        logger.add(
            sink=JournaldLogHandler(),
            level='DEBUG',
            format='{level} - {module} - {message}'
        )

    if args.daemon == 'start':
        logger.info('mcadminbot daemon is starting')
        _start_daemon(args.config_path)

    elif args.daemon == 'stop':
        logger.info('mcadminbot daemon is stopping')
        _stop_daemon()

    elif args.daemon == 'restart':
        logger.info('mcadminbot daemon restart requested')
        _stop_daemon()
        _start_daemon(args.config_path)

    else:
        logger.add(
            sink=sys.stdout,
            level='DEBUG',
            format='{level} - {time} - {module} - {message}'
        )
        logger.info('mcadminbot is starting without daemonization')
        _run(args.config_path)

if __name__ == '__main__':
    _main()

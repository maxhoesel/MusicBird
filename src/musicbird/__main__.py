#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path
import sys
from typing import List

from schema import SchemaError

from . import config, run, scan, prune, copy, encode, __version__

logger = logging.getLogger("musicbird")


def main(args: List[str]) -> bool:
    """Main command-line entrypoint.

    Called from any of the various ways to start MusicBird. Parses general arguments
    and initializes some basics (configuration), before handing off control to the
    called subcommands `$commandname_command` method

    Args:
        args (list): A list of command-line arguments, excluding argv[0] (the call to "musicbird" itself).

    Returns:
        bool: True if all commands completed successfully, False if not.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False, prog="musicbird")
    parser.add_argument("-c", "--config", help="Path to the configuration file to use",
                        default=config.Config.DEFAULT_PATH)
    parser.add_argument("--loglevel", "-v", "--verbosity", help="Set the output verbosity",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "FATAL"], default="INFO")
    parser.add_argument("--version", help="Print the program version and exit", action="store_true")
    parser.add_argument("command", nargs="?", help="The command you want to run", choices=[
                        "config", "run", "scan", "copy", "encode", "prune"])
    args, command_args = parser.parse_known_args(args)

    logging.basicConfig(level=getattr(logging, args.loglevel))

    if args.version:
        print(__version__)
        return True

    config_path = Path(args.config)
    # The "config" command needs to be runnable without having loaded an existing config.
    if args.command not in ["config"]:
        try:
            _config = config.Config(config_path)
        except OSError:
            sys.exit("Could not read config file. You can generate a new config file with 'musicbird config generate'")
        except SchemaError:
            sys.exit("Your configuration file is invalid. Please check the error message above for details")

    if args.command == "config":
        successful = config.config_command(parser, command_args, config_path)
    elif args.command == "run":
        successful = run.run_command(parser, command_args, _config.config)
    elif args.command == "scan":
        successful = scan.scan_command(parser, command_args, _config.config)
    elif args.command == "copy":
        successful = copy.copy_command(parser, command_args, _config.config)
    elif args.command == "encode":
        successful = encode.encode_command(parser, command_args, _config.config)
    elif args.command == "prune":
        successful = prune.prune_command(parser, command_args, _config.config)
    else:
        parser.parse_args()
        successful = False

    if not successful:
        return False
    return True


def entrypoint():
    """Pre-Entrypoint for the program.

    Used to pass arguments to the main function explicitly as this makes testing
    command line parameters a lot easier.
    """
    if not main(sys.argv[1:]):
        sys.exit("Some commands did not complete successfully")


if __name__ == "__main__":
    entrypoint()

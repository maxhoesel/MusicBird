"""Tools related to reading and parsing the MusicBird configuration file.

This module provides utilities to interface with MusicBirds configuration file,
as well as the entrypoint for the config CLI command.
"""

import argparse
import logging
import json
import re
import os
from pathlib import Path
import sys
from typing import Dict, List, Union

from pkg_resources import resource_stream
from schema import Schema, And, SchemaError, Use, Optional
import yaml

logger = logging.getLogger(__name__)


class Config:
    """Class representing the MusicBird configuration file.

    When created, this class loads a configuration file from disk, verifies that it is valid
    and does some basic processing, such as fully expanding all file paths. You can then access
    the configuration using the .config attribute.

    Attributes:
        config: Configuration, as a dict
    """

    _SCHEMA = Schema({
        "source": And(Use(Path)),
        "database": And(Use(str), len, lambda d: d in ("sqlite3")),
        Optional("sqlite3"): {
            "path": And(Use(Path))
        },
        "destination": And(Use(Path)),
        "copy": {
            "files": And(Use(bool)),
            "album_art": And(Use(bool))
        },
        "prune": And(Use(bool)),
        "lossy_files": And(Use(str), len, lambda l: l in ("copy", "convert", "ignore")),
        "encoder": And(Use(str), len, lambda f: f in ("mp3", "opus")),
        "mp3": {
            "vbr": And(Use(bool)),
            Optional("quality"): And(Use(int), lambda q: 0 <= q <= 9),
            Optional("bitrate"): And(Use(str), lambda b: re.match(r'\d{1,4}k', b))
        },
        "opus": {
            "bitrate": And(Use(str), lambda b: re.match(r'\d{1,4}k', b))
        },
        "threads": And(Use(int), lambda t: t > 0)
    })
    # Name of the directory used to storing files related to this app
    _DIRNAME = "musicbird"
    _DEFAULT_CONFIG = {
        "database": "sqlite3",
        "sqlite3": {
            "path": f"{os.environ.get('XDG_DATA_HOME', os.environ['HOME'] + '/.local/share')}/{_DIRNAME}/db.sqlite3"
        },
        "copy": {
            "files": True,
            "album_art": False,
        },
        "prune": True,
        "lossy_files": "copy",
        "encoder": "mp3",
        "mp3": {
            "vbr": True,
            "quality": 0,
        },
        "opus": {
            "bitrate": "128k",
        },
        "threads": os.cpu_count()
    }

    DEFAULT_PATH = Path(
        f"{os.environ.get('XDG_CONFIG_HOME', os.environ['HOME'] + '/.config')}/{_DIRNAME}/config.yml")

    def __init__(self, path: Path) -> None:
        """Read a configuration file and parse/validate it.

        This will read a configuration file from disk, and perform some validation on it,
        before representing the result as part of the returned Object.

        Args:
            path (Path): The path to the config file on disk

        Raises:
            OSError: If the file could not be read
            schema.Error: If the configuration file is invalid
        """
        try:
            with path.open() as f:
                configfile = yaml.safe_load(f)
        except OSError as e:
            logger.fatal(f"Error while attempting to read config at {repr(e)}")
            raise
        if not configfile:
            logger.fatal(f"Empty config file at {path}")
            raise EOFError(f"Empty config file at {path}")

        self.config = Config._add_default_config(configfile)
        self._validate()
        self._resolve_paths(self.config)

    def print(self, output_format: str = "yml"):
        """Print the current configuration to console.

        Args:
            output_format (str, optional): Format to print the config in. Can be "yml" or "json". Defaults to "yml".
        """
        printable_config = Config._printify_paths(self.config)

        if output_format == "yml":
            print(yaml.safe_dump(printable_config))
        elif output_format == "json":
            print(json.dumps(printable_config))

    def _validate(self):
        """Validate the configuration file.

        Performs validation of the config file against the builtin schema.
        This might not catch every possible error, but it's a good start.

        Raises:
            SchemaError: Upon failed validation
        """
        try:
            self.config = Config._SCHEMA.validate(self.config)
        except SchemaError as e:
            logger.fatal(f"Invalid configuration file: {repr(e)}")
            raise e

    @staticmethod
    def _printify_paths(item: Union[Dict, List]) -> Union[Dict, List]:
        """Convert all path objects to strings.

        Converts all Path objects in item to strings, for usage with yaml/json dump.
        Calls itself recursively

        Args:
            item (Union[Dict, List]): The collection containing Path objects

        Returns:
            Union[Dict, List]: The collection with all paths converted
        """
        if isinstance(item, dict):
            for key in item:
                if isinstance(item[key], (dict, list)):
                    item[key] = Config._printify_paths(item[key])
                elif isinstance(item[key], Path):
                    item[key] = str(item[key])
        if isinstance(item, list):
            for i in range(len(item)):
                if isinstance(item[i], (dict, list)):
                    item[i] = Config._printify_paths(item[i])
                elif isinstance(item[i], Path):
                    item[i] = str(item[i])
        return item

    @staticmethod
    def _resolve_paths(item: Union[List, Dict]) -> Union[List, Dict]:
        """Make all paths in a collection absolute.

        This calls resolve() for all paths in a given collection, converting them to their absolute versions.
        Calls itself recursively.

        Args:
            item (Union[List, Dict]): The collection containing the non-absolute paths.

        Returns:
            Union[List, Dict]: The collection with all Paths resolved.
        """
        if isinstance(item, dict):
            for key in item:
                if isinstance(item[key], (dict, list)):
                    item[key] = Config._resolve_paths(item[key])
                elif isinstance(item[key], Path):
                    item[key] = item[key].expanduser().resolve()
        if isinstance(item, list):
            for i in range(len(item)):
                if isinstance(item[i], (dict, list)):
                    item[i] = Config._resolve_paths(item[i])
                elif isinstance(item[i], Path):
                    item[i] = item[i].expanduser().resolve()
        return item

    @staticmethod
    def _add_default_config(config: Dict) -> Dict:
        """Combine the default and concrete documentation into a single dict.

        Args:
            config (Dict): The concrete configuration on which to act.

        Returns:
            Dict: A dict containing the merged config.
        """
        merged_config = Config._recursive_merge(dict(Config._DEFAULT_CONFIG), config)
        return merged_config

    @staticmethod
    def _recursive_merge(a: Dict, b: Dict) -> Dict:
        """Merge two dictionaries

        Helper method that merges a dictionary (b) into another one (a).
        Modifies A.

        Args:
            a (Dict): The dictionary to merge into.
            b (Dict): The dictionary to add to a.

        Returns:
            Dict: The fully merged dictionary (a).
        """
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    Config._recursive_merge(a[key], b[key])
                else:
                    a[key] = b[key]
            else:
                a[key] = b[key]
        return a


def config_command(parent_parser: argparse.ArgumentParser, args: List[str], config_path: Path) -> bool:
    """Entrypoint for the CLI `config` command.

    This command is not part of the usual run lifecycle,
    but is instead a convenience command to create or view a configuration file.

    Current sub-actions are:
    * generate - To create a new config file
    * print - To print an existing config file

    Args:
        parent_parser (argparse.ArgumentParser): The parser from the main entrypoint.
            Used to display a full --help output by inheriting its arguments.
        args (List[str]): List of arguments not parsed by the main parser.
        config_path (Path): Path to the configuration file to use. In other CLI entrypoints, this would be the
            parsed config Object, but we can't do that here as we might be generating one for the first time.

    Returns:
        bool: True if the command was successful, False if not
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__, prog="musicbird", parents=[parent_parser])
    subparsers = parser.add_subparsers(dest="action")

    parser_generate = subparsers.add_parser("generate", help="Generate a new configuration file")
    parser_generate.add_argument("--output", "-o", default=Config.DEFAULT_PATH,
                                 help="Select the path at which to create the configfile")
    parser_generate.add_argument(
        "--force", "-f", help="Overwrite an already existing configuration file", action="store_true")

    parser_print = subparsers.add_parser("print", help="Print the currently loaded configuration")
    parser_print.add_argument("--format", "-f", default="yml", choices=["json", "yml"],
                              help="Print the configuration in this format")

    args = parser.parse_args(args)

    if args.action == "generate":
        output = Path(args.output)
        if output.exists() and not args.force:
            sys.exit(f"Configuration file at {output} already exists")

        config = resource_stream(__name__, "data/default_config.yml").readlines()
        try:
            output.parent.mkdir(exist_ok=True, parents=True)
            with output.open(mode='wb') as f:
                f.writelines(config)
        except OSError as e:
            sys.exit(f"Error while writing configuration: {repr(e)}")
        logger.info(f"Initialized configuration file at: {output}")
        return True

    elif args.action == "print":
        try:
            Config(config_path).print(args.format)
            return True
        except OSError:
            sys.exit("Could not read config file")
        except SchemaError:
            sys.exit("Your configuration file is invalid. Please check the error message above for details")

"""Provides the run command and related functions.
"""

import argparse
import logging
from typing import Dict, List

from .db import init as init_db
from .scan import scan
from .copy import copy
from .encode import encode
from .prune import prune

logger = logging.getLogger(__name__)


def run_command(parent_parser: argparse.ArgumentParser, args: List[str], config: Dict):
    """Entrypoint for the CLI `run` command.

    Args:
        parent_parser (argparse.ArgumentParser): The parser from the main entrypoint.
            Used to display a full --help output by inheriting its arguments.
        args (List[str]): List of arguments not parsed by the main parser.
        config (Dict): Dictionary containing the MusicBird configuration
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__, prog="musicbird", parents=[parent_parser])
    parser.add_argument("--rescan", action="store_true",
                        help="Force a rescan of the entire library. This will force all files to be reprocessed")
    parser.add_argument("--pretend", action="store_true",
                        help="Show what changes would be made but don't modify any files")
    args = parser.parse_args(args)
    return run(config, args.rescan, args.pretend)


def run(config: Dict, rescan: bool = False, pretend: bool = False):
    """Scan, then process the entire music library.

    Equivalent to calling scan(), copy(), encode(), prune() in that order.

    Args:
        config (Dict): Dictionary containing the musicbird configuration.
        db (LibraryDB): Database object to read/write the library status from/to.
        pretend (bool, optional): Pretend to process/scan, but don't perform any actual operations. Defaults to False.

    Returns:
        bool: True if all files were processed successfully, false if not.
    """
    db = init_db(config, delete=rescan, pretend=pretend)

    results = []
    results.append(scan(config, db))
    results.append(copy(config, db, pretend=pretend))
    results.append(encode(config, db, pretend=pretend))
    results.append(prune(config, db, pretend=pretend))
    if False in results:
        return False
    else:
        return True

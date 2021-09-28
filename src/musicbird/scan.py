"""Provides the scan processing step and related functions.
"""

import argparse
import logging
from typing import Dict, List

from .db import LibraryDB, init as init_db
from .scanner import LibraryScanner

logger = logging.getLogger(__name__)


def scan_command(parent_parser: argparse.ArgumentParser, args: List[str], config: Dict) -> bool:
    """Entrypoint for the CLI `scan` command.

    Args:
        parent_parser (argparse.ArgumentParser): The parser from the main entrypoint.
            Used to display a full --help output by inheriting its arguments.
        args (List[str]): List of arguments not parsed by the main parser.
        config (Dict): Dictionary containing the MusicBird configuration
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__, prog="musicbird", parents=[parent_parser])
    parser.add_argument("--pretend", action="store_true", help="Show scan results but don't store them")
    args = parser.parse_args(args)
    return scan(config, init_db(config, pretend=args.pretend))


def scan(config: Dict, db: LibraryDB) -> bool:
    """Scan the source library for changed files and write them to the DB.

    Performs a filesystem scan on the source music library, registering any new, changed or deleted files along the way.
    Once files are registered, they are then stored in the Database for usage by other commands.

    Args:
        config (Dict): Dictionary containing the musicbird configuration.
        db (LibraryDB): Database object to read/write the library status from/to.
        pretend (bool, optional): Pretend to scan, but don't modify the DB. Defaults to False.

    Returns:
        bool: True if the scan was successful, False if not.
    """
    scanner = LibraryScanner(config["source"], db)
    logger.info("Scanning library...")
    result = scanner.scan()
    logger.info((
        f"Scanned library. Summary: {len(db.get_all_files())} total files, {len(db.get_files_needing_processing())} "
        f"files to process, {len(db.get_deleted_files())} files deleted."
    ))
    return result

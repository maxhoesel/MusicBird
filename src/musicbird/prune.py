"""Provides the prune processing step and related functions.
"""

import argparse
import os
import logging
from typing import Dict, List

from .db import LibraryDB, init as init_db
from .file import File

logger = logging.getLogger(__name__)


def prune_command(parent_parser: argparse.ArgumentParser, args: List[str], config: Dict) -> bool:
    """Entrypoint for the CLI `prune` command.

    Args:
        parent_parser (argparse.ArgumentParser): The parser from the main entrypoint.
            Used to display a full --help output by inheriting its arguments.
        args (List[str]): List of arguments not parsed by the main parser.
        config (Dict): Dictionary containing the MusicBird configuration
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__, prog="musicbird", parents=[parent_parser])
    parser.add_argument("--pretend", action="store_true",
                        help="Show what files would be pruned, but don't perform the actual deletion")
    args = parser.parse_args(args)
    db = init_db(config, pretend=args.pretend)
    return prune(config, db, args.pretend)


def prune(config: Dict, db: LibraryDB, pretend=False) -> bool:
    """Process and delete all files marked for deletion in the mirror library.

    Attempts to delete all files that are marked as deleted in the mirror library,
    then marks them as processed.

    Args:
        config (Dict): Dictionary containing the musicbird configuration.
        db (LibraryDB): Database object to read/write the library status from/to.
        pretend (bool, optional): Pretend to delete, but don't perform any filesystem operations. Defaults to False.

    Returns:
        bool: True if all files were processed successfully, false if not.
    """
    to_prune = db.get_deleted_files()
    logger.info(f"Need to delete {len(to_prune)} files")

    successes: List[File] = []
    failures: List[File] = []
    for file in to_prune:
        dest = file.get_dest_path(config)
        if not pretend:
            try:
                dest.unlink()
            except FileNotFoundError:
                db.remove_file(file)
                successes.append(file)
                logger.info(f"Removed file: {dest}")
            except OSError as e:
                logger.error(f"Could not remove file {dest}: {repr(e)}")
                failures.append(file)
            else:
                db.remove_file(file)
                successes.append(file)
                logger.info(f"Removed file: {dest}")
        else:
            successes.append(file)
            db.remove_file(file)

        if not os.listdir(dest.parent):
            # Remove empty leftover directories
            try:
                os.removedirs(dest.parent)
            except FileNotFoundError:
                pass
            except OSError as e:
                logger.warning(f"Could not remove empty directory {dest.parent}: {repr(e)}")

    logger.info(f"Successfully pruned {len(successes)} files")
    if failures:
        logger.error(f"Failed to delete {len(failures)} files. See above for errors")
        failures_str = "\n".join([f.path for f in failures])
        logger.debug(f"Failed files: {failures_str}")
        return False
    else:
        return True

"""Provides the copying processing step and related functions.
"""

import argparse
import logging
from typing import Dict, List

from .db import LibraryDB, init as init_db
from .file import File, FileType

logger = logging.getLogger(__name__)


def copy_command(parent_parser: argparse.ArgumentParser, args: List[str], config: Dict) -> bool:
    """Entrypoint for the CLI `copy` command.

    Args:
        parent_parser (argparse.ArgumentParser): The parser from the main entrypoint.
            Used to display a full --help output by inheriting its arguments.
        args (List[str]): List of arguments not parsed by the main parser.
        config (Dict): Dictionary containing the MusicBird configuration
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__, prog="musicbird", parents=[parent_parser])
    parser.add_argument("--pretend", action="store_true",
                        help="Show what files would be copied, but don't perform the actual copy")
    args = parser.parse_args(args)
    db = init_db(config, pretend=args.pretend)
    return copy(config, db, args.pretend)


def copy(config: Dict, db: LibraryDB, pretend=False) -> bool:
    """Process and copy all files marked for copying to the mirror library.

    Processes all regular/copyable files according to their state in the library DB.
    Will copy regular files, album art and lossy files depending on the values set in config,
    before marking them as processed in the Databse.

    Args:
        config (Dict): Dictionary containing the musicbird configuration.
        db (LibraryDB): Database object to read/write the library status from/to.
        pretend (bool, optional): Pretend to copy, but don't perform any filesystem operations. Defaults to False.

    Returns:
        bool: True if all files were processed successfully, false if not.
    """
    to_copy: List[File] = []
    for file in db.get_files_needing_processing():
        if ((file.type == FileType.OTHER and config["copy"]["files"])
            or (file.type == FileType.ALBUMART and config["copy"]["album_art"])
            or (file.type == FileType.LOSSY and config["lossy_files"] == "copy")
            ):
            to_copy.append(file)
        # Remove the processing flag from files concerning us if the required option is not set
        if ((file.type == FileType.OTHER and not config["copy"]["files"])
            or (file.type == FileType.ALBUMART and not config["copy"]["album_art"])
            or (file.type == FileType.LOSSY and config["lossy_files"] == "ignore")
            ):
            file.needs_processing = False
    logger.info(f"Need to copy {len(to_copy)} files")

    successes = []
    failures = []
    for file in to_copy:
        if not pretend:
            if file.copy_to_dest(config):
                file.needs_processing = False
                db.add_or_update_file(file)
                successes.append(file)
            else:
                failures.append(file)
        else:
            file.needs_processing = False
            db.add_or_update_file(file)
            successes.append(file)

    logger.info(f"Successfully copied {len(successes)} files")
    if failures:
        logger.error(f"Failed to copy {len(failures)} files. See above for errors")
        failures_str = "\n".join([f.path for f in failures])
        logger.debug(f"Failed files: {failures_str}")
        return False
    else:
        return True

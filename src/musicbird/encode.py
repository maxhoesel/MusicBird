"""Provides the encode processing step and related functions.
"""

import argparse
import concurrent.futures
import logging
from queue import Queue
import threading
import time
from typing import Dict, List

from .db import LibraryDB, init as init_db
from .file import File, FileType

logger = logging.getLogger(__name__)


def encode_command(parent_parser: argparse.ArgumentParser, args, config: Dict) -> bool:
    """Entrypoint for the CLI `encode` command.

    Args:
        parent_parser (argparse.ArgumentParser): The parser from the main entrypoint.
            Used to display a full --help output by inheriting its arguments.
        args (List[str]): List of arguments not parsed by the main parser.
        config (Dict): Dictionary containing the MusicBird configuration
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__, prog="musicbird", parents=[parent_parser])
    parser.add_argument("--pretend", action="store_true",
                        help="Show what files would be converted, but don't perform the actual encoding")
    args = parser.parse_args(args)
    db = init_db(config, pretend=args.pretend)
    return encode(config, db, args.pretend)


def _encode_worker(file: File, config: Dict, successes: Queue, failures: Queue) -> bool:
    """Thread function that processes a single file, then returns.

    Called by encode(), this worker first encodes its file,
    then puts the file into either the successes or failures queue, depending on whether everything went well.

    Args:
        file (File): The file to encode.
        config (Dict): MusicBird config dict.
        successes (Queue): Queue for successfully encoded files.
        failures (Queue): Queue for failed encodes.

    Returns:
        bool: True if the encode was successful, False if not
    """
    if file.encode_to_dest(config):
        file.needs_processing = False
        successes.put(file)
        return True
    else:
        failures.put(file)
        return False


def _db_update_worker(db: LibraryDB, input_q: Queue, output: Queue) -> None:
    """Processes encoded files and saves them to the DB.

    Processes files will also be put into the output queue.
    Terminates upon receiving a None object.

    args:
        db (LibraryLB): Database to write to.
        input_q (Queue): Queue to read files from.
        output (Queue): Queue to send processed files to.
    """
    while True:
        if not input_q.empty():
            file = input_q.get()
            if not file:
                # None object was sent by controll thread -> exit
                return
            db.add_or_update_file(file)
            output.put(file)
            logger.info(f"Processed file: {file.path}")
        else:
            time.sleep(1)


def encode(config: Dict, db: LibraryDB, pretend=False) -> bool:
    """Process and copy all files marked for copying to the mirror library.

    Encodes all files that are due for encoding, according to the data in the library DB.
    Will encode lossles files and also lossy files, if the configuration option is set accordingly.

    Args:
        config (Dict): Dictionary containing the musicbird configuration
        db (LibraryDB): Database object to read/write the library status from/to.
        pretend (bool, optional): Pretend to encode, but don't perform any actual operations. Defaults to False.

    Returns:
        bool: True if all files were processed successfully, false if not.
    """
    to_encode: List[File] = []
    for file in db.get_files_needing_processing():
        if file.type == FileType.LOSSLESS or (file.type == FileType.LOSSY and config["lossy_files"] == "convert"):
            to_encode.append(file)
        # Remove the processing flag from lossy files if they're to be ignored
        if file.type == FileType.LOSSY and config["lossy_files"] == "ignore":
            file.needs_processing = False
    logger.info(f"Need to encode {len(to_encode)} files")

    if not pretend:
        # Queue structure:
        # encode_worker --- success ---> successful_encodes ---> db_update_worker ---> processed_files
        #      |
        #      +----------- failure ---> failed_encodes
        successful_encodes = Queue()
        failed_encodes = Queue()
        processed_files = Queue()

        db_thread = threading.Thread(target=_db_update_worker, args=(db, successful_encodes, processed_files))
        db_thread.start()

        with concurrent.futures.ThreadPoolExecutor(config["threads"]) as executor:
            for file in to_encode:
                executor.submit(_encode_worker, file, config, successful_encodes, failed_encodes)

        # Encode jobs have finished, add termination object to DB queue
        successful_encodes.put(None)
        db_thread.join()

        # Process failures
        failures: List[File] = []
        while not failed_encodes.empty():
            failures.append(failed_encodes.get_nowait())

    else:
        processed_files = []
        for file in to_encode:
            file.needs_processing = False
            db.add_or_update_file(file)
            processed_files.append(file)
            logger.info(f"Encoded file: {file.path}")
        failures = []

    logger.info(f"Successfully encoded {len(to_encode) - len(failures)} files")
    if failures:
        logger.error(f"Failed to delete {len(failures)} files. See above for errors")
        failures_str = "\n".join([str(f.path) for f in failures])
        logger.debug(f"Failed files: {failures_str}")
        return False
    else:
        return True

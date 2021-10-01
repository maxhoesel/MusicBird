"""Provides utilities for scanning the music library filesystem for files.

This module provides a LibraryScanner class that can be used to walk through a directory and
pick up any files relevant to musicbird, plus changes made to it.
"""

import logging
from pathlib import Path

import ffmpeg

from .db import LibraryDB
from .file import File


logger = logging.getLogger(__name__)

# Always ignore these files as system metadata
IGNORE_FILES = [
    "Thumbs.db"
]


class LibraryScanner:
    """Index a directory and add its contents to the DB.

    Use this class to scan a directory for files and add them to the provided Database.
    """

    def __init__(self, path: Path, db: LibraryDB) -> None:
        """Generate a new scanner for the given path and database.

        Args:
            path (Path): The path to scan.
            db (LibraryDB): The library to save the result to.
        """
        self.path = path.resolve()
        self.db = db

    def scan(self) -> bool:
        """ Scan the filesystem for changes.

        Registers new, modified and deleted files and updates the Library.

        Returns:
            bool: True if all files were scanned successfully, False if not.
        """
        successful = False

        # Mark all files as deleted in-memory at the beginning of our scan
        # As files are rediscovered, the deleted flag will be removed
        logger.info(f"Scanning directory {self.path} into library")

        for file in self.db.get_all_files():
            file.was_deleted = True
            self.db.add_or_update_file(file)

        for path in self.path.glob("./**/*"):
            if path.is_file() and path.name not in IGNORE_FILES:
                file = File(path)
                try:
                    file.determine_type()
                except ffmpeg.Error as e:
                    logger.error(f"Could not determine filetype, skipping: {file.path}. FFmpeg error: {e.stderr}")
                    successful = False
                else:
                    self.add_or_update_file(file)
        successful = True
        return successful

    def add_or_update_file(self, file: File) -> None:
        """Adds a single new file to the library or update an existing one.

        Args:
            file (File): The file object to add
        """
        # If we're adding/updating a file, that means it must also exist physically
        file.was_deleted = False

        current_entry = self.db.get_file_by_path(file.path)
        if not current_entry:
            logger.info(f"Adding new file to library: {file.path}")
            file.needs_processing = True
        elif current_entry.mtime != file.mtime or current_entry.type != file.type:
            logger.info(f"Existing file has been modified and will be reprocessed: {file.path}")
            file.needs_processing = True
        else:
            logger.debug(f"File unchanged since last scan: {file.path}")
        self.db.add_or_update_file(file)

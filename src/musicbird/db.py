"""Database Abstractions and utilities.

This module provides the interface used by the other MusicBird components to read/write from a persistent Database.
The Abstract class LibraryLB serves as the interface used by other components, while individual DB implementations
(such as SQLiteLibrary) are derived from it.
"""

from abc import ABC, abstractmethod
import logging
from pathlib import Path
import sqlite3
from sqlite3.dbapi2 import Row
import sys
from typing import Dict, List, Tuple, Union

from .file import File, FileType

logger = logging.getLogger(__name__)


class LibraryDB(ABC):
    """Interface for communicating with a Database backend.

    This class defines all methods that clients can use to access the underlying Database.

    Note that the File path is used as a unique key, so there may only be one file for each path.
    """

    @abstractmethod
    def get_all_files(self) -> List[File]:
        """Get all files in the database.

        Returns:
            List[File]: A list of every file currently stored in the DB.
        """

    @abstractmethod
    def get_file_by_path(self, path: Path) -> Union[File, None]:
        """Get a file object by its path.

        Args:
            path (Path): The Path of the file that you want to get.

        Returns:
            Union[File, None]: The file object if present, None if that file is not in the DB.
        """

    @abstractmethod
    def get_files_by_type(self, filetype: FileType) -> List[File]:
        """Get all files of the specified FileType.

        Args:
            filetype (FileType): The kind of file you want to get.

        Returns:
            List[File]: A list of all Files of the given type.
        """

    @abstractmethod
    def get_files_needing_processing(self) -> List[File]:
        """Get all files that  have the needs_processing flag set.

        Returns:
            List[File]: A list of all Files that have the needs_processing flag set.
        """

    @abstractmethod
    def get_deleted_files(self) -> List[File]:
        """Get all files that have the was_deleted flag set.

        Returns:
            List[File]: A list of all Files that have the was_deleted flag set.
        """

    @abstractmethod
    def remove_file(self, file: File) -> None:
        """Remove this file from the DB.

        Args:
            file (File): The file to remove.
        """

    @abstractmethod
    def add_or_update_file(self, file: File) -> None:
        """Insert or update a file in the DB.

        Args:
            file (File): The file to add or update.
        """


class SQLiteLibrary(LibraryDB):
    _FILES_TABLE = "Files"
    _FILES_COLUMNS = {
        "path": "TEXT PRIMARY KEY",
        "filetype": "INT",
        "mtime": "INT",
        "needs_processing": "BOOLEAN",
        "was_deleted": "BOOLEAN"
    }

    def __init__(self, path: Path, delete: bool = False, pretend: bool = False) -> None:
        self.path = path

        if not delete and pretend:
            # Make a copy of the existing DB and save it to a in-memory DB
            self._init_db_con(pretend=False)
            files = self.get_all_files()
            self._init_db_con(pretend=True)
            for file in files:
                self.add_or_update_file(file)
        elif not delete and not pretend:
            # Default - just init the database
            self._init_db_con(pretend=False)
        elif delete and pretend:
            # Don't actually delete the database, just return an in-memory DB
            self._init_db_con(pretend=True)
        elif delete and not pretend:
            try:
                path.unlink(missing_ok=True)
                logger.info(f"Removed previous database at {self.path}")
            except FileNotFoundError:
                pass
            except OSError as e:
                logger.fatal((
                    f"Could not remove databse at {self.path}. "
                    f"Please delete the file manually to re-initialize the library. Error: {repr(e)}"
                ))
                raise e
            self._init_db_con()

        logger.debug(f"Initialzed SQLite3 database at {self.path}")

    def get_all_files(self) -> List[File]:
        fetched = self._make_query(f"SELECT * FROM {SQLiteLibrary._FILES_TABLE}")
        return [self._file_from_row(row) for row in fetched]

    def get_file_by_path(self, path: Path) -> Union[File, None]:
        fetched = self._make_query(f"SELECT * FROM {SQLiteLibrary._FILES_TABLE} WHERE path=?", (str(path),))
        if fetched:
            return self._file_from_row(fetched[0])
        else:
            return None

    def get_files_by_type(self, filetype: FileType):
        fetched = self._make_query(f"SELECT * FROM {SQLiteLibrary._FILES_TABLE} WHERE filetype=?", (filetype.value,))
        return [self._file_from_row(row) for row in fetched]

    def get_files_needing_processing(self):
        fetched = self._make_query(f"SELECT * FROM {SQLiteLibrary._FILES_TABLE} WHERE needs_processing")
        return [self._file_from_row(row) for row in fetched]

    def get_deleted_files(self):
        fetched = self._make_query(f"SELECT * FROM {SQLiteLibrary._FILES_TABLE} WHERE was_deleted")
        return [self._file_from_row(row) for row in fetched]

    def add_or_update_file(self, file: File) -> None:
        self._make_query((
            f"INSERT OR REPLACE INTO {SQLiteLibrary._FILES_TABLE} "
            "(path, filetype, mtime, needs_processing, was_deleted) VALUES (?,?,?,?,?)"
        ), (str(file.path), file.type.value, file.mtime, file.needs_processing, file.was_deleted))

    def remove_file(self, file: File) -> None:
        self._make_query(f"DELETE FROM {SQLiteLibrary._FILES_TABLE} WHERE path=?", (str(file.path),))

    def _make_query(self, query: str, params: Union[Dict, Tuple] = ()) -> Union[List, None]:
        """Perform a SQLite query with the given parameters.

        Args:
            query (str): [description]
            params (Union[Dict, Tuple], optional): Parameters in a format supported by sqlite3s execute().
                Defaults to an empty tuple.

        Raises:
            sqlite3.Error: If the query failed

        Returns:
            Union[List, None]: The returned rows. Might be None
        """
        try:
            with self._con:
                logger.debug(f"Running database query '{query}' with parameters {params}")
                result = self._con.execute(query, params).fetchall()
                return result
        except sqlite3.Error as e:
            logger.fatal(f"Error performing database query: {repr(e)}")
            raise e

    def _init_db_con(self, pretend: bool = False):
        """Initialize a datbase connection and ensure the required tables exist.

        Args:
            pretend (bool, optional): Whether the initialize the connection against a temporary in-memory DB.
                Defaults to False
        """
        columns = ', '.join([
            f"{column} {SQLiteLibrary._FILES_COLUMNS[column]}"
            for column in SQLiteLibrary._FILES_COLUMNS
        ])
        try:
            if pretend:
                self._con = sqlite3.connect(":memory:", check_same_thread=False)
            else:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                self._con = sqlite3.connect(self.path, check_same_thread=False)
            self._con.row_factory = sqlite3.Row
            with self._con:
                self._con.execute(f"CREATE TABLE IF NOT EXISTS {SQLiteLibrary._FILES_TABLE} ({columns})")
        except (sqlite3.Error, OSError) as e:
            logger.fatal(f"Error while accessing/initializing SQLite3 database at {self.path}: {repr(e)}")
            raise e

    @staticmethod
    def _file_from_row(row: Row) -> FileType:
        """Convert a row back into a full file object, including enums and Paths.
        """
        file = File(**row)
        file.path = Path(row["path"])
        file.type = FileType(row["filetype"])
        return file


def init(config: Dict, delete: bool = False, pretend: bool = False, exit_on_error: bool = False) -> LibraryDB:
    """Initialize the database connection based on the values provided in the config.

    Creates an apropiate LibraryDB object for the given backend in config and returns it.

    Args:
        config (Dict): MusicBirds configuration
        delete (bool, optional): Whether to re-initialize the DB and remove all previous records. Defaults to False.
        pretend (bool, optional): Whether to use a temporary database that
            does not store writes persistently for pretend mode. Defaults to False.
        exit_on_error (bool, optional): Whether to call sys.exit() if the initialization fails.
            If set to false, will raise exception instead. Defaults to False.

    Returns:
        LibraryDB: The library object
    """
    try:
        if config["database"] == "sqlite3":
            return SQLiteLibrary(config["sqlite3"]["path"], delete, pretend)
    except (OSError, sqlite3.Error) as e:
        if exit_on_error:
            sys.exit("Error initializing database")
        else:
            raise e

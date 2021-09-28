# pylint: disable=redefined-outer-name

from pathlib import Path
from typing import Dict, List

import pytest

from musicbird.db import LibraryDB, SQLiteLibrary
from musicbird.file import File, FileType


@pytest.fixture
def test_files():
    return [
        File(Path("lossy.mp3"), FileType.LOSSY, 12345, needs_processing=True, was_deleted=False),
        File(Path("also_lossy.mp3"), FileType.LOSSY, 234567, needs_processing=True, was_deleted=False),
        File(Path("lossless.flac"), FileType.LOSSLESS, 54321, needs_processing=False, was_deleted=True)
    ]


@pytest.fixture
def library_db(tmp_path):
    return SQLiteLibrary(Path(tmp_path).joinpath("db.sqlite3"))


def test_db_add(library_db: LibraryDB, test_files: List[File]):
    for file in test_files:
        library_db.add_or_update_file(file)
    assert sorted(test_files) == sorted(library_db.get_all_files())


def test_db_update(library_db: LibraryDB, test_files: List[File]):
    for file in test_files:
        library_db.add_or_update_file(file)
    test_files[0].needs_processing = False
    library_db.add_or_update_file(test_files[0])
    test_files[1].type = FileType.OTHER
    library_db.add_or_update_file(test_files[1])

    assert sorted(test_files) == sorted(library_db.get_all_files())


def test_db_remove(library_db: LibraryDB, test_files: List[File]):
    for file in test_files:
        library_db.add_or_update_file(file)
        library_db.remove_file(file)
    assert not library_db.get_all_files()


def test_db_get_file_by_path(library_db: LibraryDB, test_files: List[File]):
    for file in test_files:
        library_db.add_or_update_file(file)
        assert file == library_db.get_file_by_path(file.path)


def test_db_get_files_by_type(library_db: LibraryDB, test_files: List[File]):
    test_types: Dict[FileType, List] = {}
    for file in test_files:
        library_db.add_or_update_file(file)
        # Create a maping of FileTypes to all files of that type
        test_types.setdefault(file.type, []).append(file)

    for filetype in test_types:
        assert sorted(test_types[filetype]) == sorted(library_db.get_files_by_type(filetype))


def test_db_get_files_needing_processing(library_db: LibraryDB, test_files: List[File]):
    for file in test_files:
        library_db.add_or_update_file(file)

    assert sorted([f for f in test_files if f.needs_processing]) == sorted(library_db.get_files_needing_processing())


def test_db_get_deleted_files(library_db: LibraryDB, test_files: List[File]):
    for file in test_files:
        library_db.add_or_update_file(file)
    assert sorted([f for f in test_files if f.was_deleted]) == sorted(library_db.get_deleted_files())


def test_db_pretend(tmp_path, test_files: List[File]):
    # Initialize the DB and add some files
    library_db = SQLiteLibrary(Path(tmp_path).joinpath("db.sqlite3"))
    for file in test_files:
        library_db.add_or_update_file(file)
    del library_db

    # Make changes in pretend mode
    library_db = SQLiteLibrary(Path(tmp_path).joinpath("db.sqlite3"), pretend=True)
    modified_files = [
        File("lossy.mp3", FileType.LOSSY, 12345, needs_processing=False, was_deleted=False),
        File("also_lossy.mp3", FileType.OTHER, 234567, needs_processing=True, was_deleted=False),
    ]
    for file in modified_files:
        library_db.add_or_update_file(file)
    del library_db

    # Ensure that our changes did not persist
    library_db = SQLiteLibrary(Path(tmp_path).joinpath("db.sqlite3"))
    assert sorted(test_files) == sorted(library_db.get_all_files())


def test_db_delete(tmp_path, test_files: List[File]):
    # Initialize the DB and add some files
    library_db = SQLiteLibrary(Path(tmp_path).joinpath("db.sqlite3"))
    for file in test_files:
        library_db.add_or_update_file(file)
    del library_db

    library_db = SQLiteLibrary(Path(tmp_path).joinpath("db.sqlite3"), delete=True)
    assert not library_db.get_all_files()


def test_db_delete_and_pretend(tmp_path, test_files: List[File]):
    # Initialize the DB and add some files
    library_db = SQLiteLibrary(Path(tmp_path).joinpath("db.sqlite3"))
    for file in test_files:
        library_db.add_or_update_file(file)
    del library_db

    library_db = SQLiteLibrary(Path(tmp_path).joinpath("db.sqlite3"), delete=True, pretend=True)
    assert not library_db.get_all_files()
    del library_db

    library_db = SQLiteLibrary(Path(tmp_path).joinpath("db.sqlite3"))
    assert sorted(library_db.get_all_files()) == sorted(test_files)

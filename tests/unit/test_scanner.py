import os
from pathlib import Path
from typing import List, Tuple

from musicbird.db import LibraryDB
from musicbird.file import File, FileType
from musicbird.scanner import LibraryScanner


def test_fresh_scan(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_files = library_and_db[1]
    library_db = library_and_db[2]

    scanner = LibraryScanner(workdir.joinpath("library"), library_db)
    scanner.scan()

    result = library_db.get_all_files()
    assert sorted([f.path for f in result]) == sorted([file.path for file in library_files])

    for file in result:
        expected = [expected_file for expected_file in library_files if expected_file.path == file.path][0]
        assert file.type == expected.type
        assert file.needs_processing
        assert not file.was_deleted


def test_unchanged_scan(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_db = library_and_db[2]

    scanner = LibraryScanner(workdir.joinpath("library"), library_db)
    scanner.scan()
    first_scan = library_db.get_all_files()
    # Pretend we processed all files
    for file in first_scan:
        file.was_deleted = False
        file.needs_processing = False
        library_db.add_or_update_file(file)

    # Assert that second scan didn't change anything
    scanner.scan()
    second_scan = library_db.get_all_files()
    assert sorted(first_scan) == sorted(second_scan)


def test_deleted_scan(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_files = library_and_db[1]
    library_db = library_and_db[2]

    scanner = LibraryScanner(workdir.joinpath("library"), library_db)
    scanner.scan()
    first_scan = library_db.get_all_files()
    # Pretend we processed all files
    for file in first_scan:
        file.was_deleted = False
        file.needs_processing = False
        library_db.add_or_update_file(file)

    removed_file = library_files[0]
    removed_file.was_deleted = True
    os.remove(removed_file.path)

    scanner.scan()
    deleted = library_db.get_deleted_files()
    assert len(deleted) == 1
    assert deleted[0] == removed_file


def test_modified_scan(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_files = library_and_db[1]
    library_db = library_and_db[2]

    scanner = LibraryScanner(workdir.joinpath("library"), library_db)
    scanner.scan()
    first_scan = library_db.get_all_files()
    # Pretend we processed all files
    for file in first_scan:
        file.was_deleted = False
        file.needs_processing = False
        library_db.add_or_update_file(file)

    # Album at detection uses the filename. If we changed an albumart file
    # the scanner wouldn't change the type to other because it still sees it as albumart
    expected_modified = [file for file in library_files if file.type != FileType.ALBUMART][0]
    with open(expected_modified.path, 'w', encoding='utf-8') as f:
        f.write("Hello world")
    expected_modified.type = FileType.OTHER

    scanner.scan()
    actual_modified = library_db.get_files_needing_processing()
    assert len(actual_modified) == 1
    assert actual_modified[0].path == expected_modified.path
    assert actual_modified[0].type == expected_modified.type
    assert actual_modified[0].mtime != expected_modified.mtime

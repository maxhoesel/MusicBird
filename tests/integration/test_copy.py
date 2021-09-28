from pathlib import Path
from typing import Dict, List, Tuple

from musicbird.config import Config
from musicbird.copy import copy
from musicbird.file import File
from musicbird.db import LibraryDB, init as init_db
from musicbird.file import FileType
from musicbird.scanner import LibraryScanner
from musicbird.__main__ import main


def test_copy(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_files = library_and_db[1]
    library_db = library_and_db[2]

    config = Config(workdir.joinpath("config.yml")).config
    config["copy"]["album_art"] = True  # test every possible copy

    scanner = LibraryScanner(workdir.joinpath("library"), library_db)
    scanner.scan()

    assert copy(config, library_db)
    expected_files = [Path(str(file.path).replace("library", "dest", 1)) for file in library_files if
                      file.type in [FileType.LOSSY, FileType.OTHER, FileType.ALBUMART]]
    actual_files = []
    for path in workdir.glob("dest/**/*"):
        if path.is_file():
            actual_files.append(path)
    assert sorted(expected_files) == sorted(actual_files)

    # Add new file and check that it's copied
    workdir.joinpath("library/someNewFile").touch()
    scanner.scan()
    assert copy(config, library_db)
    assert workdir.joinpath("dest/someNewFile").is_file()

    # No more files are left to copy in DB
    assert not [file for file in library_db.get_files_needing_processing(
    ) if file.type in [FileType.LOSSY, FileType.OTHER, FileType.ALBUMART]]


def test_copy_pretend(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_files = library_and_db[1]
    library_db = library_and_db[2]

    config = Config(workdir.joinpath("config.yml")).config
    config["lossy_files"] = "copy"  # test every possible copy

    # Create a temporary "pretend" DB for use with the copy command
    # We also initialize the actual DB to ensure that no changes are written to it
    pretend_db = init_db(config, pretend=True)
    pretend_scanner = LibraryScanner(workdir.joinpath("library"), pretend_db)
    pretend_scanner.scan()

    library_scanner = LibraryScanner(workdir.joinpath("library"), library_db)
    library_scanner.scan()

    assert copy(config, pretend_db, pretend=True)

    expected_still_to_copy = [file.path for file in library_files if file.type in
                              [FileType.LOSSY, FileType.OTHER, FileType.ALBUMART]]
    actual_still_to_copy = [file.path for file in library_db.get_files_needing_processing() if file.type in
                            [FileType.LOSSY, FileType.OTHER, FileType.ALBUMART]]

    assert sorted(expected_still_to_copy) == sorted(actual_still_to_copy)


def test_copy_command(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_db = library_and_db[2]

    scanner = LibraryScanner(workdir.joinpath("library"), library_db)
    scanner.scan()

    args = ["-c", str(workdir.joinpath("config.yml")), "copy"]
    assert main(args)

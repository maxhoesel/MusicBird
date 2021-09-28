from pathlib import Path
from typing import List, Tuple

from musicbird.config import Config
from musicbird.copy import copy
from musicbird.db import LibraryDB, init as init_db
from musicbird.encode import encode
from musicbird.file import File
from musicbird.prune import prune
from musicbird.file import FileType
from musicbird.scanner import LibraryScanner
from musicbird.__main__ import main


def test_prune(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_files = library_and_db[1]
    library_db = library_and_db[2]
    config = Config(workdir.joinpath("config.yml")).config

    scanner = LibraryScanner(workdir.joinpath("library"), library_db)
    scanner.scan()
    copy(config, library_db)
    encode(config, library_db)

    # Test empty prune
    assert prune(config, library_db)
    expected_files = [file.get_dest_path(config) for file in library_files if file.type != FileType.ALBUMART]
    actual_files = []
    for path in workdir.glob("dest/**/*"):
        if path.is_file():
            actual_files.append(path)
    assert sorted(expected_files) == sorted(actual_files)

    # Remove file and check that it's pruned
    pruned_file = [file for file in library_files if file.type !=
                   FileType.ALBUMART][0]  # Album art is ignored by default
    pruned_file.path.unlink()
    scanner.scan()
    assert len(library_db.get_deleted_files()) == 1
    assert library_db.get_deleted_files()[0].path == pruned_file.path

    assert prune(config, library_db)
    assert not pruned_file.get_dest_path(config).is_file()
    assert not library_db.get_deleted_files()
    assert not library_db.get_file_by_path(pruned_file.path)


def test_prune_empty_dir_deletion(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_files = library_and_db[1]
    library_db = library_and_db[2]
    config = Config(workdir.joinpath("config.yml")).config
    config["lossy_files"] = "convert"  # test every possible prune option

    scanner = LibraryScanner(workdir.joinpath("library"), library_db)
    scanner.scan()
    copy(config, library_db)
    encode(config, library_db)

    dir_to_empty = [file.path.parent for file in library_files if file.path.parent.name != "library"][0]
    files_to_delete = [file for file in library_files if str(dir_to_empty) in str(file.path)]
    for file in files_to_delete:
        file.path.unlink()
    dir_to_empty.rmdir()

    scanner.scan()
    assert prune(config, library_db)

    deleted_dest_dir = files_to_delete[0].get_dest_path(config).parent
    assert not deleted_dest_dir.exists()
    assert not library_db.get_deleted_files()
    for file in files_to_delete:
        assert not library_db.get_file_by_path(file.path)


def test_prune_pretend(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_files = library_and_db[1]
    library_db = library_and_db[2]

    config = Config(workdir.joinpath("config.yml")).config
    library_scanner = LibraryScanner(workdir.joinpath("library"), library_db)
    library_scanner.scan()
    encode(config, library_db)
    copy(config, library_db)

    # Create a temporary "pretend" DB for use with the prune command
    pretend_db = init_db(config, pretend=True)
    pretend_scanner = LibraryScanner(workdir.joinpath("library"), pretend_db)

    pruned_file = [file for file in library_files if file.type !=
                   FileType.ALBUMART][0]  # Album art is ignored by default
    pruned_file.path.unlink()
    library_scanner.scan()
    pretend_scanner.scan()

    assert prune(config, pretend_db, pretend=True)
    # All files were processed in the pretend db
    assert not pretend_db.get_file_by_path(pruned_file.path)

    # The file is still in the main DB and on the FS
    assert library_db.get_file_by_path(pruned_file.path).was_deleted
    assert pruned_file.get_dest_path(config).exists()


def test_prune_command(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_db = library_and_db[2]

    scanner = LibraryScanner(workdir.joinpath("library"), library_db)
    scanner.scan()

    args = ["-c", str(workdir.joinpath("config.yml")), "prune"]
    assert main(args)

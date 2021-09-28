from pathlib import Path
import shutil
from typing import List, Tuple

from musicbird.config import Config
from musicbird.db import LibraryDB, init as init_db
from musicbird.file import File
from musicbird.encode import encode
from musicbird.file import FileType
from musicbird.scanner import LibraryScanner
from musicbird.__main__ import main


def test_encode(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_files = library_and_db[1]
    library_db = library_and_db[2]

    config = Config(workdir.joinpath("config.yml")).config
    config["lossy_files"] = "convert"  # test every possible encode option

    scanner = LibraryScanner(workdir.joinpath("library"), library_db)
    scanner.scan()

    assert encode(config, library_db)
    expected_files = [file.get_dest_path(config) for file in library_files if
                      file.type in [FileType.LOSSY, FileType.LOSSLESS]]
    actual_files = []
    for path in workdir.glob("dest/**/*"):
        if path.is_file():
            actual_files.append(path)
    assert sorted(expected_files) == sorted(actual_files)

    # Add new file and check that it's encoded
    lossless_file = [file for file in library_files if file.type == FileType.LOSSLESS][0]
    filename = lossless_file.path.stem

    shutil.copy(lossless_file.path, Path(str(lossless_file.path).replace(filename, "Copy of other lossless file")))
    scanner.scan()
    assert encode(config, library_db)

    assert Path(str(lossless_file.get_dest_path(config)).replace(filename, "Copy of other lossless file")).is_file()

    # No more files are left to copy in DB
    assert not [file for file in library_db.get_files_needing_processing(
    ) if file.type in [FileType.LOSSY, FileType.LOSSLESS]]


def test_encode_pretend(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_files = library_and_db[1]
    library_db = library_and_db[2]

    config = Config(workdir.joinpath("config.yml")).config
    config["lossy_files"] = "convert"  # test every possible encode

    # Create a temporary "pretend" DB for use with the encode command
    # We also initialize the actual DB to ensure that no changes are written to it
    pretend_db = init_db(config, pretend=True)
    pretend_scanner = LibraryScanner(workdir.joinpath("library"), pretend_db)
    pretend_scanner.scan()

    library_scanner = LibraryScanner(workdir.joinpath("library"), library_db)
    library_scanner.scan()

    assert encode(config, pretend_db, pretend=True)
    # All files were processed in the pretend db
    assert not [file for file in pretend_db.get_files_needing_processing() if file.type in [
        FileType.LOSSLESS, FileType.LOSSY]]

    expected_still_to_encode = [file.path for file in library_files if file.type in [FileType.LOSSLESS, FileType.LOSSY]]
    actual_still_to_encode = [file.path for file in library_db.get_files_needing_processing() if file.type in [
        FileType.LOSSLESS, FileType.LOSSY]]

    assert sorted(expected_still_to_encode) == sorted(actual_still_to_encode)


def test_encode_command(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_db = library_and_db[2]

    scanner = LibraryScanner(workdir.joinpath("library"), library_db)
    scanner.scan()

    args = ["-c", str(workdir.joinpath("config.yml")), "encode"]
    assert main(args)

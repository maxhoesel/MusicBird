from pathlib import Path
from typing import Dict, List, Tuple

from musicbird.db import LibraryDB
from musicbird.file import File
from musicbird.scan import scan
from musicbird.config import Config
from musicbird.__main__ import main


def test_scan(library_and_db: Tuple[Path, List[File], LibraryDB]):
    workdir = library_and_db[0]
    library_files = library_and_db[1]
    library_db = library_and_db[2]

    config = Config(workdir.joinpath("config.yml")).config
    assert scan(config, library_db)

    result = sorted([file.path for file in library_db.get_all_files()])
    assert result == sorted([file.path for file in library_files])


def test_scan_command(library: Tuple[Path, List[File]]):
    workdir = library[0]

    args = ["-c", str(workdir.joinpath("config.yml")), "scan"]
    assert main(args)

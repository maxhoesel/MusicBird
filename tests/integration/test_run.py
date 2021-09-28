from pathlib import Path
from typing import List, Tuple

from musicbird.config import Config
from musicbird.db import LibraryDB, init as init_db
from musicbird.file import File
from musicbird.run import run
from musicbird.__main__ import main


def test_run(library: Tuple[Path, List[File], LibraryDB]):
    workdir = library[0]
    library_files = library[1]

    config = Config(workdir.joinpath("config.yml")).config
    config["copy"]["album_art"] = True

    assert run(config)

    expected_files = [file.get_dest_path(config) for file in library_files]
    actual_files = []
    for path in workdir.glob("dest/**/*"):
        if path.is_file():
            actual_files.append(path)
    assert sorted(expected_files) == sorted(actual_files)

    library_db = init_db(config)
    assert not library_db.get_files_needing_processing()


def test_run_pretend(library: Tuple[Path, List[File], LibraryDB]):
    workdir = library[0]

    config = Config(workdir.joinpath("config.yml")).config

    assert run(config, pretend=True)
    assert not workdir.joinpath("dest").exists()


def test_run_command(library: Tuple[Path, List[File], LibraryDB]):
    workdir = library[0]

    args = ["-c", str(workdir.joinpath("config.yml")), "run"]
    assert main(args)

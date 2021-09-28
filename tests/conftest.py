# pylint: disable=redefined-outer-name

from pathlib import Path
from typing import Dict, List, Tuple
import shutil

import pytest
import yaml

from musicbird.db import LibraryDB, SQLiteLibrary
from musicbird.file import File, FileType


@pytest.fixture
def library_and_db(library) -> Tuple[Path, Dict[Path, Dict], LibraryDB]:
    """Same as library(), but also returns a LibraryDB object initialized to the local sqlite3 database
    """
    return library[0], library[1], SQLiteLibrary(Path(library[0]).joinpath("db.sqlite3"))


@pytest.fixture
def library(tmp_path) -> Tuple[Path, List[File]]:
    """Creates a temporary library that contains tes files to use.

    The returned path has the following directory structure:
    tmp_path/
      - library/ - Example library, copied from tests/files/library
      - config.yml - Minimal config file pointing to
      - db.sqlite3 - SQlite3 database used as the DB backend. Not initialized
      - dest/ - Referenced in config.yml, but not actually created. Output for conversion commands
    Returns a tuple, containing:
      - the test path
      - A list of File() objects for each file in the library
    """
    files_path = "tests/files"

    shutil.copytree(files_path, Path(tmp_path), dirs_exist_ok=True)
    config = {
        "source": str(Path(tmp_path).joinpath("library")),
        "destination": str(Path(tmp_path).joinpath("dest")),
        "sqlite3": {
            "path": str(Path(tmp_path).joinpath("db.sqlite3"))
        }
    }
    # Don' try to determine these dynamically, as doing so would involve calling determine_type().
    # We might have to test that method for functionality, so let's not rely on it
    library_files = [
        File(Path(tmp_path).joinpath("library/Artist/Album/cover.jpg"), FileType.ALBUMART),
        File(Path(tmp_path).joinpath("library/Artist/Album/noncover_image.jpg"), FileType.OTHER),
        File(Path(tmp_path).joinpath("library/Artist/Album/01 - A Track.flac"), FileType.LOSSLESS),
        File(Path(tmp_path).joinpath("library/Artist/Album/02 - Also a Track.flac"), FileType.LOSSLESS),
        File(Path(tmp_path).joinpath("library/Attributions.txt"), FileType.OTHER),
        File(Path(tmp_path).joinpath("library/track.mp3"), FileType.LOSSY),
    ]

    with Path(tmp_path).joinpath("config.yml").open("w", encoding='utf-8') as f:
        yaml.dump(config, f)
    return tmp_path, library_files

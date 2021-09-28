import hashlib
from pathlib import Path
from typing import List, Tuple

import pytest

from musicbird.config import Config
from musicbird.file import File, FileType
from musicbird.encoder import init as init_encoder


def test_type_detection(library: Tuple[Path, List[File]]):
    library_files = library[1]

    for file in library_files:
        testfile = File(file.path)
        testfile.determine_type()
        assert testfile.type == file.type


@pytest.mark.parametrize("encoder", ["opus", "mp3"])
def test_get_dest_path(library: Tuple[Path, List[File]], encoder):
    workdir = library[0]
    library_files = library[1]

    config = Config(workdir.joinpath("config.yml")).config
    config["encoder"] = encoder
    suffix = init_encoder(config).extension

    # pylint: disable=line-too-long
    expected_paths = [
        Path(str(file.path).replace("library", "dest", 1)).with_suffix(suffix) for file in library_files if file.type == FileType.LOSSLESS] + [
            Path(str(file.path).replace("library", "dest", 1))for file in library_files if file.type != FileType.LOSSLESS]
    actual_paths = []
    for file in library_files:
        actual_paths.append(file.get_dest_path(config))

    assert sorted(expected_paths) == sorted(actual_paths)


def test_copy(library: Tuple[Path, List[File]]):
    workdir = library[0]
    library_files = library[1]
    testfile = library_files[0]

    config = Config(workdir.joinpath("config.yml")).config

    testfile.copy_to_dest(config)
    dest = testfile.get_dest_path(config)

    with testfile.path.open('rb') as f:
        original_hash = hashlib.sha256(f.read()).digest()
    with dest.open('rb') as f:
        copied_hash = hashlib.sha256(f.read()).digest()
    assert original_hash == copied_hash

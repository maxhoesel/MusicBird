from pathlib import Path
from typing import List, Tuple
import ffmpeg

from musicbird.file import File, FileType
from musicbird.encoder import MP3Encoder, OpusEncoder


def test_mp3_vbr_encoder(library: Tuple[Path, List[File]]):
    library_files = library[1]
    config = {
        "vbr": True,
        "quality": 2
    }

    encoder = MP3Encoder(config)
    to_encode = [file.path for file in library_files if file.type in (FileType.LOSSLESS, FileType.LOSSY)]
    file = to_encode[0]  # Only encode a single file for faster test runs
    dest = Path(str(file).replace("library", "dest", 1)).with_suffix(encoder.extension)
    assert encoder.encode(file, dest)
    # There is no easy way to determine the encoding mode/quality from ffprobes output,
    # but we can still make a rough check via bitrate
    assert int(ffmpeg.probe(str(dest))["format"]["bit_rate"]) <= 170000


def test_mp3_cbr_encoder(library: Tuple[Path, List[File]]):
    library_files = library[1]
    config = {
        "vbr": False,
        "bitrate": "120k"
    }

    encoder = MP3Encoder(config)
    to_encode = [file.path for file in library_files if file.type in (FileType.LOSSLESS, FileType.LOSSY)]
    file = to_encode[0]  # Only encode a single file for faster test runs
    dest = Path(str(file).replace("library", "dest", 1)).with_suffix(encoder.extension)
    assert encoder.encode(file, dest)
    # There is no easy way to determine the encoding mode/quality from ffprobes output,
    # but we can still make a rough check via bitrate
    assert int(ffmpeg.probe(str(dest))["format"]["bit_rate"]) <= 140000


def test_opus_encoder(library: Tuple[Path, List[File]]):
    library_files = library[1]
    config = {
        "bitrate": "120k"
    }

    encoder = OpusEncoder(config)
    to_encode = [file.path for file in library_files if file.type in (FileType.LOSSLESS, FileType.LOSSY)]
    file = to_encode[0]  # Only encode a single file for faster test runs
    dest = Path(str(file).replace("library", "dest", 1)).with_suffix(encoder.extension)
    assert encoder.encode(file, dest)
    # There is no easy way to determine the encoding mode/quality from ffprobes output,
    # but we can still make a rough check via bitrate
    assert int(ffmpeg.probe(str(dest))["format"]["bit_rate"]) <= 140000

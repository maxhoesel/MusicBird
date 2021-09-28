"""Provides a representation/abstraction layer for files in the underlying Filesystem.

This modules main purpose is to provide the File class, which represents a file in the source music library.
All file-based operations should be performed via File's methods.
"""

from enum import Enum
import logging
import os
from pathlib import Path
from shutil import copy
from typing import Dict

import ffmpeg

from .encoder import init as init_encoder

logger = logging.getLogger(__name__)

LOSSY_CODECS = [
    "mp3",
    "opus",
    "ogg",
    "wmav1",
    "wmav2",
    "aac"
]
LOSSLESS_CODECS = [
    "flac",
    "wav",
    "aiff",
]

ALBUMART_FILENAMES = [
    "cover",
    "album",
    "albumart",
]
ALBUMART_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
]


class FileType(Enum):
    """Enum used to set the type of file, as far as MusicBird is concerned.

    In order to process various kinds files, each File has a specific type
    attached to it. This enum provides all possible values for that attribute.
    """

    LOSSY = 1
    """A lossy audio file(MP3, Opus, WAV, ...)"""

    LOSSLESS = 2
    """A lossless audio file(FLAC, WAV, AIFF)"""

    ALBUMART = 3
    """An image file that's most likely the album art cover"""

    OTHER = 4
    """Any other kind of file"""


class File:
    """Provides an abstraction layer for all operations on the music library source files.

    A File object represents one file in the original music library. File is used used
    to store information about the files relevant attributes as well as to provide
    methods for processing each file. File objects are usually generated during scan
    operations and are then stored in the Database, from where other actions can retrieve and process them.

    File objects can be compared with each other, and are sortable(using the path as a sorting base).
    Since they are mutable, they are not hashable and cannot be used as keys in dictionaries, among other things.

    Attributes:
        path: Path object containing the full filesystem Path to the underlying file.
        filetype: Kind of file, represented by a FileType enum.
        mtime: Last time the file was modified. Stored as a UNIX timestamp(Integer).
        needs_processing: Bool indicating whether the file requires processing.
            This usually means that file was modified/added recently.
        was_deleted: Bool indicating whether the file was deleted and no longer exists on the fs.
            Used to track deletions.
    """

    def __init__(self, path: Path, filetype: FileType = None, mtime: int = None,
                 needs_processing: bool = False, was_deleted: bool = False) -> None:
        """Creates a new File object, representing a physical file in the source libary.

        Args:
            path(Path): Path object containing the full filesystem Path to the underlying file.
            filetype(FileType, optional): The kind of the file(lossless/lossy/...). Use the FileType enum for this.
            mtime(int, optional): Last time the file was modified as a UNIX timestamp(int).
                Will read the current mtime if not specified.
            needs_processing(bool, optional): Bool indicating whether the file requires processing.
                This usually means that file was modified/added recently.
            was_deleted(bool, optional): Bool indicating whether the file was deleted and no longer exists on the fs.
                Used to track deletions.
        """
        self.path = path
        self.needs_processing = needs_processing
        self.was_deleted = was_deleted
        self.type = filetype

        if not mtime:
            self.mtime = round(os.path.getmtime(path))
        else:
            self.mtime = mtime

    def copy_to_dest(self, config: Dict) -> bool:
        """Copy the file to the destination library.

        Copies the file to its relative path in the destination library specified in config.
        For example, if the original file is in ~/music/Artist1/Album1/Track1.mp3 and the
        destination directory is ~/music_converted, then the file will be copied to
        ~/music_converted/Artist1/Album1/Track1.mp3. Any missing directories will be created.

        Args:
            config(dict): Musicbird config as a dict.

        Returns:
            bool: True if the copy operation was successful, False if not.
        """
        if self.was_deleted:
            logger.error(f"File {self.path} was deleted and cannot be copied")
            return False

        dest = self.get_dest_path(config)
        logger.info(f"Copying file: {self.path}")
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            copy(self.path, dest)
        except OSError as e:
            logger.error(f"Could not copy file {self.path} to {dest}: {repr(e)}")
            return False
        return True

    def encode_to_dest(self, config: Dict) -> bool:
        """Encode the file and save it in the destination library.

        Encodes the file to its relative path in the destination library specified in config.
        For example, if the original file is in ~/music/Artist1/Album1/Track1.flac and the
        destination directory is ~/music_converted, then the file will be encoded to
        ~/music_converted/Artist1/Album1/Track1.mp3/opus/...

        Any missing directories will be created.

        Args:
            config(dict): Musicbird config as a dict.

        Returns:
            bool: True if the encode operation was successful, False if not.
        """
        dest = self.get_dest_path(config)
        encoder = init_encoder(config)
        return encoder.encode(self.path, dest)

    def get_dest_path(self, config: Dict) -> Path:
        """Get the files path in the destination library.

        Generates the path for the mirror copy of this file in the destination library, as specified by the config.
        For example, if the original file is in ~/music/Artist1/Album1/Track1.mp3 and the
        destination directory is ~/music_converted, then the destination path would be
        ~/music_converted/Artist1/Album1/Track1.mp3.

        If the file due to be encoded, the file extension is also changed to reflect this(e.g. .flac -> .mp3)

        Args:
            config(dict): The musicbird configuration in dict form.

        Returns:
            bool: A Path object pointing to the path of the destination file.
        """
        src = config["source"]
        dest = config["destination"]

        if not self.type:
            self.determine_type()

        path = Path(str(self.path).replace(str(src), str(dest), 1))
        if self.type == FileType.LOSSLESS or (self.type == FileType.LOSSY and config["lossy_files"] == "convert"):
            path = path.with_suffix(init_encoder(config).extension)
        return path

    def determine_type(self) -> None:
        """Detects the type of file and sets the filetype attribute accordingly.

        Tries to figure out the kind of file present at self.path based on a few tests,
        then sets the filetype attribute to the best match. Among other things, it uses
        ffmpeg to parse media files and checks the filename for patterns(such as cover.jpg) files.

        Since this does actually need to physically access the file, it is not called during File
        initialization. This method is especially useful if you are adding a new file and don't know its exact type yet.
        """
        if self.path.name.lower() in [name + ext for name in ALBUMART_FILENAMES for ext in ALBUMART_EXTENSIONS]:
            self.type = FileType.ALBUMART
            return

        try:
            probe = ffmpeg.probe(self.path)
        except (OSError, ffmpeg.Error) as e:
            if "Invalid data found when processing input" in str(e.stderr):
                # ffmpeg can't handle the file, so its safe to assume that it's something else. Binary, text, whatever
                self.type = FileType.OTHER
                return
            else:
                logger.error(
                    f"Failure trying to determine type for file {self.path}, falling back to type 'OTHER': {repr(e)}.")
                self.type = FileType.OTHER

        # Generate a set of audio codecs used in the file. Regular audio files usually only have a single stream.
        audio_codecs = list({probe["streams"][i]["codec_name"] for i in range(len(probe["streams"]))
                            if probe["streams"][i]["codec_type"] == "audio"})

        if not audio_codecs:
            self.type = FileType.OTHER  # Some other non-audio file recognized by FFMPEG
        elif len(audio_codecs) > 1:
            logger.warning(f"File has multiple audio streams: {self.path}. Cannot encode safely, Will copy instead.")
            self.type = FileType.OTHER
        elif audio_codecs[0] in LOSSLESS_CODECS:
            self.type = FileType.LOSSLESS
        elif audio_codecs[0] in LOSSY_CODECS:
            self.type = FileType.LOSSY
        else:
            self.type = FileType.OTHER  # Audio file that we don't recognize. Copy instead

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, File):
            return False
        return (self.path == o.path
                and self.type == o.type
                and self.mtime == o.mtime
                and self.was_deleted == o.was_deleted
                and self.needs_processing == o.needs_processing
                )

    def __lt__(self, o: object) -> bool:
        return self.path < o.path

    def __gt__(self, o: object) -> bool:
        return self.path > o.path

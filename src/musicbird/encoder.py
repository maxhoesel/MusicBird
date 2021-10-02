"""Interfaces for encoding audio files.

This module provides the interface used by the other MusicBird components to encode audio files.
The Abstract class Encoder serves as the interface used by other components, while individual Encoder implementations
(such as MP3Encoder) are derived from it.
"""
from abc import ABC, abstractmethod
import logging
from pathlib import Path
import subprocess
import re
import sys
from typing import Dict

import ffmpeg

logger = logging.getLogger(__name__)


class Encoder(ABC):
    """Interface for interacting with an Audio file Encoder.

    All encode operations are intended to be done using the methods defined by this class
    """

    extension = ""

    @abstractmethod
    def encode(self, src: Path, dest: Path) -> bool:
        """Encode the file at src to dest.

        Calls the encoders backend and converts the source file, then saves the output at the destination directory.

        Args:
            src (Path): The file to encode.
            dest (Path): The Path at which to store the encoded file.

        Returns:
            bool: True if the operation was successful, False if not.
        """

    @staticmethod
    def mkdir(dest: Path) -> bool:
        """Create the directory for the dest file.

        Returns:
            bool: Whether the creatin was successful
        """
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(f"Could not create directory to encode file {dest}: {repr(e)}")
            return False
        return True


class FFmpegEncoder(Encoder):
    """Base class for all encoders utilizing ffmpeg.

    Child encoders can inherit from this class and set their parameters accordingly.
    """
    # We might need to use config in this class in the future, so keep it in
    # pylint: disable=unused-argument

    def __init__(self, config: Dict) -> None:
        super().__init__()
        self.ffmpeg_args = {}

        # Check if we can access ffmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except FileNotFoundError as e:
            logger.fatal("Could not access ffmpeg. Pease make sure that it is installed")
            raise e
        except subprocess.CalledProcessError as e:
            logger.fatal(f"Could not verify that ffmpeg is ready. Error: {repr(e)}")
            raise e

    def encode(self, src: Path, dest: Path) -> bool:
        if not self.mkdir(dest):
            return False
        try:
            logger.debug(f"Encoding to {str(dest)} with arguments {self.ffmpeg_args}")
            stream = ffmpeg.input(str(src))
            stream = ffmpeg.output(stream, str(dest), **self.ffmpeg_args)
            stream = ffmpeg.overwrite_output(stream)
            ffmpeg.run(stream, quiet=True)
        except ffmpeg.Error as e:
            logger.error(f"Failed to encode file {src}. ffmpeg error: \n {e.stderr}")
            return False
        return True


class MP3Encoder(FFmpegEncoder):
    def __init__(self, config: Dict) -> None:
        super().__init__(config)
        self.extension = ".mp3"
        self.ffmpeg_args["acodec"] = "libmp3lame"
        if config["vbr"]:
            self.ffmpeg_args["q:a"] = config["quality"]
        else:
            self.ffmpeg_args["audio_bitrate"] = config["bitrate"]


class OpusEncoder(FFmpegEncoder):

    opusenc_checked = False
    use_opusenc = False

    def __init__(self, config: Dict) -> None:
        super().__init__(config)

        self.extension = ".opus"

        if self._init_opusenc():
            self.opus_args = [
                "--bitrate", re.sub('\D', '', config["bitrate"]),  # Strip k postfix from bitrate
            ]
        else:
            # FFmpeg fallback
            self.ffmpeg_args["acodec"] = "libopus"
            self.ffmpeg_args["audio_bitrate"] = config["bitrate"]

    def encode(self, src: Path, dest: Path) -> bool:
        if self.use_opusenc:
            if not self.mkdir(dest):
                return False

            args = ["opusenc", str(src), str(dest.with_suffix(self.extension))] + self.opus_args
            try:
                subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except (subprocess.CalledProcessError, OSError) as e:
                logger.error(f"fFailed to encode file {src}. opusenc error: \n {repr(e)}")
                return False
            return True
        else:
            return super().encode(src, dest)

    def _init_opusenc(self) -> bool:
        """Look for opusenc and set the encoder to use it if available.

        FFmpegs libopus encoder does not support embedding album art as of late 2021.
        To work around this, we use opusenc directly if it is installed. If not,
        we issue a warning and fallback to ffmpeg.

        Returns:
            bool: Whether opusenc can be used.
        """

        # Use a classvar to only check for opusenc once every run.
        # If it's not there the first, it's not gonna be there at all.
        if OpusEncoder.opusenc_checked:
            return OpusEncoder.use_opusenc

        try:
            subprocess.run(["opusenc", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.warning((
                "opusenc does not appear to be installed. Falling back to ffmpeg encoding."
                "Please install 'opus-tools' if you want embedded album art support in Opus files"
            ))
            OpusEncoder.use_opusenc = False
        else:
            OpusEncoder.use_opusenc = True
        finally:
            OpusEncoder.opusenc_checked = True
        return OpusEncoder.use_opusenc


def init(config, exit_on_error: bool = True) -> Encoder:
    """Initialize an encoder object based on the values provided in the config.

    Creates an apropiate LibraryDB object for the given backend in config and returns it.

    Args:
        config (Dict): MusicBirds configuration
        exit_on_error (bool, optional): Whether to call sys.exit() if the initialization fails.
            If set to false, will raise exception instead. Defaults to False.

    Returns:
        Encoder: The Encoder object
    """
    try:
        if config["encoder"] == "mp3":
            return MP3Encoder(config["mp3"])
        elif config["encoder"] == "opus":
            return OpusEncoder(config["opus"])
    except (OSError, ffmpeg.Error) as e:
        if exit_on_error:
            sys.exit("Error initializing database")
        else:
            raise e

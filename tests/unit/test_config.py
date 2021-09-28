import json
from pathlib import Path
import subprocess
from typing import Dict, List, Tuple

import pytest
from schema import SchemaError
import yaml

from musicbird.config import Config
from musicbird.__main__ import main
from musicbird.file import File


@pytest.mark.parametrize("invalid_entries", [
    {"source": 42},
    {"database": "notvalid"},
    {"wrongkey": "uh oh"}
])
def test_fail_on_invalid_config(library: Tuple[Path, List[File]], invalid_entries: Dict):
    workdir = library[0]
    with workdir.joinpath("config.yml").open() as f:
        config = {**yaml.safe_load(f), **invalid_entries}
    with workdir.joinpath("config.yml").open("w", encoding="utf-8") as f:
        yaml.dump(config, f)

    with pytest.raises(SchemaError):
        Config(workdir.joinpath("config.yml"))


def test_config_print_command(library: Tuple[Path, List[File]]):
    workdir = library[0]

    with workdir.joinpath("config.yml").open() as f:
        config: Dict = yaml.safe_load(f)
    args = ["musicbird", "-c", str(workdir.joinpath("config.yml")), "config", "print", "--format", "json"]
    result = subprocess.run(args, check=True, capture_output=True)
    assert config.items() <= json.loads(result.stdout).items()


def test_config_generate_command(tmp_path):
    output = Path(tmp_path).joinpath("config.yml")
    args = ["config", "generate", "-o", str(output)]
    assert main(args)

    # Fail if config file already exists
    with pytest.raises(SystemExit):
        main(args)

    args.append("--force")
    assert main(args)

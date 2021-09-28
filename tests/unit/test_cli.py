import subprocess

from musicbird import __version__


def test_command_entrypoint():
    args = ["musicbird", "--version"]
    result = subprocess.run(args, check=True, capture_output=True)
    assert __version__ == result.stdout.decode(encoding="utf-8").rstrip('\n')


def test_module_call():
    args = ["python3", "-m", "musicbird", "--version"]
    result = subprocess.run(args, check=True, capture_output=True)
    assert __version__ == result.stdout.decode(encoding="utf-8").rstrip('\n')

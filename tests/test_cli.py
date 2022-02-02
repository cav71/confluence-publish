import pytest
from confluence_publish import cli, main

DATADIR = __name__


def test_cli_help(scripter):
    script = scripter / "-m confluence_publish.main"
    result = script.run([ "--help" ])
    scripter.compare(result, populate=True, is_help=True)


def test_subparsers(scripter):
    from confluence_publish.main import parse_args

    options = parse_args(["publish"])
    assert options.commit is None

    options = parse_args(["publish", "--commit"])
    assert options.commit is True

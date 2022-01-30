import pytest
from confluence_publish import cli, main

DATADIR = __name__


def test_cli_help(scripter):
    script = scripter / "-m confluence_publish.main"
    result = script.run([ "--help" ])
    scripter.compare(result, populate=True)

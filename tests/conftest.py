import collections
import contextlib
import os
from pathlib import Path
import subprocess
import sys
from typing import List, Union, Optional

import pytest


@pytest.fixture()
def datadir(request):
    basedir = Path(__file__).parent / "data"
    if os.getenv("DATADIR"):
        basedir = Path(os.getenv("DATADIR"))
    basedir = basedir / getattr(request.module, "DATADIR", "")
    return basedir


@pytest.fixture()
def scripter(request, tmp_path_factory, datadir):
    """handles script (cli) execution

    def test(scripter):
        script = scripter / "script-file.py"

        # run the script collecting the stdout and stderr
        result = script.run(["--help"]) # this will execute:
                                        #   script-file.py --help
        assert result.out and result.err


    """
    Result = collections.namedtuple("R", "out,err,code")

    class ScripterError(Exception):
        pass

    class MissingItemError(ScripterError):
        pass

    class Result:
        def __init__(self, outfile: Path, errfile: Path, errcode: int = 0):
            self.outfile = outfile
            self.errfile = errfile
            self.errcode = errcode

        @property
        def out(self) -> str:
            return self.outfile.read_text()

        @property
        def err(self) -> str:
            return self.errfile.read_text()

        def as_txt(self, what: str = "both") -> str:
            txt = f"*=> ERRCODE {self.errcode}"
            if what in { "both", "stdout"}:
                txt += "" if txt.endswith("\n") else "\n"
                txt += "*=> STDOUT\n"
                txt += self.out

            if what in { "both", "stderr"}:
                txt += "" if txt.endswith("\n") else "\n"
                txt += "*=> STDERR\n"
                txt += self.err
            txt += "" if txt.endswith("\n") else "\n"
            return txt

    class Script:
        def __repr__(self):
            return (
                f"<{self.__class__.__name__} script={self.script} at {hex(id(self))}>"
            )

        def __init__(
            self,
            script: Union[str, Path],
            workdir: Union[str, Path],
            datadir: Union[str, Path],
            py3: Union[str, Path],
        ):
            self.script = script
            self.workdir = Path(workdir)
            self.datadir = Path(datadir)
            self.py3 = Path(py3)
            if not (str(self.script).startswith("-m") or Path(script).exists()):
                raise MissingItemError(f"script file {script} not found")

        def cmd(self, args: Optional[List[Union[str, Path]]] = None) -> List[str]:
            script = (
                ["-m", self.script[3:]]
                if str(self.script).startswith("-m")
                else [self.script]
            )
            return [str(a) for a in [self.py3, *script, *(args or [])]]

        def run(
            self, args: List[Union[str, Path]], cwd: Optional[Union[Path, str]] = None
        ):
            cmd = self.cmd(args)

            with contextlib.ExitStack() as stack:
                fpout = stack.enter_context((self.workdir / "stdout.txt").open("w"))
                fperr = stack.enter_context((self.workdir / "stderr.txt").open("w"))
                self.p = subprocess.Popen(
                    cmd,
                    cwd=self.workdir if cwd is True else cwd,
                    stdout=fpout,
                    stderr=fperr,
                )
                self.p.communicate()

            return Result(
                self.workdir / "stdout.txt",
                self.workdir / "stderr.txt",
                self.p.returncode,
            )

    class Scripter:
        def __init__(
            self, srcdir: Path, datadir: Path, nodename: str, py3: str = sys.executable
        ):
            self.srcdir = srcdir
            self.datadir = datadir
            self.nodename = nodename
            self.py3 = py3

        def __truediv__(self, path: Union[Path, str]) -> Script:
            if str(path).startswith("-m "):
                script = path
                basetmp = str(path)[3:]
            else:
                script = self.srcdir / path
                basetmp = Path(path).with_suffix("").name
            tmpdir = tmp_path_factory.mktemp(basetmp, numbered=True)
            return Script(script, tmpdir, self.datadir, self.py3)

        def compare(
            self,
            result: Result,
            subdir: Optional[Union[Path, str]] = True,
            populate: bool = False,
            overwrite: bool = False,
            what: str = "both"
        ):
            srcdir = (
                self.datadir / self.nodename
                if subdir is True
                else self.datadir / subdir
                if subdir
                else self.datadir
            )

            target = srcdir / "output.txt"
            if populate:
                srcdir.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    target.write_text(result.as_txt(what))
            right = target.read_text()
            left = result.as_txt(what)

            if overwrite and (left != right):
                target.write_text(result.as_txt(what))

            assert left == right

    return Scripter(Path(request.module.__file__).parent, datadir, request.node.name)


def pytest_configure(config):
    config.addinivalue_line("markers", "manual: test intended to run manually")


def pytest_collection_modifyitems(config, items):
    if config.option.keyword or config.option.markexpr:
        return  # let pytest handle this

    for item in items:
        if "manual" not in item.keywords:
            continue
        item.add_marker(pytest.mark.skip(reason="manual not selected"))

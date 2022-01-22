import ast
import logging
import dataclasses as dc
from pathlib import Path

# import docutils.core
#
import markdown2
# import yaml


log = logging.getLogger()



class LitteralException(Exception):
    pass


class InvalidLitteralValue(LitteralException):
    pass


@dc.dataclass
class Litterate:
    title : str
    summary : str
    meta : dc.field(default_factory=dict)
    body : str   # <- generated by md2litterate (md or html) or rst2litterate (html)
    mode : str

    def __setattr__(self, key, value):
        if key == "mode":
            expected = [ "", "html", "md"]
            if value not in expected:
                raise InvalidLitteralValue("invalid value", value, expected)


def get_doc(txt: str) -> str:
    """extracts the __doc__ part in a txt (python code)

    Args:
        txt (str): string to be parsed as python script

    Returrns:
        str - string extracted from __doc__
    """
    class MyVisitor(ast.NodeVisitor):
        def visit_Module(self, node):
            self.doc = ast.get_docstring(node)

    visitor = MyVisitor()
    visitor.visit(ast.parse(txt))
    doc = getattr(visitor, 'doc', None) or ''
    return doc


def load_doc(path: Path) -> str:
    """loads and extract the __doc__ part from path

    Args:
        path (Path): file location
    Returns:
        str - docstring from path
    """
    with path.open() as fp:
        txt = fp.read()
    return get_doc(txt)


def process_markdown(txt: Path):
    from markdown2 import Markdown
    md = Markdown(extras=['metadata'])
    html = md.convert(txt)
    return html, getattr(md, "metadata", None)

############################


def any2litterate(txt):
    """process a document with == Meta == tag"""
    lit = Litterate()
    if not txt:
        return lit, None

    # the first line in the doc is the summary
    lit.summary = (txt.strip().split("\n") or [""])[0]

    # in the meta dictionary, groups are unlimted elements list, category as single string
    aslist = [ ("groups", None,), ("category", (0, 1)) ]

    lines = [ l.rstrip() for l in txt.strip().split("\n") ]
    lit.meta, lines = popmeta(lines, aslist=aslist)
    return lit, lines


def md2litterate(txt, embedd=False):
    """process the markdown into a Litterate instance"""
    lit, lines = any2litterate(txt)
    md = markdown.Markdown(extensions = ['markdown.extensions.meta'])
    html = md.convert("\n".join(lines))
    if embedd:
        lit.body = "\n".join(lines)
        lit.mode = "md"
    else:
        lit.body = html
        lit.mode = "html"
    return lit


def rst2litterate(txt):
    """process txt (rst) into a data and html"""
    lit, lines = any2litterate(txt)
    # we extract the body part (it should have all the __doc__ rendered
    root = docutils.core.publish_parts(source="\n".join(lines), writer_name="html")
    lit.body = root["body"]
    lit.mode = "html"
    return lit
import pytest

from confluence_publish import doc2lit


def test_getdoc(datadir):
    txt = """
'''A doc example
with more line
'''

if __name__ == "__main__":
    pass
"""
    assert (
        doc2lit.get_doc(txt)
        == """
A doc example
with more line
""".strip()
    )


def test_load_doc(datadir):
    txt = doc2lit.load_doc(datadir / "testdoc.py")
    assert (
        txt
        == """
---
title: a title
author: an author name
multi: >
  a multiline
    text with indentation
      on multiple lines
---

This is a simple test doc to use
  for testing
""".strip()
    )

@pytest.mark.parametrize("kind",
        ["md", "rst"])
def test_popmeta(datadir, kind):
    src = datadir / {
        "rst": "sample-script-with-rst.py",
        "md": "sample-script-with-markdown.py",
    }[kind]
    txt = doc2lit.load_doc(src)
    meta, text = doc2lit.popmeta(txt, parse=False)
    assert meta.strip() == """
title: a title
author: an author name
multiline: >
  a multiline
    text with indentation
      on multiple lines
  this is the last line
""".strip()

    meta, text = doc2lit.popmeta(txt, parse=True)
    assert set(meta) == { "author", "title", "multiline"}


    assert { k:meta[k] for k in {"author", "title"} } == {
        'author': 'an author name',
        'title': 'a title'
    }

    assert meta["multiline"] == """
a multiline
    text with indentation
      on multiple lines
  this is the last line
""".strip()

    if kind == "rst":
        assert text.strip() == """
~~~~~~
Sample
~~~~~~

This is an example of rst script published in confluence.
""".strip()
    else:
        assert text.strip() == """
## Sample

This is an example of md script published in confluence.
""".strip()


def test_md2lit(datadir):
    txt = doc2lit.load_doc(datadir / "sample-script-with-markdown.py")
    lit = doc2lit.md2lit(txt)

    assert {
        "title": "a title",
        "author": "an author name",
        "multiline": """a multiline
    text with indentation
      on multiple lines
  this is the last line""" } == lit.meta
    assert """<h2>Sample</h2>

<p>This is an example of md script published in confluence.</p>
""" == lit.body



def test_rst2lit(datadir):
    src = datadir / "sample-script-with-rst.py"
    doc2lit.rst2lit(src.read_text())
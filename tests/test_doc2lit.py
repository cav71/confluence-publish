from confluence_publish import doc2lit


def test_getdoc(datadir):
    txt = """
'''A doc example
with more line
'''

if __name__ == "__main__":
    pass
"""
    assert doc2lit.get_doc(txt) == """
A doc example
with more line
""".strip()


def test_load_doc(datadir):
    txt = doc2lit.load_doc(datadir / "testdoc.py")
    assert txt == """
a simple test doc

This is a simple test doc to use
  for testing

---
title: a title
author: an author name
multi: a multiline
    text with indenration
      on multiple lines
---
""".strip()


def test_process_markdown(datadir):
    txt = doc2lit.load_doc(datadir / "testdoc.py")
    html, meta = doc2lit.process_markdown(txt)
    assert html == "<p>This is a simple test doc to use\n  for testing</p>\n"
    assert meta == {'author': 'an author name',
                    'multi': 'a multiline\n    text with indentation\n      on multiple lines',
                    'title': 'a title'}
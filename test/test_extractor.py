# coding=utf-8

from babel._compat import StringIO
from pybabel_angularjs.extractor import extract_angularjs


def test_extract_no_tags():
    buf = StringIO('<html></html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == []


def test_simple_string():
    buf = StringIO('<html><div i18n>hello world!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', 'hello world!', [])
    ]


def test_comments():
    buf = StringIO('<html><div i18n="page title">hello world!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', 'hello world!', ['page title'])
    ]


def test_nested_tags():
    buf = StringIO('<html><div i18n>hello <strong>Beautiful</strong> world!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', 'hello <strong>Beautiful</strong> world!', [])
    ]


def test_collapse_whitespaces():
    buf = StringIO('<html><div i18n>  \n\t\t  hello    <strong>Beautiful</strong> \n\t\t  world!\n\t\t  </div>  </html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', 'hello <strong>Beautiful</strong> world!', [])
    ]


def test_utf8_encoding():
    buf = StringIO('<html><div i18n>Příliš žluťoučký kůň úpěl ďábelské ódy.</div></html>')
    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', u'Příliš žluťoučký kůň úpěl ďábelské ódy.', [])
    ]


def test_attribute():
    buf = StringIO('<html><div title="some title">hello world!</div></html>')
    messages = list(extract_angularjs(buf, [], [], {"include_attributes": "title"}))
    assert messages == [
        (1, 'gettext', 'some title', ["title"])
    ]

# coding=utf-8

from babel._compat import StringIO
from pybabel_angularjs.extractor import extract_angularjs, TagNotAllowedException


def test_check_tags_in_content_error():
    buf = StringIO('<html><div title="hello world!" i18n> hello <br><strong><div>world</div></strong>!\n</div>\n<div alt="hello world!" i18n> hello world!</div></html>')

    try:
        messages = list(extract_angularjs(buf, [], [], {"include_attributes": "title alt"}))
    except TagNotAllowedException:
        assert True


def test_check_tags_in_content_ok():
    buf = StringIO('<html><div title="hello world!" i18n> hello <br><strong>world</strong>!\n</div>\n<div alt="hello world!" i18n> hello world!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {"include_attributes": "title alt"}))
    assert messages == [
        (1, 'gettext', u'hello world!', ['title']),
        (1, 'gettext', u'hello <br><strong>world</strong>!', []),
        (3, 'gettext', u'hello world!', ['alt']),
        (3, 'gettext', u'hello world!', [])
    ]


def test_get_string_positions():
    buf = StringIO('<html>  \n\n\n<div title="hello <br> world!" i18n> \n   hello      world!\n</div>\n<div alt="   hello\n world  \t!" i18n> hello world! ěščřžýá</div></html>')

    messages = list(extract_angularjs(buf, [], [], {"include_attributes": "title alt"}))
    assert messages == [
        (4, 'gettext', u'hello <br> world!', ['title']),
        (4, 'gettext', u'hello world!', []),
        (7, 'gettext', u'hello world !', ['alt']),
        (7, 'gettext', u'hello world! ěščřžýá', [])
    ]


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

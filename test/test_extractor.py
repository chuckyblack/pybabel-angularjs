# -*- coding: utf-8 -*-
from babel._compat import StringIO

from pybabel_angularjs.extractor import extract_angularjs

default_keys = []


def test_extract_no_tags():
    buf = StringIO('<html></html>')

    messages = list(extract_angularjs(buf, default_keys, [], {}))
    assert messages == []


def test_simple_string():
    buf = StringIO('<html><div data-translate>hello world!</div></html>')

    messages = list(extract_angularjs(buf, default_keys, [], {}))
    assert messages == [
        (1, u'gettext', 'hello world!', []),
    ]


def test_attr_value():
    """We should not translate tags that have *data-translate* as the value of an
    attribute.
    """
    buf = StringIO('<html><div id="data-translate">hello world!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == []


def test_attr_value_plus_directive():
    """Unless they also have a *data-translate* directive.
    """
    buf = StringIO(
        '<html><div id="data-translate" data-translate>'
        'hello world!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', 'hello world!', [])
    ]


def test_plural_form():
    buf = StringIO(
        '<html><div data-translate data-translate-plural='
        '"hello {$count$} worlds!">hello one world!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'ngettext',
         ('hello one world!',
          'hello {$count$} worlds!'),
         [])
    ]


def test_comments():
    buf = StringIO(
        '<html><div data-translate data-translate-comment='
        '"What a beautiful world">hello world!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', 'hello world!', ['What a beautiful world'])
    ]


def test_nested_tags():
    buf = StringIO(
        '<html><div data-translate>'
        'hello <b>Beautiful</b> world!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', 'hello <b>Beautiful</b> world!', [])
    ]


def test_utf8_encoding():
    buf = StringIO('<html><div data-translate>What’s up!</p></html>')
    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', u'What’s up!', [])
    ]

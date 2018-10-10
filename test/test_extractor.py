# coding=utf-8

from babel._compat import StringIO
from pybabel_angularjs.extractor import extract_angularjs, TagNotAllowedException, TagAttributeNotAllowedException, ExtractAttributeNotAllowedException


def test_extract_no_tags():
    buf = StringIO('<html></html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == []


def test_simple_string():
    buf = StringIO('<html><div i18n>hello world!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', 'hello world!', [], ())
    ]


def test_angularjs_expression():
    buf = StringIO('<html><div i18n>hello {{ name }}!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', 'hello {{ name }}!', [], ("angularjs-format", ))
    ]

def test_comments():
    buf = StringIO('<html><div i18n="page title">hello world!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', 'hello world!', ['page title'], ())
    ]


def test_nested_tags():
    buf = StringIO('<html><div i18n>hello <strong>Beautiful</strong> world!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', 'hello <strong>Beautiful</strong> world!', [], ())
    ]


def test_collapse_whitespaces():
    buf = StringIO('<html><div i18n>  \n\t\t  hello    <strong>Beautiful</strong> \n\t\t  world!\n\t\t  </div>  </html>')

    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', 'hello <strong>Beautiful</strong> world!', [], ())
    ]


def test_utf8_encoding():
    buf = StringIO('<html><div i18n>Příliš žluťoučký kůň úpěl ďábelské ódy.</div></html>')
    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', u'Příliš žluťoučký kůň úpěl ďábelské ódy.', [], ())
    ]


def test_attribute():
    buf = StringIO('<html><div title="some title">hello world!</div></html>')
    messages = list(extract_angularjs(buf, [], [], {"include_attributes": "title"}))
    assert messages == [
        (1, 'gettext', 'some title', ["title"], ())
    ]


def test_extract_attribute():
    buf = StringIO('<html><div something="some title" i18n-something>hello world!</div></html>')
    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', 'some title', ["something"], ())
    ]


def test_extract_attribute2():
    buf = StringIO('<html><div><strong something="some title" i18n-something>hello world!</strong></div></html>')
    messages = list(extract_angularjs(buf, [], [], {}))
    assert messages == [
        (1, 'gettext', 'some title', ["something"], ())
    ]


def test_extract_attribute3():
    buf = StringIO('<html><div i18n><strong something="some title" i18n-something>hello world!</strong></div></html>')
    messages = list(extract_angularjs(buf, [], [], {"include_attributes": "something"}))
    assert messages == [
        (1, 'gettext', 'some title', ["something"], ()),
        (1, 'gettext', '<strong something="some title" i18n-something="">hello world!</strong>', [], ())
    ]


def test_do_not_extract_attribute():
    buf = StringIO('<html><div title="some title" no-i18n-title>hello world!</div></html>')
    messages = list(extract_angularjs(buf, [], [], {"include_attributes": "title"}))
    assert messages == []


def test_auto_extract():
    buf = StringIO('<html><h2>Heading 2</h2>\n<h3>Heading 3</h3>\n<p>Hello world!</p><p i18n="useful comment for translator">Hello again.</p></html>')
    messages = list(extract_angularjs(buf, [], [], {"include_tags": "p h2 h3", "allowed_tags": "span strong br i a", "allowed_attributes_i": "class", "allowed_attributes_span": "class", "allowed_attributes_a": "target ng-href"}))
    assert messages == [
        (1, 'gettext', u'Heading 2', [], ()),
        (2, 'gettext', u'Heading 3', [], ()),
        (3, 'gettext', u'Hello world!', [], ()),
        (3, 'gettext', u'Hello again.', ["useful comment for translator"], ())
    ]


def test_do_not_extract_tag():
    buf = StringIO('<html><h2 no-i18n>Heading 2</h2>\n<h3 no-i18n="fake comment">Heading 3</h3>\n<p>Hello world!</p><p i18n="useful comment for translator">Hello again.</p></html>')

    messages = list(extract_angularjs(buf, [], [], {"include_tags": "p h2 h3"}))
    assert messages == [
        (3, 'gettext', u'Hello world!', [], ()),
        (3, 'gettext', u'Hello again.', ["useful comment for translator"], ())
    ]


def test_check_tags_in_content_attr_error():
    buf = StringIO('<html><div title="hello world!" i18n> hello <br><strong class="anything">world</strong>!\n</div>\n<div alt="hello world!" i18n> hello world!</div></html>')

    passed = False
    try:
        messages = list(extract_angularjs(buf, [], [], {"include_attributes": "title alt", }))
    except TagAttributeNotAllowedException:
        passed = True
    assert passed


def test_check_tags_in_content_tag_error():
    buf = StringIO('<html><div title="hello world!" i18n> hello <br><strong><div>world</div></strong>!\n</div>\n<div alt="hello world!" i18n> hello world!</div></html>')

    passed = False
    try:
        messages = list(extract_angularjs(buf, [], [], {"include_attributes": "title alt"}))
    except TagNotAllowedException:
        passed = True
    assert passed


def test_check_tag_attributes_in_content_ok():
    buf = StringIO('<html><div i18n>hello <br><strong><a href="www.helloworld.com" >world</a></strong>!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {"include_attributes": "title alt", "allowed_tags": "a br strong", "allowed_attributes_a": "href"}))
    assert messages == [
        (1, 'gettext', u'hello <br><strong><a href="www.helloworld.com">world</a></strong>!', [], ())
    ]


def test_check_tags_in_content_ok():
    buf = StringIO('<html><div title="hello world!" i18n> hello <br><strong>world</strong>!\n</div>\n<div alt="hello world!" i18n> hello world!</div></html>')

    messages = list(extract_angularjs(buf, [], [], {"include_attributes": "title alt"}))
    assert messages == [
        (1, 'gettext', u'hello world!', ['title'], ()),
        (1, 'gettext', u'hello <br><strong>world</strong>!', [], ()),
        (3, 'gettext', u'hello world!', ['alt'], ()),
        (3, 'gettext', u'hello world!', [], ())
    ]


def test_get_string_positions():
    buf = StringIO('<html>  \n\n\n<div title="hello <br> world!" i18n> \n   hello      world!\n</div>\n<div alt="   hello\n world  \t!" i18n> hello world! ěščřžýá</div></html>')

    messages = list(extract_angularjs(buf, [], [], {"include_attributes": "title alt"}))
    assert messages == [
        (4, 'gettext', u'hello <br> world!', ['title'], ()),
        (4, 'gettext', u'hello world!', [], ()),
        (7, 'gettext', u'hello world !', ['alt'], ()),
        (7, 'gettext', u'hello world! ěščřžýá', [], ())
    ]


def test_do_not_extract_entire_div_block():
    buf = StringIO('<html><div no-i18n>hello world!\n<h2 title="some title">Heading 2</h2>\n<div>another div <p>text1</p></div><p>text2</p></div>\n<h3 title="extracted title">Heading 3</h3></html>')

    messages = list(extract_angularjs(buf, [], [], {"include_attributes": "title alt", "include_tags": "p h2 h3"}))
    assert messages == [
        (4, 'gettext', u'extracted title', ['title'], ()),
        (4, 'gettext', u'Heading 3', [], ()),
    ]


def test_do_not_extract_entire_div_block_inner_attributes_error():
    for attr in ["i18n", "no-i18n", "i18n-title", "no-i18n-title"]:
        buf = StringIO('<html><div no-i18n>hello world!\n<h2 title="some title" %s>Heading 2</h2>\n<div>another div <p>text1</p></div><p>text2</p>\n<h3 title="extracted title">Heading 3</h3></div></html>' % attr)

        passed = False
        try:
            messages = list(extract_angularjs(buf, [], [], {"include_attributes": "title alt", "include_tags": "p h2 h3"}))
        except ExtractAttributeNotAllowedException:
            passed = True
        assert passed

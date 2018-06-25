try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser

from babel._compat import PY2

import bs4
import re


class AngularJSGettextHTMLParser(HTMLParser):
    """Parse HTML to find translate directives.

    Currently this parses for these forms of translation:

    <p data-translate>content</p>
        The content will be translated. Angular value templating will be
        recognised and transformed into gettext-familiar translation
        entries (i.e. "{$ expression $}" becomes "%(expression)")
    """

    def __init__(self, encoding):
        try:
            super(AngularJSGettextHTMLParser, self).__init__()
        except TypeError:
            HTMLParser.__init__(self)

        self.encoding = encoding
        self.in_translate = False
        self.inner_tags = []
        self.data = ''
        self.entries = []
        self.line = 0
        self.plural = False
        self.plural_form = ''
        self.comments = []

    def handle_starttag(self, tag, attrs):
        self.lineno = self.getpos()[0]
        attrdict = dict(attrs)

        # handle data-translate attribute for translating content
        if 'translate' in attrdict:
                self.in_translate = True
                self.plural_form = ''
                if 'data-translate-plural' in attrdict:
                    self.plural = True
                    value = attrdict['data-translate-plural']
                    if PY2:
                        value = value.decode(self.encoding)
                    self.plural_form = value
                if 'data-translate-comment' in attrdict:
                    value = attrdict['data-translate-comment']
                    if PY2:
                        value = value.decode(self.encoding)
                    self.comments.append(value)
        elif self.in_translate:
            self.data += '<%s>' % tag
            self.inner_tags.append(tag)

        # handle data-translate-attr attribute for translating attributes
        if 'data-translate-attr' in attrdict:
            for attr in attrdict['data-translate-attr'].split(','):
                attr = attr.strip()
                if attr not in attrdict:
                    raise RuntimeError(
                        "Cannot find attribute %r on <%s> at line %s" %
                        (attr, tag, self.lineno))
                value = attrdict[attr]
                if PY2:
                    value = value.decode(self.encoding)
                self.entries.append(
                    (self.lineno, u'gettext', value, [])
                )

    def handle_data(self, data):
        if self.in_translate:
            self.data += data

    def handle_endtag(self, tag):
        if self.in_translate:
            if len(self.inner_tags) > 0:
                tag = self.inner_tags.pop()
                self.data += "</%s>" % tag
                return
            value = self.data.strip()
            if PY2:
                value = value.decode(self.encoding)
            if self.plural_form:
                messages = (
                    value,
                    self.plural_form
                )
                func_name = u'ngettext'
            else:
                messages = value
                func_name = u'gettext'
            self.entries.append(
                (self.lineno, func_name, messages, self.comments)
            )
            self.in_translate = False
            self.data = ''
            self.comments = []


def extract_angularjs(fileobj, keywords, comment_tags, options):
    """Extract messages from AngularJS template (HTML) files that use the
    data-translate directive as per.

    :param fileobj: the file-like object the messages should be extracted
                    from
    :param keywords: This is a standard parameter so it isaccepted but ignored.

    :param comment_tags: This is a standard parameter so it is accepted but
                        ignored.
    :param options: Another standard parameter that is accepted but ignored.
    :return: an iterator over ``(lineno, funcname, message, comments)``
             tuples
    :rtype: ``iterator``
    """
    # atributy, ktere chceme prekladat, tzn extrahovat do .po
    ATTRIBUTES = ["placeholder", "data-title", "alt", "data-tooltip", "href", "title"]

    encoding = options.get('encoding', 'utf-8')
    html = bs4.BeautifulSoup(fileobj, "html.parser")
    tags = html.find_all(lambda tag: tag.has_attr("translate"))  # type: list[bs4.Tag]

    for tag in tags:
        content = tag.encode_contents()
        content = content.replace("\n", " ").replace("\t", " ")
        content = re.sub("\s+", " ", content).strip()
        content = content.replace("/>", ">")

        if content:
            # jinak to vraci warning pri prazdnem stringu
            yield (1, u"gettext", content.decode("utf-8"), [tag.attrs["translate"]])

        for attr in tag.attrs:
            if attr not in ATTRIBUTES:
                continue
            attrContent = tag.attrs[attr]
            print attr, attrContent
            yield (1, u"gettext", attrContent, [tag.attrs["translate"]])
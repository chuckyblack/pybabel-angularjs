try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser


class AngularJSGettextHTMLParser(HTMLParser):
    """Parse HTML to find translate directives.

    Currently this parses for these forms of translation:

    <p data-translate>content</p>
        The content will be translated. Angular value templating will be
        recognised and transformed into gettext-familiar translation
        entries (i.e. "{$ expression $}" becomes "%(expression)")
    """

    def __init__(self):
        try:
            super(AngularJSGettextHTMLParser, self).__init__()
        except TypeError:
            HTMLParser.__init__(self)

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
        if 'data-translate' in attrdict:
                self.in_translate = True
                self.plural_form = ''
                if 'data-translate-plural' in attrdict:
                    self.plural = True
                    self.plural_form = attrdict['data-translate-plural']
                if 'data-translate-comment' in attrdict:
                    self.comments.append(attrdict['data-translate-comment'])
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
                self.entries.append(
                    (self.lineno, u'gettext', attrdict[attr], [])
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
            if self.plural_form:
                messages = (
                    self.data.strip(),
                    self.plural_form
                )
                func_name = u'ngettext'
            else:
                messages = self.data.strip()
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

    parser = AngularJSGettextHTMLParser()

    for line in fileobj:
        parser.feed(line)

    for entry in parser.entries:
        yield entry

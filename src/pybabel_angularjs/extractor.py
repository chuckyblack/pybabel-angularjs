# coding=utf-8

try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser

import re


class TagNotAllowedException(Exception):
    pass


class TagAttributeNotAllowedException(Exception):
    pass


class ExtractAttributeNotAllowedException(Exception):
    pass


class MissingAttributeException(Exception):
    pass


class AngularJSGettextHTMLParser(HTMLParser):
    """Parse HTML to find translate directives.

    Currently this parses for these forms of translation:

    <p data-translate>content</p>
        The content will be translated. Angular value templating will be
        recognised and transformed into gettext-familiar translation
        entries (i.e. "{$ expression $}" becomes "%(expression)")
    """

    def __init__(self, encoding, include_tags, include_attributes, extract_attribute, allowed_attributes_by_tag):
        try:
            super(AngularJSGettextHTMLParser, self).__init__()
        except TypeError:
            HTMLParser.__init__(self)

        self.encoding = encoding
        self.include_tags = include_tags
        self.include_attributes = include_attributes
        self.extract_attribute = extract_attribute
        self.allowed_attributes_by_tag = allowed_attributes_by_tag

        self.in_translate = False
        self.inner_tags = []
        self.data = ''
        self.entries = []
        self.start_lineno = 0
        self.plural = False
        self.plural_form = ''
        self.comments = []
        self.re_collapse_whitespaces = re.compile("\s+")
        self.in_do_not_translate = False

    @property
    def do_not_extract_attribute(self):
        return "no-" + self.extract_attribute

    def normalize_string(self, string, replace_whitespace=u" "):
        """
        :type string: str
        :type replace_whitespace: str
        """
        string = (
            string
                .replace("\n", " ")
                .replace("\t", " ")
                .replace("/>", ">")
                .replace("</br>", "")
                .replace(u" ", "&nbsp;")
        )
        if isinstance(string, bytes):
            string = string.decode("utf-8")
        return self.re_collapse_whitespaces.sub(replace_whitespace, string).strip()

    def add_entry(self, message, comments=[], lineno=None):
        self.entries.append(
            (
                lineno or self.start_lineno,
                u'gettext',
                self.normalize_string(message),
                [self.normalize_string(comment) for comment in comments],
                ("angularjs-format", ) if "{{" in message else tuple()
            )
        )

    def append_inner_tag(self, tag):
        if tag not in ("br", "input", "img"):
            self.inner_tags.append(tag)

    def attrdict_contains(self, attrdict, search=None):
        search = search or [self.extract_attribute, self.do_not_extract_attribute]
        for attr in attrdict:   # type: str
            for string in search:
                if attr.startswith(string):
                    return True
        return False

    def handle_starttag(self, tag, attrs):
        attrdict = dict(attrs)
        lineno = self.getpos()[0]

        if self.in_do_not_translate:
            if self.attrdict_contains(attrdict):
                raise ExtractAttributeNotAllowedException((lineno, tag, attrdict))
            self.append_inner_tag(tag)
            return

        if tag == "div" and self.do_not_extract_attribute in attrdict:
            self.in_do_not_translate = True
            if self.attrdict_contains(attrdict, [self.extract_attribute]):
                raise ExtractAttributeNotAllowedException((lineno, tag, attrdict))
            return

        # handle data-translate attribute for translating content
        if self.extract_attribute in attrdict or (tag in self.include_tags and self.do_not_extract_attribute not in attrdict):
            self.start_lineno = lineno
            self.in_translate = True
            comment = attrdict.get(self.extract_attribute)
            if comment:
                self.comments.append(comment)
        elif self.in_translate:
            if tag not in self.allowed_attributes_by_tag:
                raise TagNotAllowedException((lineno, tag))

            allowed_attributes = self.allowed_attributes_by_tag[tag]
            diff_attributes = set(attrdict.keys()) - set(allowed_attributes)
            for attr in diff_attributes:
                if attr.startswith(self.extract_attribute + "-"):   # i18n-
                    pairAttr = attr.split("-", 1)[1]
                else:
                    pairAttr = "%s-%s" % (self.extract_attribute, attr)
                if pairAttr not in attrdict:
                    raise TagAttributeNotAllowedException((lineno, tag, attrdict))

            if attrs:
                insert_value = ""
                for attr in attrs:
                    name = attr[0]
                    value = attr[1]
                    insert_value += " " + '%s="%s"' % (name, value or "")
                self.data += '<%s %s>' % (tag, insert_value)
            else:
                self.data += '<%s>' % tag

            self.append_inner_tag(tag)

        already_added_attrs = []
        # auto-add attributes
        for attr in self.include_attributes:
            exclude_attribute = "%s-%s" % (self.do_not_extract_attribute, attr)
            if attr in attrdict and exclude_attribute not in attrdict:
                self.add_entry(attrdict[attr], [attr], lineno)
                already_added_attrs.append(attr)

        # i18n-marked attributes
        for attr in attrdict:  # type: str
            if attr.startswith(self.extract_attribute + "-"):
                name = attr.split("-", 1)[1]
                if name not in attrdict:
                    raise MissingAttributeException((lineno, tag, name))

                if name not in already_added_attrs:
                    self.add_entry(attrdict[name], [name], lineno)

    def handle_data(self, data):
        if self.in_translate:
            self.data += data

    def handle_endtag(self, tag):
        if self.in_do_not_translate:
            if len(self.inner_tags) > 0:
                self.inner_tags.pop()
                return

            self.in_do_not_translate = False

        if self.in_translate:
            if len(self.inner_tags) > 0:
                tag = self.inner_tags.pop()
                self.data += "</%s>" % tag
                return

            self.add_entry(self.data, self.comments)
            self.in_translate = False
            self.data = ''
            self.comments = []


def get_option_list(options, name, default=[]):
    value = options.get(name)
    return value and value.split(" ") or default


def extract_angularjs(fileobj, keywords, comment_tags, options):
    """Extract messages from AngularJS template (HTML) files that use the
    data-translate directive as per.

    :param fileobj: the file-like object the messages should be extracted from
    :param keywords: This is a standard parameter so it isaccepted but ignored.
    :param comment_tags: This is a standard parameter so it is accepted but ignored.
    :param options: Another standard parameter that is accepted but ignored.
    :return: an iterator over ``(lineno, funcname, message, comments, flags)`` tuples
    :rtype: ``iterator``
    """
    include_tags = get_option_list(options, "include_tags")
    include_attributes = get_option_list(options, "include_attributes")
    allowed_tags = get_option_list(options, "allowed_tags", ["strong", "br", "i"])
    extract_attribute = options.get("extract_attribute") or "i18n"
    allowed_attributes_by_tag = {tag: get_option_list(options, "allowed_attributes_" + tag) for tag in allowed_tags}
    encoding = options.get('encoding', 'utf-8')

    parser = AngularJSGettextHTMLParser(
        encoding,
        include_tags,
        include_attributes,
        extract_attribute,
        allowed_attributes_by_tag
    )

    for line in fileobj:
        if isinstance(line, bytes):
            line = line.decode("utf-8")
        line = line.replace("&#xa;", "<br>")
        line = line.replace("&nbsp;", u" ")
        parser.feed(line)

    for entry in parser.entries:
        yield entry

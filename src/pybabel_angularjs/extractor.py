# coding=utf-8

import bs4
import re

re_collapse_whitespaces = re.compile("\s+")


def normalize_content(tag):
    """
    :type tag: bs4.Tag
    """
    content = (
        tag
        .encode_contents()
        .replace("\n", " ")
        .replace("\t", " ")
        .replace("/>", ">")
        .replace("</br>", "")
    )
    return re_collapse_whitespaces.sub(" ", content).strip()


def get_tag_lineno(fileobj, tag):
    """
    :param fileobj: html content
    :type tag: bs4.Tag
    """
    # TODO: find tag on file line using parents and siblings
    return 1


def check_tags_in_content(tag):
    """
    :type tag: bs4.Tag
    """
    # TODO: allow only some tags inside content, e.g. <strong>, <br>, ...
    pass


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
    attributes = options.get("include_attributes", [])
    attributes = attributes and attributes.split(" ")
    extract_attribute = options.get("extract_attribute") or "i18n"

    html = bs4.BeautifulSoup(fileobj, "html.parser")
    tags = html.find_all()  # type: list[bs4.Tag]

    for tag in tags:
        for attr in attributes:
            if tag.attrs.get(attr):
                yield (get_tag_lineno(fileobj, tag), "gettext", tag.attrs[attr], [attr])

        if extract_attribute in tag.attrs:
            check_tags_in_content(tag)
            content = normalize_content(tag)
            comment = tag.attrs[extract_attribute]
            yield (get_tag_lineno(fileobj, tag), "gettext", content.decode("utf-8"), [comment] if comment else [])

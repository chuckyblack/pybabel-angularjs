# coding=utf-8

import bs4
import re

re_collapse_whitespaces = re.compile("\s+")


def normalize_content(tag, replace_whitespace=" "):
    """
    :type tag: bs4.Tag
    :type replace_whitespace: str
    """
    return normalize_string(tag.decode_contents(), replace_whitespace)


def normalize_string(string, replace_whitespace=" "):
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
    )
    if not isinstance(string, unicode):
        string = string.decode("utf-8")
    return re_collapse_whitespaces.sub(replace_whitespace, string).strip()


def get_string_lineno(fileobj, string_positions_cache, stripped_string):
    """
    :param fileobj: html content
    :type string_positions_cache: dict
    :type stripped_string: unicode
    """
    cache = string_positions_cache.get(stripped_string)
    if cache is None:
        string_positions_cache[stripped_string] = get_string_positions(fileobj, stripped_string)
    return string_positions_cache[stripped_string].pop(0)


def get_string_positions(fileobj, stripped_string):
    """
    :type fileobj: html content
    :type stripped_string: unicode
    """
    fileobj.seek(0)
    buf = fileobj.read()
    buf = buf.decode("utf-8")

    newlines_positions = find_all_strings('\n', buf)
    openings_positions = find_all_strings('<[^/]', buf)

    buf_stripped = normalize_string(buf, "")
    openings_positions_stripped = find_all_strings('<[^/]', buf_stripped)
    strings_positions_stripped = find_all_strings(stripped_string, buf_stripped)

    result = []
    for string_pos in strings_positions_stripped:
        tag_position_index = get_tag_original_index(string_pos, openings_positions_stripped)
        tag_position = openings_positions[tag_position_index]
        line_number = get_tag_original_line(tag_position, newlines_positions)
        if not line_number:
            line_number = 1
        result.append(line_number)
    return result


def get_tag_original_index(string_pos, openings_positions_stripped):
    """
    :param string_pos: int
    :param openings_positions_stripped: list(int)
    """
    i = 0
    for i in range(0, len(openings_positions_stripped)):
        if openings_positions_stripped[i] > string_pos:
            return i - 1
    return i


def get_tag_original_line(tag_position, newlines_positions):
    """
    :param stringPos: int
    :param openingsPositionsStripped: list(int)
        """
    line_number = 1
    for newline_pos in newlines_positions:
        if newline_pos > tag_position:
            return line_number
        else:
            line_number += 1
    return line_number


def find_all_strings(pattern, string):
    """
    :param pattern: str
    :param string: str
    """
    return [a.start() for a in list(re.finditer(pattern, string))]


def check_tags_in_content(tag):
    """
    :type tag: bs4.Tag
    """
    allowed_tags = ["strong", "br", "b",  "i", "span"]
    for child in tag.descendants:
        if isinstance(child, bs4.NavigableString):
            continue
        if child.name not in allowed_tags:
            raise TagNotAllowedException()
        if child.attrs:
            raise TagNotAllowedException()


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

    stringPositionsCache = {}

    for tag in tags:
        for attr in attributes:
            if tag.attrs.get(attr):
                attrValue = normalize_string(tag.attrs[attr])
                lineno = get_string_lineno(fileobj, stringPositionsCache, normalize_string(tag.attrs[attr], ""))
                yield (lineno, "gettext", attrValue, [attr])

        if extract_attribute in tag.attrs:
            check_tags_in_content(tag)
            content = normalize_content(tag)
            comment = tag.attrs[extract_attribute]
            lineno = get_string_lineno(fileobj, stringPositionsCache, normalize_content(tag, ""))
            yield (lineno, "gettext", content, [comment] if comment else [])


class TagNotAllowedException(Exception):
    pass

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


# TODO sloucit s normalize_content - ale ta neumi attributy
def strip(string):
    string = re.sub('\s+', '', string)
    string = string.replace("<br/>", "<br>")
    return string


def get_string_lineno(fileobj, stringPositionsCache, strippedString):
    cache = stringPositionsCache.get(strippedString)
    if not cache:
        stringPositionsCache[strippedString] = get_string_positions(fileobj, strippedString)
    return stringPositionsCache[strippedString].pop(0)


def get_string_positions(fileobj, strippedString):
    """
    :param fileobj: html content
    :type strippedString: str
    """
    fileobj.seek(0)
    buf = unicode(fileobj.read(), "utf-8")
    newlinesPositions = findAllStrings('\n', buf)
    openingsPositions = findAllStrings('<[^/]', buf)

    bufStripped = strip(buf)
    openingsPositionsStripped = findAllStrings('<[^/]', bufStripped)
    stringsPositionsStripped = findAllStrings(strippedString, bufStripped)

    result = []
    for stringPos in stringsPositionsStripped:
        tagPositionIndex = getTagOriginalIndex(stringPos, openingsPositionsStripped)
        tagPosition = openingsPositions[tagPositionIndex]
        lineNumber = getTagOriginalLine(tagPosition, newlinesPositions)
        if not lineNumber:
            lineNumber = 1
        result.append(lineNumber)
    return result


def getTagOriginalIndex(stringPos, openingsPositionsStripped):
    i = 0
    for i in range(0, len(openingsPositionsStripped)):
        if openingsPositionsStripped[i] > stringPos:
            return i - 1
    return i


def getTagOriginalLine(tagPosition, newlinesPositions):
    lineNumber = 1
    for newlinePos in newlinesPositions:
        if newlinePos > tagPosition:
            return lineNumber
        else:
            lineNumber += 1
    return lineNumber


def findAllStrings(pattern, string):
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
            raise TagNotAllowedException


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
                attrValue = tag.attrs[attr]
                # TODO normalize_content pro atributy
                lineno = get_string_lineno(fileobj, stringPositionsCache, strip(attrValue))
                yield (lineno, "gettext", attrValue, [attr])

        if extract_attribute in tag.attrs:
            check_tags_in_content(tag)
            content = normalize_content(tag)
            comment = tag.attrs[extract_attribute]
            lineno = get_string_lineno(fileobj, stringPositionsCache, strip(tag.decode_contents()))
            yield (lineno, "gettext", content.decode("utf-8"), [comment] if comment else [])


class TagNotAllowedException(Exception):
    pass

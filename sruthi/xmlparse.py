import defusedxml.ElementTree as etree
from . import errors

namespaces = {
    'sru': 'http://www.loc.gov/zing/srw/',
    'isad': 'http://www.expertisecentrumdavid.be/xmlschemas/isad.xsd',
    'rel': 'info:srw/extension/2/relevancy-1.0',
    'ap': 'http://www.archivportal.ch/srw/extension/',
}


class XMLNone(object):
    def __nonzero__(self):
        return False

    def __bool__(self):
        return False

    text = None


def parse(content):
    try:
        return etree.fromstring(content)
    except Exception as e:
        raise errors.SruError("Error while parsing XML: %s" % e)


def find(xml, path):
    elem = xml.find(path, namespaces)
    if elem is None:
        return XMLNone()
    return elem


def findall(xml, path):
    return xml.findall(path, namespaces)

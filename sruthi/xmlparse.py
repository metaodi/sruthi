import re
import defusedxml.ElementTree as etree
from . import errors


class XMLNone(object):
    def __nonzero__(self):
        return False

    def __bool__(self):
        return False

    def iter(self):
        return []

    text = None


class XMLParser(object):
    def __init__(self):
        self.namespaces = {
            'sru': 'http://www.loc.gov/zing/srw/',
            'isad': 'http://www.expertisecentrumdavid.be/xmlschemas/isad.xsd',
            'rel': 'info:srw/extension/2/relevancy-1.0',
            'ap': 'http://www.archivportal.ch/srw/extension/',
            'zr': 'http://explain.z3950.org/dtd/2.1/',
        }

    def parse(self, content):
        try:
            return etree.fromstring(content)
        except Exception as e:
            raise errors.SruError("Error while parsing XML: %s" % e)

    def find(self, xml, path):
        if isinstance(path, list):
            for p in path:
                elem = self.find(xml, p)
                if not isinstance(elem, XMLNone):
                    return elem
            return XMLNone()
        elem = xml.find(path, self.namespaces)
        if elem is None:
            return XMLNone()
        return elem

    def findall(self, xml, path):
        return xml.findall(path, self.namespaces)

    def tostring(self, xml):
        return etree.tostring(xml)

    def namespace(self, element):
        m = re.match(r'\{(.*)\}', element.tag)
        return m.group(1) if m else ''

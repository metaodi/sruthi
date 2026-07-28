import re
from typing import Any
from xml.etree.ElementTree import Element

import defusedxml.ElementTree as etree
import xmltodict

from . import errors


class XMLNone:
    """
    Sentinel returned instead of ``None`` for missing XML elements, so that
    callers can chain ``.text`` without guarding for ``None`` first.
    """

    text: str | None = None

    def __bool__(self) -> bool:
        return False

    def iter(self) -> list[Element]:
        return []


#: An element lookup either finds an ``Element`` or yields the ``XMLNone`` sentinel.
FoundElement = Element | XMLNone


class XMLParser:
    def __init__(self) -> None:
        self.namespaces: dict[str, str] = {
            "sru": "http://www.loc.gov/zing/srw/",
            "isad": "http://www.expertisecentrumdavid.be/xmlschemas/isad.xsd",
            "rel": "info:srw/extension/2/relevancy-1.0",
            "ap": "http://www.archivportal.ch/srw/extension/",
            "zr": "http://explain.z3950.org/dtd/2.1/",
            "zr2": "http://explain.z3950.org/dtd/2.0/",
        }
        self.dict_namespaces: dict[str, str | None] = {
            "http://www.loc.gov/zing/srw/": "sru",
            "http://explain.z3950.org/dtd/2.1/": "zr",
            "info:srw/extension/2/relevancy-1.0": None,
            "http://www.archivportal.ch/srw/extension/": None,
            "http://www.loc.gov/MARC21/slim": None,
            "info:lc/xmlns/marcxchange-v1": None,
            "http://www.loc.gov/mods/v3": None,
            "http://www.loc.gov/standards/mods/v3/mods-3-6.xsd": None,
            "http://purl.org/dc/elements/1.1/": None,
            "http://www.expertisecentrumdavid.be/xmlschemas/isad.xsd": None,
            "http://www.w3.org/2001/XMLSchema-instance": None,
            "http://www.w3.org/XML/1998/namespace": None,
        }

    def parse(self, content: str | bytes) -> Element:
        try:
            element: Element = etree.fromstring(content)
            return element
        except Exception as e:
            raise errors.SruError(f"Error while parsing XML: {e}") from e

    def find(self, xml: Element, path: str | list[str]) -> FoundElement:
        if isinstance(path, list):
            for p in path:
                elem = self.find(xml, p)
                if not isinstance(elem, XMLNone):
                    return elem
            return XMLNone()
        found = xml.find(path, self.namespaces)
        if found is None:
            return XMLNone()
        return found

    def findall(self, xml: Element, path: str | list[str]) -> list[Element]:
        if isinstance(path, list):
            for p in path:
                elems = self.findall(xml, p)
                if elems:
                    return elems
            return []
        return xml.findall(path, self.namespaces)

    def tostring(self, xml: Element) -> bytes:
        data: bytes = etree.tostring(xml)
        return data

    def todict(
        self, xml: FoundElement | str | bytes, **kwargs: Any
    ) -> dict[str, Any] | None:
        if isinstance(xml, XMLNone):
            return None
        if isinstance(xml, Element):
            xml = self.tostring(xml)

        dict_args: dict[str, Any] = {
            "dict_constructor": dict,
            "process_namespaces": True,
            "namespaces": self.dict_namespaces,
            "attr_prefix": "",
            "cdata_key": "text",
        }
        dict_args.update(kwargs)
        return dict(xmltodict.parse(xml, **dict_args))

    def namespace(self, element: Element) -> str:
        m = re.match(r"\{(.*)\}", element.tag)
        return m.group(1) if m else ""

from __future__ import annotations

import re
from typing import Any, Dict, Iterator, List, Optional, Union
from xml.etree.ElementTree import Element
import defusedxml.ElementTree as etree
import xmltodict
from . import errors


class XMLNone:
    text: Optional[str] = None

    def __nonzero__(self) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def iter(self) -> Iterator[Any]:
        return iter([])

    def __iter__(self) -> Iterator[Any]:
        return iter([])

    def find(self, path: str, namespaces: Any = None) -> None:
        return None

    def findall(self, path: str, namespaces: Any = None) -> List[Any]:
        return []


class XMLParser:
    def __init__(self) -> None:
        self.namespaces: Dict[str, str] = {
            "sru": "http://www.loc.gov/zing/srw/",
            "isad": "http://www.expertisecentrumdavid.be/xmlschemas/isad.xsd",
            "rel": "info:srw/extension/2/relevancy-1.0",
            "ap": "http://www.archivportal.ch/srw/extension/",
            "zr": "http://explain.z3950.org/dtd/2.1/",
            "zr2": "http://explain.z3950.org/dtd/2.0/",
        }
        self.dict_namespaces: Dict[str, Optional[str]] = {
            "http://www.loc.gov/zing/srw/": "sru",
            "http://explain.z3950.org/dtd/2.1/": "zr",
            "info:srw/extension/2/relevancy-1.0": None,
            "http://www.archivportal.ch/srw/extension/": None,
            "http://www.loc.gov/MARC21/slim": None,
            "info:lc/xmlns/marcxchange-v1": None,
            "http://www.loc.gov/mods/v3": None,
            "http://www.loc.gov/standards/mods/v3/mods-3-6.xsd": None,
            "http://www.loc.gov/standards/mods/v3/mods-3-6.xsd": None,
            "http://purl.org/dc/elements/1.1/": None,
            "http://www.expertisecentrumdavid.be/xmlschemas/isad.xsd": None,
            "http://www.w3.org/2001/XMLSchema-instance": None,
            "http://www.w3.org/XML/1998/namespace": None,
        }

    def parse(self, content: bytes) -> Element:
        try:
            return etree.fromstring(content)
        except Exception as e:
            raise errors.SruError(f"Error while parsing XML: {e}")

    def find(
        self,
        xml: Union[Element, XMLNone],
        path: Union[str, List[str]],
    ) -> Union[Element, XMLNone]:
        if isinstance(path, list):
            for p in path:
                result = self.find(xml, p)
                if not isinstance(result, XMLNone):
                    return result
            return XMLNone()
        found = xml.find(path, self.namespaces)
        if found is None:
            return XMLNone()
        return found

    def findall(
        self,
        xml: Union[Element, XMLNone],
        path: Union[str, List[str]],
    ) -> List[Element]:
        if isinstance(path, list):
            for p in path:
                elems = self.findall(xml, p)
                if elems:
                    return elems
            return []
        return xml.findall(path, self.namespaces)

    def tostring(self, xml: Element) -> bytes:
        return etree.tostring(xml)

    def todict(
        self, xml: Union[Element, XMLNone], **kwargs: Any
    ) -> Optional[Dict[str, Any]]:
        if isinstance(xml, XMLNone):
            return None
        xml_bytes: bytes = self.tostring(xml)

        dict_args: Dict[str, Any] = {
            "dict_constructor": dict,
            "process_namespaces": True,
            "namespaces": self.dict_namespaces,
            "attr_prefix": "",
            "cdata_key": "text",
        }
        dict_args.update(kwargs)
        return dict(xmltodict.parse(xml_bytes, **dict_args))

    def namespace(self, element: Element) -> str:
        m = re.match(r"\{(.*)\}", element.tag)
        return m.group(1) if m else ""

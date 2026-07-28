import warnings
from collections import defaultdict
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any, overload
from xml.etree.ElementTree import Element

from flatten_dict import flatten

from . import errors, xmlparse

if TYPE_CHECKING:  # pragma: no cover - import cycle, only needed for annotations
    from .client import DataLoader

#: A single, flattened SRU record.
Record = dict[str, Any]


class Response:
    #: Set by ``_parse_content()``, i.e. only after ``__init__()`` has run.
    sru_version: str | None

    def __init__(self, data_loader: "DataLoader") -> None:
        self.data_loader = data_loader
        self.xmlparser = xmlparse.XMLParser()
        self.records: list[Record] = []
        xml = self.data_loader.load()
        self._parse_content(xml)

    def _parse_content(self, xml: Element) -> None:
        raise NotImplementedError

    def maybe_int(self, s: Any) -> Any:
        try:
            return int(s)
        except (ValueError, TypeError):
            return s

    def _check_response_tag(self, xml: Element, tag: str) -> None:
        sru = "{http://www.loc.gov/zing/srw/}"
        response = f"{sru}{tag}"
        if not xml.tag == response:
            # fix namespace for servers that provide the wrong namespace URI
            main_ns = self.xmlparser.namespace(xml)
            if "www.loc.gov/zing/srw" in main_ns:
                warnings.warn(
                    f"""
                    The server has the wrong namespace for SRU,
                    it should be {sru} but it's currently set to {{{main_ns}}}.
                    """,
                    errors.WrongNamespaceWarning,
                    stacklevel=2,
                )
                self.xmlparser.namespaces["sru"] = main_ns
            else:
                raise errors.ServerIncompatibleError(
                    f"Server response did not contain a {response} tag"
                )


class SearchRetrieveResponse(Response):
    #: Set by ``_parse_content()``, i.e. only after ``__init__()`` has run.
    count: int
    next_start_record: int | None

    def __repr__(self) -> str:
        try:
            return (
                f"SearchRetrieveResponse("
                f"sru_version={self.sru_version!r},"
                f"count={self.count!r},"
                f"next_start_record={self.next_start_record!r})"
            )
        except AttributeError:
            return "SearchRetrieveResponse(empty)"

    def _parse_content(self, xml: Element) -> None:
        self._check_response_tag(xml, "searchRetrieveResponse")

        self.sru_version = self.xmlparser.find(xml, "./sru:version").text
        self.count = self.maybe_int(
            self.xmlparser.find(xml, "./sru:numberOfRecords").text
        )
        self._extract_records(xml)

        next_start_record = self.xmlparser.find(xml, "./sru:nextRecordPosition").text
        if next_start_record:
            self.next_start_record = self.maybe_int(next_start_record)
        else:
            self.next_start_record = None

    def __length_hint__(self) -> int:
        return self.count

    def __iter__(self) -> Iterator[Record]:
        # use while loop since self.records could grow while iterating
        i = 0
        while True:
            # load new data when near end
            if i == len(self.records):
                try:
                    self._load_new_data()
                except errors.NoMoreRecordsError:
                    break
            yield self.records[i]
            i += 1

    @overload
    def __getitem__(self, key: int) -> Record: ...

    @overload
    def __getitem__(self, key: slice) -> list[Record]: ...

    def __getitem__(self, key: int | slice) -> Record | list[Record]:
        if isinstance(key, slice):
            limit = max(key.start or 0, key.stop or self.count)
            self._load_new_data_until(limit)
            count = len(self.records)
            return [self.records[k] for k in range(*key.indices(count))]

        if not isinstance(key, int):
            raise TypeError("Index must be an integer or slice")

        limit = key
        if limit < 0:
            # if we get a negative index, load all data
            limit = self.count
        self._load_new_data_until(limit)
        return self.records[key]

    def _load_new_data_until(self, limit: int) -> None:
        while limit >= len(self.records):
            try:
                self._load_new_data()
            except errors.NoMoreRecordsError:
                break

    def _load_new_data(self) -> None:
        if self.next_start_record is None:
            raise errors.NoMoreRecordsError()
        xml = self.data_loader.load(startRecord=self.next_start_record)
        self._parse_content(xml)

    def _extract_records(self, xml: Element) -> None:
        new_records = []

        xml_recs = self.xmlparser.findall(xml, "./sru:records/sru:record")
        for xml_rec in xml_recs:
            record: defaultdict[str, Any] = defaultdict()
            record["schema"] = self.xmlparser.find(xml_rec, "./sru:recordSchema").text
            record_data = self.xmlparser.find(xml_rec, "./sru:recordData")
            extra_data = self.xmlparser.find(xml_rec, "./sru:extraRecordData")

            record.update(self._tag_data(record_data, "sru:recordData") or {})
            record["extra"] = self._tag_data(extra_data, "sru:extraRecordData")

            new_records.append(dict(record))
        self.records.extend(new_records)

    def _tag_data(
        self, elem: xmlparse.FoundElement, parent: str
    ) -> dict[str, Any] | None:
        if isinstance(elem, xmlparse.XMLNone) or not len(elem):
            return None

        todict = self.xmlparser.todict(elem, xml_attribs=True)
        record_data: Any = todict.get(parent) if todict else None
        if not record_data:
            return None

        # check if there is only one element on the top level
        keys = list(record_data.keys())
        if len(record_data) == 1 and len(keys) > 0 and len(record_data[keys[0]]) > 0:
            record_data = record_data[keys[0]]

        record_data.pop("schemaLocation", None)
        record_data.pop("xmlns", None)

        def leaf_reducer(k1: str | None, k2: str) -> str:
            # only use key of leaf element
            return k2

        try:
            record_data = flatten(record_data, reducer=leaf_reducer)
        except ValueError:
            # if the keys of the leaf elements are not unique
            # the dict will not be flattened
            pass

        flattened: dict[str, Any] = record_data
        return flattened


class ExplainResponse(Response):
    #: Set by ``_parse_content()``, i.e. only after ``__init__()`` has run.
    server: dict[str, Any]
    database: dict[str, str | None]
    index: dict[str, dict[str, str | None]]
    schema: dict[str, dict[str, Any]]
    config: dict[str, Any]

    def __repr__(self) -> str:
        return (
            f"ExplainResponse("
            f"sru_version={self.sru_version!r},"
            f"server={self.server!r},"
            f"database={self.database!r}"
            f"index={self.index!r}"
            f"schema={self.schema!r}"
            f"config={self.config!r})"
        )

    def asdict(self) -> "AttributeDict":
        return AttributeDict(
            {
                "sru_version": self.sru_version,
                "server": self.server,
                "database": self.database,
                "index": self.index,
                "schema": self.schema,
                "config": self.config,
            }
        )

    def _parse_content(self, xml: Element) -> None:
        self._check_response_tag(xml, "explainResponse")

        record_schema = self.xmlparser.find(xml, ".//sru:recordSchema").text
        if record_schema:
            self.xmlparser.namespaces["zr"] = record_schema

        self.sru_version = self.xmlparser.find(xml, "./sru:version").text

        self.server = self._parse_server(xml)
        self.database = self._parse_database(xml)
        self.index = self._parse_index(xml)
        self.schema = self._parse_schema(xml)
        self.config = self._parse_config(xml)

    def _parse_server(self, xml: Element) -> dict[str, Any]:
        server_info: dict[str, Any] = {
            "host": self.xmlparser.find(
                xml, [".//zr:serverInfo/zr:host", ".//zr2:serverInfo/zr:host"]
            ).text,
            "port": self.xmlparser.find(
                xml,
                [
                    ".//zr:serverInfo/zr:port",
                    ".//zr2:serverInfo/zr:port",
                ],
            ).text,
            "database": self.xmlparser.find(
                xml,
                [
                    ".//zr:serverInfo/zr:database",
                    ".//zr2:serverInfo/zr:database",
                ],
            ).text,
        }
        server_info["port"] = self.maybe_int(server_info["port"])
        return server_info

    def _parse_schema(self, xml: Element) -> dict[str, dict[str, Any]]:
        def bool_or_none(v: str | None) -> bool | None:
            if v is None:
                return None
            return bool(v)

        def ident(a: str | None) -> str | None:
            return a

        attributes: dict[str, Callable[[Any], Any]] = {
            "identifier": ident,
            "name": ident,
            "location": ident,
            "sort": bool_or_none,
            "retrieve": bool_or_none,
        }

        schemas: dict[str, dict[str, Any]] = {}
        xml_schemas = self.xmlparser.findall(
            xml,
            [
                ".//zr:schemaInfo/zr:schema",
                ".//zr2:schemaInfo/zr2:schema",
            ],
        )
        for schema in xml_schemas:
            schema_info: dict[str, Any] = {}
            for attr, fn in attributes.items():
                xml_attr = schema.attrib.get(attr)
                if xml_attr:
                    schema_info[attr] = fn(xml_attr)
            schema_info["title"] = self.xmlparser.find(schema, "./zr:title").text
            schemas[schema.attrib.get("name", "")] = schema_info
        return schemas

    def _parse_config(self, xml: Element) -> dict[str, Any]:
        config: dict[str, Any] = {}
        settings = self.xmlparser.findall(
            xml,
            [
                ".//zr:configInfo/zr:setting",
                ".//zr2:configInfo/zr:setting",
            ],
        )
        for setting in settings:
            t = setting.attrib["type"]
            config[t] = self.maybe_int(setting.text)

        # defaults
        xml_defaults = self.xmlparser.findall(
            xml,
            [
                ".//zr:configInfo/zr:default",
                ".//zr2:configInfo/zr:default",
            ],
        )
        defaults: dict[str, Any] = {}
        for default in xml_defaults:
            t = default.attrib["type"]
            defaults[t] = self.maybe_int(default.text)
        config["defaults"] = defaults
        return config

    def _parse_database(self, xml: Element) -> dict[str, str | None]:
        db = self.xmlparser.find(xml, ".//zr:databaseInfo")
        if isinstance(db, xmlparse.XMLNone) or not len(db):
            return {}
        db_info: dict[str, str | None] = {
            "title": self.xmlparser.find(db, ["./zr:title", "./title"]).text,
            "description": self.xmlparser.find(
                db, ["./zr:description", "./description"]
            ).text,
            "contact": self.xmlparser.find(db, ["./zr:contact", "./contact"]).text,
        }
        return {k: v.strip() if v else v for (k, v) in db_info.items()}

    def _parse_index(self, xml: Element) -> dict[str, dict[str, str | None]]:
        index: defaultdict[str, dict[str, str | None]] = defaultdict(dict)
        index_sets = self.xmlparser.findall(
            xml,
            [
                ".//zr:indexInfo/zr:set",
                ".//zr2:indexInfo/zr2:set",
            ],
        )
        for index_set in index_sets:
            index[index_set.attrib["name"]] = {}

        index_fields = self.xmlparser.findall(
            xml, [".//zr:indexInfo/zr:index", ".//zr2:indexInfo/zr2:index"]
        )
        for index_field in index_fields:
            title = self.xmlparser.find(index_field, ["./zr:title", "./title"]).text
            if title:
                title = title.strip()
            names = self.xmlparser.findall(
                index_field, [".//zr:map/zr:name", ".//zr2:map/zr2:name"]
            )
            for name in names:
                index[name.attrib["set"]][(name.text or "").strip()] = title

        return dict(index)


class AttributeDict(dict[str, Any]):
    def __getattr__(self, attr: str) -> Any:
        return self[attr]

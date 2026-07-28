__version__ = "2.0.0"
__all__ = [
    # public API
    "Client",
    "searchretrieve",
    "explain",
    "SruthiError",
    "ServerIncompatibleError",
    "SruError",
    "NoMoreRecordsError",
    "SruthiWarning",
    "WrongNamespaceWarning",
    # submodules
    "client",
    "errors",
    "response",
    "xmlparse",
]

import requests

from . import client, errors, response, xmlparse
from .client import Client
from .errors import (
    NoMoreRecordsError,
    ServerIncompatibleError,
    SruError,
    SruthiError,
    SruthiWarning,
    WrongNamespaceWarning,
)
from .response import AttributeDict, SearchRetrieveResponse


def searchretrieve(
    url: str,
    query: str,
    start_record: int = 1,
    maximum_records: int = 10,
    record_schema: str | None = None,
    sru_version: str = "1.2",
    session: requests.Session | None = None,
) -> SearchRetrieveResponse:
    c = Client(
        url=url,
        maximum_records=maximum_records,
        record_schema=record_schema,
        sru_version=sru_version,
        session=session,
    )
    return c.searchretrieve(query=query, start_record=start_record)


def explain(
    url: str,
    maximum_records: int = 10,
    record_schema: str | None = None,
    sru_version: str = "1.2",
    session: requests.Session | None = None,
) -> AttributeDict:
    c = Client(
        url=url,
        maximum_records=maximum_records,
        record_schema=record_schema,
        sru_version=sru_version,
        session=session,
    )
    return c.explain()

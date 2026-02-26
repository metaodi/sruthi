from __future__ import annotations

from typing import Any

__version__ = "2.0.0"
__all__ = ["client", "errors", "response", "xmlparse"]

from .errors import (  # noqa
    SruthiError,
    ServerIncompatibleError,
    SruError,
    NoMoreRecordsError,
)
from .errors import SruthiWarning, WrongNamespaceWarning  # noqa
from .client import Client  # noqa
from .response import SearchRetrieveResponse  # noqa


def searchretrieve(url: str, query: str, **kwargs: Any) -> SearchRetrieveResponse:
    search_params = ["query", "start_record"]
    search_kwargs = {k: v for k, v in kwargs.items() if k in search_params}
    search_kwargs["query"] = query

    # assume all others kwargs are for the client
    client_kwargs = {k: v for k, v in kwargs.items() if k not in search_params}
    client_kwargs["url"] = url

    c = Client(**client_kwargs)
    return c.searchretrieve(**search_kwargs)


def explain(url: str, **kwargs: Any) -> Any:
    c = Client(url, **kwargs)
    return c.explain()

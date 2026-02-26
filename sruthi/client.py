from __future__ import annotations

from typing import Any, Dict, Optional
from xml.etree.ElementTree import Element

import requests
from requests import Session

from . import errors
from . import xmlparse
from . import response


class Client:
    def __init__(
        self,
        url: Optional[str] = None,
        maximum_records: int = 10,
        record_schema: Optional[str] = None,
        sru_version: str = "1.2",
        session: Optional[Session] = None,
    ) -> None:
        self.url = url
        self.maximum_records = maximum_records
        self.sru_version = sru_version
        self.record_schema = record_schema
        self.session: Session = session or requests.Session()

    def searchretrieve(
        self, query: str, start_record: int = 1
    ) -> response.SearchRetrieveResponse:
        params: Dict[str, Any] = {
            "operation": "searchRetrieve",
            "version": self.sru_version,
            "query": query,
            "startRecord": start_record,
            "maximumRecords": self.maximum_records,
        }

        if self.record_schema:
            params["recordSchema"] = self.record_schema

        data_loader = DataLoader(self.url, self.session, params)
        return response.SearchRetrieveResponse(data_loader)

    def explain(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "operation": "explain",
            "version": self.sru_version,
        }
        data_loader = DataLoader(self.url, self.session, params)
        explain_response = response.ExplainResponse(data_loader)
        return explain_response.asdict()


class DataLoader:
    def __init__(
        self,
        url: Optional[str],
        session: Session,
        params: Dict[str, Any],
    ) -> None:
        self.session = session
        self.url = url
        self.params = params
        self.response: Optional[Any] = None
        self.xmlparser = xmlparse.XMLParser()

    def load(self, **kwargs: Any) -> Any:
        self.params.update(kwargs)
        xml = self._get_content(self.url, self.params)
        self._check_errors(xml)
        return xml

    def _get_content(self, url: Optional[str], params: Dict[str, Any]) -> Any:
        if url is None:
            raise errors.SruthiError("URL is required")
        try:
            res = self.session.get(url, params=params)
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise errors.SruthiError(f"HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            raise errors.SruthiError(f"Request error: {e}")

        return self.xmlparser.parse(res.content)

    def _check_errors(self, xml: Any) -> None:
        sru = "{http://www.loc.gov/zing/srw/}"
        diag = "{http://www.loc.gov/zing/srw/diagnostic/}"
        diagnostics = self.xmlparser.find(xml, f"{sru}diagnostics/{diag}diagnostic")
        if isinstance(diagnostics, Element):
            error_msg = ", ".join([d.text or "" for d in diagnostics])
            raise errors.SruError(error_msg)

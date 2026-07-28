from xml.etree.ElementTree import Element

import requests

from . import errors, response, xmlparse

#: The query string parameters sent to an SRU endpoint.
SruParams = dict[str, str | int]


class Client:
    def __init__(
        self,
        url: str | None = None,
        maximum_records: int = 10,
        record_schema: str | None = None,
        sru_version: str = "1.2",
        session: requests.Session | None = None,
    ) -> None:
        self.url = url
        self.maximum_records = maximum_records
        self.sru_version = sru_version
        self.record_schema = record_schema
        self.session = session or requests.Session()

    def searchretrieve(
        self, query: str, start_record: int = 1
    ) -> "response.SearchRetrieveResponse":
        params: SruParams = {
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

    def explain(self) -> "response.AttributeDict":
        params: SruParams = {
            "operation": "explain",
            "version": self.sru_version,
        }
        data_loader = DataLoader(self.url, self.session, params)
        explain_response = response.ExplainResponse(data_loader)
        return explain_response.asdict()


class DataLoader:
    def __init__(
        self, url: str | None, session: requests.Session, params: SruParams
    ) -> None:
        self.session = session
        self.url = url
        self.params = params
        self.xmlparser = xmlparse.XMLParser()

    def load(self, **kwargs: str | int) -> Element:
        self.params.update(kwargs)
        xml = self._get_content(self.url, self.params)
        self._check_errors(xml)
        return xml

    def _get_content(self, url: str | None, params: SruParams) -> Element:
        if url is None:
            raise errors.SruthiError("No SRU endpoint URL provided")
        try:
            res = self.session.get(url, params=params)
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise errors.SruthiError(f"HTTP error: {e}") from e
        except requests.exceptions.RequestException as e:
            raise errors.SruthiError(f"Request error: {e}") from e

        return self.xmlparser.parse(res.content)

    def _check_errors(self, xml: Element) -> None:
        sru = "{http://www.loc.gov/zing/srw/}"
        diag = "{http://www.loc.gov/zing/srw/diagnostic/}"
        diagnostics = self.xmlparser.find(xml, f"{sru}diagnostics/{diag}diagnostic")
        if isinstance(diagnostics, xmlparse.XMLNone) or not len(diagnostics):
            return
        error_msg = ", ".join(d.text or "" for d in diagnostics)
        raise errors.SruError(error_msg)

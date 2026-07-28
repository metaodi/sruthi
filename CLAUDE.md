# CLAUDE.md

Guidance for AI assistants working in this repository.

## Project overview

**sruthi** is a small, dependency-light Python client for [SRU (Search/Retrieve via URL)](http://www.loc.gov/standards/sru/), the library/archive search protocol. It supports **SRU 1.1 and 1.2** and the two operations `searchRetrieve` and `explain`.

Published on PyPI as [`sruthi`](https://pypi.org/project/sruthi/). Current version: see `__version__` in `sruthi/__init__.py` (single source of truth — `setup.py` reads it with a regex).

Key design principle: **sruthi makes no assumptions about the record schema.** Record data is returned as-is, as a flattened `dict`. It has been used with `dc`, `marcxml` and `isad`, but nothing in the code is schema-specific beyond XML namespace registration.

## Layout

```
sruthi/
  __init__.py     # public API: searchretrieve(), explain(), Client, errors
  client.py       # Client (builds SRU params) + DataLoader (HTTP + error check)
  response.py     # SearchRetrieveResponse, ExplainResponse, AttributeDict
  xmlparse.py     # XMLParser: namespace-aware find/findall/todict + XMLNone
  errors.py       # exception + warning hierarchy
tests/
  sruthi_test.py  # base TestCase classes (SruthiTestCase, ResponseTestCase)
  sru_test.py     # module-level API (sruthi.searchretrieve / sruthi.explain)
  client_test.py  # Client behaviour, iteration, slicing, warnings
  response_test.py# response parsing against fixtures
  conftest.py     # fixture_content helper + valid_xml pytest fixture
  fixtures/*.xml  # recorded SRU responses (see naming convention below)
examples/         # runnable scripts hitting real SRU endpoints; also linted
.github/workflows/
  lint_python.yml    # PR + push to master: matrix 3.9–3.12, runs ./validate.sh
  publish_python.yml # on tags v*: builds sdist/wheel and uploads to PyPI
```

## Architecture

Data flows in one direction: `Client` → `DataLoader` → `XMLParser` → `Response`.

- **`sruthi/__init__.py`** — the convenience functions. `searchretrieve(url, query, **kwargs)` splits kwargs: `query`/`start_record` go to the search call, *everything else* is assumed to be `Client` constructor args (`maximum_records`, `record_schema`, `sru_version`, `session`). If you add a new search-level parameter, you **must** add it to the `search_params` list, or it will be silently forwarded to `Client()` and raise a `TypeError`.
- **`Client`** (`client.py`) only assembles the SRU query-string params (`operation`, `version`, `query`, `startRecord`, `maximumRecords`, optional `recordSchema`) and hands them to a `DataLoader`. It holds no response state.
- **`DataLoader`** (`client.py`) owns the `requests.Session` and is the *only* place doing HTTP. `requests` exceptions are wrapped into `errors.SruthiError`; SRU `<diagnostic>` elements in the response body become `errors.SruError`. It is re-invoked lazily by `SearchRetrieveResponse` for pagination.
- **`SearchRetrieveResponse`** (`response.py`) is lazily paginating. `records` starts with the first page; `__iter__`, `__getitem__` and slicing call `_load_new_data()` which re-requests with an updated `startRecord` until `nextRecordPosition` is absent (then `NoMoreRecordsError` stops the loop). Negative indices force loading *all* records. Keep this laziness in mind: touching `r[-1]` on a large result set fires many HTTP requests.
- **`ExplainResponse`** parses `serverInfo`/`databaseInfo`/`indexInfo`/`schemaInfo`/`configInfo` and is returned to callers as an `AttributeDict` (a `dict` subclass allowing both `info['server']` and `info.server`) via `Client.explain()` → `asdict()`.
- **`XMLParser`** (`xmlparse.py`) wraps `defusedxml.ElementTree` (never plain `xml.etree` — parsing untrusted remote XML is the whole point) plus `xmltodict`. `find()`/`findall()` accept a **list of paths** and return the first one that matches — this is how alternative namespaces (`zr` 2.1 vs `zr2` 2.0) and non-namespaced servers are handled. Missing elements return the `XMLNone` sentinel (falsy, `.text is None`) instead of `None`, so callers can chain `.text` without guards.
- **Namespace tolerance** is a recurring theme. `XMLParser.namespaces` maps prefixes for XPath lookups; `dict_namespaces` maps URIs to `None` to strip them during `todict()`. Servers using a wrong-but-recognisable SRU namespace trigger a `WrongNamespaceWarning` and the parser rewrites its `sru` prefix on the fly (`Response._check_response_tag`); a genuinely non-SRU response raises `ServerIncompatibleError`.
- **Record flattening** (`_tag_data`) unwraps a single top-level element, drops `schemaLocation`/`xmlns`, and flattens nested dicts to leaf keys via `flatten_dict`. If leaf keys collide, the `ValueError` is swallowed and the nested dict is returned unflattened — so consumers cannot assume a flat shape.

Adding a new schema or a new server quirk usually means: register the namespace in `xmlparse.py`, add a fixture XML under `tests/fixtures/`, and add a test.

## Development workflow

Setup (`./setup.sh` creates a `pyenv/` virtualenv, or install directly):

```bash
make deps          # pip install -r requirements.txt -r test-requirements.txt
pip install -e .
```

Common commands (`make help` lists them):

```bash
make test          # python -m pytest --cov=sruthi tests/
make lint          # black --check + flake8 over sruthi examples tests
make format        # black sruthi examples tests
make coverage      # coverage run + report -m
./validate.sh      # what CI runs: make lint && make test
```

Run a single test: `python -m pytest tests/client_test.py::TestSruthiClient::test_searchretrieve -q`.

Always run `./validate.sh` before committing — CI runs exactly that on Python 3.9–3.12.

## Conventions

- **Code style: `black`** (non-negotiable, CI fails on `black --check`). `setup.cfg` configures flake8 to match: `max-line-length = 88`, `extend-ignore = E203`, `max-complexity = 10`. Run `make format` rather than hand-formatting.
- **f-strings** throughout (the codebase was migrated away from `%`/`.format()`); `setup.py` is the one remaining exception.
- **Python support**: `python_requires='>=3.7'` in `setup.py`, but CI tests 3.9–3.12. Do not use syntax newer than the declared floor without also updating `setup.py` classifiers and the CI matrix.
- **Dependencies are deliberately few**: `requests`, `defusedxml`, `xmltodict`, `flatten-dict`. Adding one needs a good reason and must be added to *both* `requirements.txt` and `install_requires` in `setup.py`.
- **Errors**: everything derives from `SruthiError`; warnings from `SruthiWarning`. Raise the specific subclass, and export new ones from `sruthi/__init__.py`.
- **Every user-visible change gets a CHANGELOG.md entry** under `## [Unreleased]`, using the Keep-a-Changelog categories listed at the bottom of that file.
- New features should come with a runnable script in `examples/` when they change the public API — examples are linted, so they must be black-clean.

## Testing

- `unittest`-style `TestCase` classes, executed by pytest. Files are named `*_test.py` (not `test_*.py`); pytest picks both up by default.
- Tests import each other by bare module name (`from sruthi_test import SruthiTestCase`). This works because `tests/` has no `__init__.py` and pytest prepends the test file's directory to `sys.path` — **run pytest from the repository root**, and don't add an `__init__.py` to `tests/`.
- **No network access in tests.** `SruthiTestCase.setUp` patches `sruthi.client.requests.Session` and feeds it canned XML.
- **Fixture naming is magic**: `_test_content()` defaults to `<test-method-name>.xml` in `tests/fixtures/`. Adding `test_foo` to a `SruthiTestCase` subclass automatically loads `tests/fixtures/test_foo.xml` as the mocked response. If the file doesn't exist, the mock returns empty content instead of failing — so a missing fixture shows up as a confusing parse error, not a missing-file error.
- `ResponseTestCase._data_loader_mock([...])` takes a *list* of fixture filenames and returns them successively from `load()` — that's how multi-page pagination (`response_multiple_1/2/3.xml`) is tested without HTTP.
- Fixtures are real recorded server responses (Staatsarchiv Zürich, DNB, KB, LoC). When adding one, trim it to the minimum needed to exercise the case.

## Branching and release

- **Default branch is `develop`.** Target `develop` for new/changed functionality; `master` is only for urgent bugfixes (see `CONTRIBUTING.md`). Releases are merges of `develop` into `master`.
- Release process: bump `__version__` in `sruthi/__init__.py` → update `CHANGELOG.md` (move Unreleased items under the new version, add the compare link) → PR `develop` → `master` → create a GitHub release/tag `vX.Y.Z` on `master`. The `publish_python.yml` workflow uploads to PyPI on `v*` tags.
- Semantic Versioning. BC-breaks are called out explicitly in the CHANGELOG.

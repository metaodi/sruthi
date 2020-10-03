# Changelog
All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project follows [Semantic Versioning](http://semver.org/).

## [Unreleased]

## [0.1.1] - 2020-10-04
### Fixed
- Fix distribution to PyPI

## [0.1.0] - 2020-10-04
### Added
- Add `record_schema` parameter
- Add new dependencies to xmltodict and flatten-dict

### Changed
- recordData is now returned as flattened dict (if possible)

### Fixed
- Fix typo in `searchRetrieve` operation name

## [0.0.5] - 2020-06-10
### Changed
- Remove dependencies to convert md to rst
- Directly provide markdown to PyPI

## [0.0.4] - 2020-06-10
### Fixed
- Fix description text on PyPI

## [0.0.3] - 2020-06-10
### Fixed
- Fixed publish workflow to not create release
- Add missing modules to `__all__`

## [0.0.2] - 2020-06-10
### Added
- Support for explain operation
- Response classes
- Tests for the existing functionality
- `maximum_records` parameter for Client
- Example scripts in the `examples` directory
- CHANGELOG.md and CONTRIBUTING.md

### Changed
- XMLParser is now a class, so that XML namespaces can be changed on-the-fly

## [0.0.1] - 2020-05-23
### Added
- Initial release of sruthi
- basic support for searchretrieve operation



# Categories
- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for once-stable features removed in upcoming releases.
- `Removed` for deprecated features removed in this release.
- `Fixed` for any bug fixes.
- `Security` to invite users to upgrade in case of vulnerabilities.

[Unreleased]: https://github.com/metaodi/sruthi/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/metaodi/sruthi/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/metaodi/sruthi/compare/v0.0.5...v0.1.0
[0.0.5]: https://github.com/metaodi/sruthi/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/metaodi/sruthi/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/metaodi/sruthi/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/metaodi/sruthi/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/metaodi/sruthi/releases/tag/v0.0.1

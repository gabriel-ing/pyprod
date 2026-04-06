# Changelog

## [0.1.2] - 2026-04-06

### Fixed
- BO MessageMap now accepts f-string based keys
- BO MessageMap can now also be named `message_map` or `Message_Map`.
- IRISProperty now accepts `num` as a data type and maps it to `%Library.Numeric`

### Changed
- Added a new environement variable to installation steps to account for containers running on Windows
- Added IRIS kit `iris-community:2026.1` to list of kits used in automated tests

## [0.1.1] - 2026-03-10

### Fixed
- Prevention of sys.path growth when Business Processes share common pool CPU jobs

### Changed
- README and installation documentation updates

## [0.1.0] - 2026-01-21

### Added
- Initial public release.
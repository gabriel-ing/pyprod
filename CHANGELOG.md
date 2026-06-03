# Changelog

  ## [0.2.0] - 2026-06-03

  ### Added
  - `Production` class for declarative, code-first production definitions
  - `ServiceItem`, `ProcessItem`, and `OperationItem` for declaring business host config items with host and adapter settings
  - `director` module wrapping `Ens.Director` — provides `start_production`, `stop_production`, `restart_production`,  `update_production`, `get_production_status`, `clean_production`, `enable_config_item`, `list_all_productions`, `get_host_messages`,  and `create_business_service`
  - Load-time validation of `host_settings` and `adapter_settings` key names against IRIS class definitions, with warnings for unrecognised properties
  - Load-time validation of unknown attributes on `Production` subclasses

  ### Changed
  - README updated with programmatic production creation example and director usage
  - API reference expanded with full documentation for `Production`, `ServiceItem`, `ProcessItem`, `OperationItem`, and the `director` module
  - Quick Start guide updated with Step 9 covering production definition and programmatic startup
  - Removed IRIS kit iris-community:2024.3 from list of kits used in automated tests

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
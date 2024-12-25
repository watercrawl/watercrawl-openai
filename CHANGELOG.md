# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-25

### Added
- Initial release of WaterCrawl OpenAI Plugin
- Enhanced OpenAI plugin schema with configurable options
- Added support for GPT-4O and GPT-4O Mini models
- Implemented JSON schema validation for extractor configuration
- Added customizable prompt support
- Improved UI configuration with textarea and JSON editor widgets
- Added cached property decorator for better performance

### Changed
- Updated dependency to use watercrawl-plugin>=0.1.0
- Migrated from openai._compat to functools for cached_property
- Improved input validation with JSON schema-based configuration

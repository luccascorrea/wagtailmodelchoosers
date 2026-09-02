# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

## [1.10.0] - 2026-09-02

### Added
- Official support for **Wagtail 5.2.8 (LTS)** and the Wagtail 5.2.x series.
- Added official support and PyPI classifier for **Django 5.0** (`Framework :: Django :: 5.0`).
- Enhanced `ModelChooserWidget.get_edit_endpoint()` to resolve Wagtail 5.2 generic `ModelViewSet` edit routes (`<model_name>:edit`, `<app>_<model_name>:edit`) and Wagtail Page edit routes (`wagtailadmin_pages:edit`) for Page subclasses.
- Expanded `django-filter` dependency ceiling in `setup.py` from `<=23.0` to `<25.0` to resolve packaging conflicts with Wagtail 5.2's requirement of `django-filter>=23.3,<24`.
- Added `wt52: wagtail>=5.2,<5.3` and `dj50: Django>=5.0,<5.1` test environments to `tox.ini`.
- Expanded automated test suite to **100 tests** covering `ModelViewSet` edit routes, Page edit routes, and StreamField values serialization with 0 failures and 0 warnings.

### Verified
- Verified compatibility with Wagtail 5.2.8 source code and release fixes (including CVE-2024-39317, StreamField null value migrations, and lazy block loading).
- Verified full test suite passes with 100% success rate (100/100 tests) and 86% overall code coverage.


## [1.9.0] - 2026-09-01

### Added
- Official support for **Wagtail 5.1.3** (and Wagtail 5.1.x series).
- Added `read_only` and `attrs` support to `ModelChooserPanel` and `RemoteModelChooserPanel`.
- Implemented `format_value_for_display(self, value)` on `ModelChooserPanel` and `RemoteModelChooserPanel` to support Wagtail 5.1 read-only panel rendering.
- Enhanced `ModelChooserWidget.get_edit_endpoint()` to resolve modern `SnippetViewSet` URL patterns (`wagtailsnippets_<app>_<model>:edit` and `wagtailsnippets:edit`) prior to legacy ModelAdmin.
- Added `wt51: wagtail>=5.1,<5.2` to `tox.ini` matrix.
- Expanded test suite to **95 tests** with comprehensive test coverage for `read_only`, `attrs`, `format_value_for_display`, snippet edit URL routing, and admin hooks.

### Changed
- Migrated admin CSS injection hook in `wagtail_hooks.py` from deprecated `insert_editor_css` to `insert_global_admin_css` to eliminate `RemovedInWagtail60Warning`.

### Verified
- Verified 0 deprecation warnings emitted from `wagtailmodelchoosers` under Wagtail 5.1.3.
- Verified test suite passes with 100% success rate across all 95 tests with 87% code coverage.


## [1.8.0] - 2026-08-26

### Added
- Official support for **Wagtail 5.0.5** and **Django 4.2 (LTS)**.
- Enhanced `ModelChooserPanel` and `RemoteModelChooserPanel` to support `icon` and `base_form_class` parameters.
- Implemented standard `clone_kwargs()` method on `ModelChooserPanel` and `RemoteModelChooserPanel` for seamless Wagtail panel cloning.
- Added `TitleFieldPanel` support in `tests/testapp/` for title and slug synchronization with Stimulus `w-sync`.
- Expanded test suite to **74 tests** verifying panel options (`icon`, `base_form_class`), cloning kwargs, and `ReferenceIndex` integration.
- Added semantic surface tokens and CSS custom property fallbacks for dark mode compatibility in modal picker.
- Added `wt50: wagtail>=5.0,<5.1` test environments in `tox.ini`.
- Added PyPI classifier `Framework :: Wagtail :: 5` and updated package constraints to `'wagtail>=2.0,<6.0'`.

### Changed
- Removed deprecated `BASE_URL` setting from test application in favor of standard `WAGTAILADMIN_BASE_URL`.

### Verified
- Verified compatibility with Wagtail 5.0.5's complete removal of `wagtail.core` and `wagtail.admin.edit_handlers`.
- Verified `extract_references()` behavior in `ModelChooserBlock` and `RemoteModelChooserBlock` under Wagtail 5.0's optimized `ReferenceIndex`.
- Verified DRF API proxy views, serialization, and filtering under Wagtail 5.0.5 with 0 failures and 0 warnings.

## [1.7.0] - 2026-08-20

### Added
- Official compatibility and test coverage for **Wagtail 4.2.4 (LTS)**.
- Expanded `tox.ini` matrix testing covering Wagtail 4.2 across Django 3.2, 4.0, 4.1, 4.2 and Python 3.8–3.12.
- Additional test cases for Wagtail 4.2 panel binding lifecycles, clone methods, and revision diffing comparisons (`ModelComparison`, `ChildModelComparison`).

### Verified
- Verified compatibility with Wagtail 4.2 panel submodule reorganization (`wagtail.admin.panels`).
- Verified `extract_references` behavior in `ModelChooserBlock` and `RemoteModelChooserBlock` for `ReferenceIndex` traversal.
- Verified Willow image pipeline compatibility with thumbnail resolution.

# [0.4.2] - 2018-08-20

### Added

Added custom inline panel that makes viewing revisions possible.

# [0.4.1] - 2018-08-17

### Added

Added button for editing related model.

# [0.4.0] - 2018-07-30

### Added

Added option to allow alternating between additive/exclusive filters.


# [0.3.0] - 2018-07-24

### Added

Added option to allow displaying a thumbnail along with chooser and picker.


# [0.2.0] - 2018-07-23

### Added

Added side panel to the model picker in order to display dynamic filters.


# [0.1.2] - 2017-08-22

### Fixed

Infinite loop when the `display` option is an array.

# [0.1.1] - 2017-07-13

### Fixed

Compatibility with IE11

## [0.1.0] - 2017-04-27

Initial Release

[Unreleased]: https://github.com/springload/wagtailmodelchoosers/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/springload/wagtailmodelchoosers/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/springload/wagtailmodelchoosers/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/springload/wagtailmodelchoosers/compare/d6c8c2925e23a2473a1f051c6135fc72b1793761...v0.1.0

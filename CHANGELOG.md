# Changelog

## 1.1.2 (2026-01-31)

```diff
+   | Added timezone, language, and accept_language configuration options to context
```

## 1.1.1 (2026-01-31)

```diff
    | Fixed config being defaulted to blank when unset
+   | Added explicit page return on authentication rather than creating a new page after authentication
    | Fixed pages not being checked for successful navigation in handshake navigator
```

## 1.1.0 (2026-01-30)

```diff
    | Fixed handshake auth handler not being able to fill password fields
+   | Added context injector support
+   | Added FlareSolverr injector
+   | Added playwright stealth support
+   | Added a whole bunch of logging
+   | Added timeout configuration options and overrides
    | Restructured config into individual sections for context, auth, extractors, etc.
```

## 1.0.4 (2026-01-28)

```diff
    | Fixed broken page wait in Handshake auth handler
```

## 1.0.3 (2026-01-28)

```diff
+   | Added configurable user data directory
+   | Added automatic termination to Handshake auth handler after detecting successful login URL at any point during navigation
```

## 1.0.2 (2026-01-28)

```diff
+   | Added configuration support for auth handler types
```

## 1.0.1 (2026-01-28)

```diff
    | Changed name of argument `metadata_download_dir` to `metadata_download_directory`
+   | Added instructions for installing the package via pip in the README
```

## 1.0.0 (2025-08-30)

```diff
    | Initial release of the project with basic Looker metadata extraction capabilities
+   | Added support for Handshake authentication method
+   | Added support for General authentication method
+   | Added support for No authentication method
+   | Added support for Handshake Looker navigation
+   | Added support for query extraction
+   | Added support for explore extraction
+   | Added support for model extraction
+   | Added persistent context management
+   | Added download management for extractions so that extracted files are organized
```

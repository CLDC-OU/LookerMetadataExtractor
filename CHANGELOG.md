# Changelog

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

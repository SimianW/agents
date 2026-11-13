## Changelog

`CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/): one entry per release, newest first, its changes grouped under `###` category headings. <When an entry is written, such as "Add the entry in the PR that changes the version.">

```markdown
## [<a version in this repo's format>] - YYYY-MM-DD

### Changed

- Redesigned the settings page: ...

### Fixed

- Fixed a crash when opening settings.
```

Use these categories, in this order, and only the ones the release has:

| Category | For | Example |
|---|---|---|
| Added | new features | Added dark mode support. |
| Changed | changes to existing features | Improved the settings UI. |
| Fixed | bug fixes | Fixed a crash when opening settings. |
| Removed | removed features | Removed legacy API support. |
| Deprecated | features to be removed later | Deprecated the old authentication API. |
| Security | security fixes | Fixed an XSS vulnerability. |
| Performance | speed and resource use | Reduced startup time by 30%. |

A problem the release ships with goes last, under `### Known issues`.

Each bullet is one change the user can notice, opening with a past-tense verb ("Added", "Fixed", "Reduced"); a known issue instead describes the problem. Name what the user sees, keep the bullet short, and give the measured number for a performance change when there is one. Leave out changes only developers see (tests, CI, tooling).

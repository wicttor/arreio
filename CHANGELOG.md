# Changelog

All notable changes to Arreio are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Versions prior to 1.0.5 predate this changelog. See `git log` for historical commits.

## [1.0.5] - 2026-09-02

### Fixed

- **Postinstall script targeted wrong directory.** When Arreio was installed as a dependency, the `postinstall` script used `process.cwd()`, which inside `node_modules/arreio/` points to the package directory itself — not the consuming project. Skills were being copied to `node_modules/arreio/.agents/skills/` instead of `<project>/.agents/skills/`. Switched the destination base to `process.env.INIT_CWD || process.cwd()`, which npm sets to the original invocation directory during lifecycle scripts.

### Documentation

- **README: clarified npm 10+ install-script behavior.** Replaced the misleading "informational advisory" note with actionable guidance. npm 10+ blocks lifecycle scripts by default; users must run `npm install-scripts approve arreio` to run the postinstall, or invoke `/arreio-init` in their AI coding agent to install skills manually.
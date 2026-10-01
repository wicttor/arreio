# Changelog

All notable changes to Arreio are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Versions prior to 1.0.5 predate this changelog. See `git log` for historical commits.

## [Unreleased]

### Added

- **`/plan --deep` flag.** Forces the Deep plan tier in any interaction mode (including Autopilot), skipping the tier question. `tier_recommended` still records the algorithm's result so the override is auditable. The Design phase also produces ≥ 2 alternatives and rollout/integration drafts when the flag is set.

### Fixed

- **Work/Review/Learn reliability pass.** Each skill gets an "Execution Rules" block (ordered steps, no invented values, compute-don't-copy, one question at a time, phase-transition announcements, write rules). Work's execution-mode selection now states first-match-wins evaluation, treats `serial` as a fallback only, and builds its Detailed-mode question (with an `Auto` option) from computed values. `--deep` stays Plan-only: the other skills have no plan tier.
- **Plan tier no longer collapses to Standard.** The tier prompt hardcoded "Auto … (result: Standard)" and its example contradicted the algorithm (HIGH complexity → Deep). The prompt is now built from computed values, `Auto` resolves to `tier_recommended`, and Design computes `tier_recommended` with the same `recommend_tier(complexity, risk_level)` function Generate re-checks.
- **Complexity scoring consistency.** Risk now maps to a fixed score (LOW 0, MEDIUM 1, HIGH 2, CRITICAL 3); the missing-risk default is MEDIUM = 1 (was documented as 2); each dimension requires cited evidence.

### Changed

- **Intermediate phase artifacts are now written only in `detailed` mode.** In `smart` and `autopilot` mode, the plan, work, review, and learn pipelines pass phase artifacts in context instead of writing hidden files (`.scope/`, `.research/`, `.design/`, `.triage/`, `.prepare/`, `.execute/`, `.analyze/`, `.capture/`, `.refine/`, `.index/`, `.maintain/`). Final deliverables (plans, tasks, Work Reports, Review Reports, learn entries) are still always written. `arreio-init` no longer pre-creates the intermediate directories.

## [1.0.5] - 2026-09-02

### Fixed

- **Postinstall script targeted wrong directory.** When Arreio was installed as a dependency, the `postinstall` script used `process.cwd()`, which inside `node_modules/arreio/` points to the package directory itself — not the consuming project. Skills were being copied to `node_modules/arreio/.agents/skills/` instead of `<project>/.agents/skills/`. Switched the destination base to `process.env.INIT_CWD || process.cwd()`, which npm sets to the original invocation directory during lifecycle scripts.

### Documentation

- **README: clarified npm 10+ install-script behavior.** Replaced the misleading "informational advisory" note with actionable guidance. npm 10+ blocks lifecycle scripts by default; users must run `npm install-scripts approve arreio` to run the postinstall, or invoke `/arreio-init` in their AI coding agent to install skills manually.
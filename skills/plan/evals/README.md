# Plan evals

Scenario evals for the `plan` skill. Each JSON file gives a query, the files it needs, the interaction mode, and the behavior a correct run shows. Run each scenario on Haiku, Sonnet, and Opus and compare against `expected_behavior`.

`fixtures/` also holds a good and a bad plan for the coverage gate; check them mechanically:

```bash
cd skills/plan/evals/fixtures
python ../../scripts/check-plan.py plan-good.md --source milestone-source.md --section '^## 8\.'   # PASS, exit 0
python ../../scripts/check-plan.py plan-bad.md  --source milestone-source.md --section '^## 8\.'   # FAIL, exit 1
```

`plan-bad.md` reproduces the defects found in a real run (orphan unit, out-of-order IDs, backward dependency, "as needed" files, unit blow-up, missing source items and test IDs).

`fixtures/plan-files-bad.md` exercises the repository checks (`--repo fixtures/repo-stub`): a `Create` path that exists, a `Modify` path that does not, a file created by two units, and a stated file count that disagrees with the lists. `m2-codebase-grounded.json` replays the soulcrystals M2 plan, whose review found layering, seam, clock, data-asset, hook and persistence gaps that the earlier source-bound fixes did not target; check its behaviors by reading the Design Artifact's Codebase Trace and Integrity Checks.

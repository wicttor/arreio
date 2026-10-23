# Review evals

Scenario evals for the `review` skill. Each JSON file gives a query, the files it needs, the interaction mode, and the behavior a correct run shows. Run each scenario on Haiku, Sonnet, and Opus and compare against `expected_behavior`.

`fixtures/` also holds a coherent task-in-review report with the task folder it should leave behind, and a broken report; check them mechanically:

```bash
cd skills/review/evals/fixtures
python ../../scripts/check-review.py report-good.md --registry registry.md --tasks tasks-after-good   # PASS, exit 0
python ../../scripts/check-review.py report-bad.md  --registry registry-dupe.md --tasks tasks-after-good   # FAIL, exit 1
```

`report-bad.md` reproduces the defects found when auditing the 1.3.x skill: an approval status that does not follow from the findings, a rollup that does not match them, a `major` finding without evidence, a finding with both a trace and a creep flag, an absolute path, a duplicated id, acceptance on a non-creep finding, verdicts that contradict the findings and the task files, and a duplicated registry row.

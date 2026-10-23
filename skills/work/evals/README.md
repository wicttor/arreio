# Work evals

Scenario evals for the `work` skill. Each JSON file gives a query, the files it needs, the interaction mode, and the behavior a correct run shows. Run each scenario on Haiku, Sonnet, and Opus and compare against `expected_behavior`.

`fixtures/` also holds a coherent run and a broken run for the coherence gate; check them mechanically:

```bash
cd skills/work/evals/fixtures
python ../../scripts/check-work.py run-good --plan plan-coverage.md   # PASS, exit 0 (T03 held at for-review is a warning)
python ../../scripts/check-work.py run-bad  --plan plan-coverage.md   # FAIL, exit 1
python ../../scripts/check-work.py run-good --require-complete        # FAIL, exit 1 (T03 is not completed)
```

`run-bad` reproduces the defects found when auditing the 1.3.x skill: a task flipped back from completed to for-review with its checkboxes still ticked, a task left in-progress, two test files on one task, an orphan unit, and a duplicated Work Report block.

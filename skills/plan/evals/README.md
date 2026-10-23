# Plan evals

Scenario evals for the `plan` skill. Each JSON file gives a query, the files it needs, the interaction mode, and the behavior a correct run shows. Run each scenario on Haiku, Sonnet, and Opus and compare against `expected_behavior`.

`fixtures/` also holds a good and a bad plan for the coverage gate; check them mechanically:

```bash
cd skills/plan/evals/fixtures
python ../../scripts/check-plan.py plan-good.md --source milestone-source.md --section '^## 8\.'   # PASS, exit 0
python ../../scripts/check-plan.py plan-bad.md  --source milestone-source.md --section '^## 8\.'   # FAIL, exit 1
```

`plan-bad.md` reproduces the defects found in a real run (orphan unit, out-of-order IDs, backward dependency, "as needed" files, unit blow-up, missing source items and test IDs).

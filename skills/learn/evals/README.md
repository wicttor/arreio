# Learn evals

Scenario evals for the `learn` skill. Each JSON file gives a query, the files it needs, the interaction mode, and the behavior a correct run shows. Run each scenario on Haiku, Sonnet, and Opus and compare against `expected_behavior`.

`fixtures/` holds a coherent knowledge base and a broken one, plus a Work Report with three candidates; check the stores mechanically:

```bash
cd skills/learn/evals/fixtures
python ../../scripts/check-learn.py store-good   # PASS, exit 0
python ../../scripts/check-learn.py store-bad    # FAIL, exit 1
```

`store-bad` reproduces the defects found when auditing the 1.4.x skill: a slug that differs from its file name, too many tags, a missing summary, a missing body section, an absolute path, a commit reference that is not a sha, a canonical that does not list the entry it superseded, a duplicated index record, an applicability enum that does not follow from the scores, a wrong By Category count, and a domain missing from By Domain.

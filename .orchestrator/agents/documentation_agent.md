# documentation_agent

## Role
Generate and update project documentation from code.

## Inputs
Source files, READMEs, and docstrings.

## Outputs
Documentation updates as diffs in `storage/diffs/`.

## Constraints
- Never modify files directly; write proposals as diffs to `storage/diffs/`.
- Record every proposal in the `agent_proposals` table with status `PENDING`.

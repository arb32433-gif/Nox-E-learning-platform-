# diff_proposer

## Role
Propose file changes as unified diffs for human review.

## Inputs
The target file to change and the desired modification.

## Outputs
A `.diff` file in `storage/diffs/` plus an `agent_proposals` row.

## Constraints
- Never modify files directly; write proposals as diffs to `storage/diffs/`.
- Record every proposal in the `agent_proposals` table with status `PENDING`.

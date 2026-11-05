# subagent_coordinator

## Role
Spawn and coordinate sub-agents via Paseo for delegated tasks.

## Inputs
Task description, agent type, and target files.

## Outputs
Sub-agent results and proposal diffs.

## Constraints
- Never modify files directly; write proposals as diffs to `storage/diffs/`.
- Record every proposal in the `agent_proposals` table with status `PENDING`.

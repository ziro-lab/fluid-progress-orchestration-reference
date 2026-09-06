---
{
  "schema_name": "fpo.record",
  "schema_version": "0.2",
  "record_type": "plan_unit_state",
  "record_id": "UNITSTATE-0001",
  "logical_id": "UNITSTATE-W-EXAMPLE-UNIT-001",
  "record_revision": 1,
  "work_id": "W-EXAMPLE",
  "base_state_revision": 0,
  "sequence": 20,
  "actor": {
    "id": "runtime-1",
    "role": "runtime",
    "authority": "execution_projection"
  },
  "created_at": "2026-08-25T07:30:00Z",
  "bundle_id": "Fluid-Progress-Orchestration-v0.2-Architectural-Hardening-Candidate",
  "bundle_revision": "0.2-candidate-2",
  "policy_revision": "FPO-v0.2",
  "sensitivity": "internal",
  "retention_class": "work_standard",
  "payload": {
    "plan_ref": "records/PLAN-0001.md",
    "unit_id": "UNIT-001",
    "state": "blocked",
    "attempt_refs": [
      "attempts/ATT-0001.md"
    ],
    "operation_refs": [
      "records/OP-0001.md"
    ],
    "effect_refs": [
      "records/EFF-0001.md"
    ],
    "adopted_result_refs": [],
    "blocked_by_refs": [
      "records/BLK-0001.md"
    ],
    "target_revision_refs": [
      "TARGET-R0"
    ],
    "last_event_ref": "records/EVT-0001.md"
  }
}
---

Immutable Plan Unit transition/source record. Current projection carries a rebuildable cache and references this record.

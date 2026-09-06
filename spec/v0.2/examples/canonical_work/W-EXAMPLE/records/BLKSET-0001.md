---
{
  "schema_name": "fpo.record",
  "schema_version": "0.2",
  "record_type": "blocker_set",
  "record_id": "BLKSET-0001",
  "logical_id": "BLKSET-W-EXAMPLE",
  "record_revision": 1,
  "work_id": "W-EXAMPLE",
  "base_state_revision": 0,
  "sequence": 14,
  "actor": {
    "id": "p5-owner",
    "role": "P5",
    "authority": "blocker_case"
  },
  "created_at": "2026-08-25T07:30:00Z",
  "bundle_id": "Fluid-Progress-Orchestration-v0.2-Architectural-Hardening-Candidate",
  "bundle_revision": "0.2-candidate-2",
  "policy_revision": "FPO-v0.2",
  "sensitivity": "internal",
  "retention_class": "work_standard",
  "payload": {
    "active_blocker_refs": [
      "records/BLK-0001.md"
    ],
    "blocking_count": 1,
    "waiting_count": 0,
    "scope_summary": [
      "UNIT-001 blocked by unknown operation/effect"
    ],
    "last_p5_decision_ref": "records/EVT-0001.md"
  }
}
---

Blocker set projection example.

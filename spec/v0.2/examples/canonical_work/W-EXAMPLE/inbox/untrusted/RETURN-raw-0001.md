---
{
  "$schema": "urn:fpo:v0.2:fpo-records",
  "schema_name": "fpo.capability_return",
  "schema_version": "0.2",
  "message_type": "capability_return",
  "return_id": "RET-RAW-0001",
  "work_id": "W-EXAMPLE",
  "logical_intent_id": "INT-001",
  "dispatch_id": "DISP-0001",
  "attempt_id": "ATT-0001",
  "remote_operation_id": "REMOTE-0001",
  "provider_identity": "provider.example/code-agent",
  "capability_id": "code.general",
  "capability_revision": "1.0",
  "provider_sequence": 2,
  "operation_state": "unknown",
  "partial": true,
  "observed_definition_ref": "records/DEF-0001.md",
  "observed_plan_ref": "records/PLAN-0001.md",
  "observed_target_revision_ref": "TARGET-R0",
  "observed_policy_revision": "FPO-v0.2",
  "artifact_refs": [
    "staging/output/normalized.txt"
  ],
  "evidence_candidate_refs": [],
  "effect_update_refs": [
    "records/EFF-0001.md"
  ],
  "diagnostic_facts": [
    "provider response channel closed after operation start"
  ],
  "error_summary": "Terminal outcome not confirmed; reconcile before retry.",
  "created_at": "2026-08-25T07:30:00Z"
}
---

Untrusted provider Return. Schema-valid does not mean adopted or trusted.

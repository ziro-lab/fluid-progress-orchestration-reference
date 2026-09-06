from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

EXPECTED_FLOW_COMMIT = "462055e88346d7531c9494e011d2c1d19128f20a"
EXPECTED_FLOW_ARCHIVE_SHA256 = "454f835efac1f09d774ccc3a4bce76352761f208a6dffba9305b646f2d18f93c"
EXPECTED_PARALLEL_ARCHIVE_SHA256 = "b4004d8afadddc20da998ff84b1ee0682b2b311614e04dec5232833b3fe9b2be"

errors: list[str] = []
passes: list[str] = []


def ok(name: str, condition: bool) -> None:
    (passes if condition else errors).append(name)


def load(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"load {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"object required: {path.relative_to(ROOT)}")
        return {}
    return value


cap = load(HERE / "CAPABILITY.json")
binding = load(HERE / "BINDING.json")
composition_path = ROOT / "CURRENT_FLOW_MINI_COMPOSITION.md"
composition = composition_path.read_text(encoding="utf-8") if composition_path.is_file() else ""

provider = binding.get("provider", {}) if isinstance(binding, dict) else {}
flow = binding.get("flow_mini", {}) if isinstance(binding, dict) else {}
parallel = binding.get("parallel", {}) if isinstance(binding, dict) else {}
dispatch = binding.get("dispatch_binding", {}) if isinstance(binding, dict) else {}
ret = binding.get("return_binding", {}) if isinstance(binding, dict) else {}
failure = binding.get("failure_policy", {}) if isinstance(binding, dict) else {}
field = binding.get("live_field_gate", {}) if isinstance(binding, dict) else {}

ok("capability id", cap.get("capability_id") == "codex.flow-mini")
ok("capability revision", cap.get("revision") == "1")
ok("capability binding ref", cap.get("binding_ref") == "capabilities/flow_mini/BINDING.json")
ok("binding capability id", binding.get("capability_id") == cap.get("capability_id"))
ok("binding capability revision", binding.get("capability_revision") == cap.get("revision"))
ok("binding id", binding.get("binding_id") == "codex.flow-mini@1")

ok("provider repository", provider.get("repository") == "ziro-lab/Flow-Mini-Harness")
ok("provider identity", cap.get("provider_identity") == f"codex-plugin:{provider.get('repository')}")
ok("provider commit format", bool(re.fullmatch(r"[a-f0-9]{40}", str(provider.get("commit", "")))))
ok("provider commit exact", provider.get("commit") == EXPECTED_FLOW_COMMIT)
ok("plugin identity", provider.get("plugin_name") == "flow-mini-harness" and provider.get("plugin_version") == "0.1.1")
ok("bundle identity", provider.get("bundle_path") == "plugin/BUNDLE.json" and provider.get("bundle_version") == "0.1.1")

ok("flow version", flow.get("version") == "0.5.0")
ok("flow controller", flow.get("controller_revision") == "FM-EXEC-0.5.0-r3")
ok("flow archive hash", flow.get("source_archive_sha256") == EXPECTED_FLOW_ARCHIVE_SHA256)
ok("parallel explicit", parallel.get("activation") == "explicit")
ok("parallel profile", parallel.get("profile_version") == "0.1.2.1")
ok("parallel archive hash", parallel.get("profile_archive_sha256") == EXPECTED_PARALLEL_ARCHIVE_SHA256)
ok("parallel runtime not overclaimed", parallel.get("runtime_proven") is False)

required_dispatch = {
    "attempt_id",
    "capability_id",
    "capability_revision",
    "binding_ref",
    "definition_ref",
    "plan_ref",
    "target_revision_ref",
    "policy_revision",
}
ok("dispatch exact binding coverage", required_dispatch.issubset(set(dispatch.get("freeze_into_dispatch", []))))
ok("dispatch binding ref", dispatch.get("binding_ref") == cap.get("binding_ref"))

required_return = {
    "dispatch_id",
    "attempt_id",
    "provider_identity",
    "capability_id",
    "capability_revision",
}
required_reconcile = {
    "binding_ref",
    "definition_ref",
    "plan_ref",
    "target_revision_ref",
    "policy_revision",
}
ok("return identity coverage", required_return.issubset(set(ret.get("must_match_return_fields", []))))
ok("current dispatch reconciliation coverage", required_reconcile.issubset(set(ret.get("reconcile_through_current_dispatch_or_operation", []))))
ok("done not acceptance", ret.get("flow_mini_done_is_fpo_acceptance") is False)
ok("done not close", ret.get("flow_mini_done_is_fpo_close") is False)

ok("missing binding fails closed", failure.get("missing_or_mismatched_binding") == "do_not_dispatch")
ok("silent revision fallback disabled", failure.get("silent_revision_fallback") is False)
ok("unknown effect reconciles", failure.get("unknown_effect") == "reconcile_before_retry")
ok("complex recovery returns to P5", failure.get("complex_recovery") == "return_to_fpo_p5")

ok("live field gate remains unproven", field.get("status") == "NOT_RUN")
ok("live field cases", {"S7", "S8"}.issubset(set(field.get("required_cases", []))))
ok("capability live proof not overclaimed", cap.get("fitness", {}).get("current_plugin_live_proven") is False)

ok("composition exists", bool(composition))
ok("composition binds capability", "capabilities/flow_mini/CAPABILITY.json" in composition and "capabilities/flow_mini/BINDING.json" in composition)
ok("composition pins provider commit", EXPECTED_FLOW_COMMIT in composition)
ok("composition keeps root doc non-core", "NOT CORE / NOT SPEC" in composition)

for name in passes:
    print(f"PASS - {name}")
for name in errors:
    print(f"FAIL - {name}")

if errors:
    print(f"FAILED: {len(errors)}")
    sys.exit(1)
print(f"ALL FLOW MINI BINDING CHECKS PASS ({len(passes)})")

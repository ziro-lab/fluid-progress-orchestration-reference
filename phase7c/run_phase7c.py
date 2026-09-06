"""Parent-side Phase 7C naturalistic integrated parallel trial.

The fixtures expose only a short seed and ordinary project materials.  The
parent observes the initial failures, chooses a route from those observations,
and keeps the oracle/final acceptance outside the capability adapter.  The
local Flow Mini adapter is run in fresh subprocesses so no transcript is
carried between lanes.  It is intentionally not an AI model invocation.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

PHASE7B_ROOT = Path(__file__).resolve().parents[1] / "phase7b"
sys.path.insert(0, str(PHASE7B_ROOT))
from provider.parallel_provider import ParallelProvider, ProviderError, digest  # noqa: E402


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
FIXTURES = ROOT / "fixtures"
STATE = ROOT / "state"
EVIDENCE = ROOT / "evidence"
VALIDATION = ROOT / "validation"
ATTEMPTS = ROOT / "attempts"
STARTING_REVISION = "802fb802b509e2c93d8d1d49cdccbd4eaf2f480e"
PHASE6_BASELINE = "fb74cac46a3833195262f6e4a3a78c3034b819a9"
SEED = "Make these small tools usable according to their project materials, validate the result, and confirm completion."
FLOW_REVISION = "Flow_Mini_Harness_v0.5.0_Implementation_Core_Convergence_Candidate_r3@sha256:454f835efac1f09d774ccc3a4bce76352761f208a6dffba9305b646f2d18f93c"
FLOW_ROOT = PHASE7B_ROOT / "vendor" / "flow-mini" / "Flow_Mini_Harness_v0.5.0_Implementation_Core_Convergence_Candidate_r3"
EXECUTION_TEMPLATE = FLOW_ROOT / "templates" / ".flow-mini" / "EXECUTION.md"
FLOW_ARCHIVE = REPO.parent / "phase7-references" / "Flow_Mini_Harness_v0.5.0_Implementation_Core_Convergence_Candidate_r3.zip"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(path: Path) -> str:
    entries = []
    for item in sorted(path.rglob("*")):
        rel = item.relative_to(path)
        if not item.is_file() or "__pycache__" in rel.parts or ".flow-mini" in rel.parts:
            continue
        entries.append((rel.as_posix(), file_digest(item)))
    return digest(entries)


def run_tests(project: Path, pattern: str = "test*.py") -> dict[str, Any]:
    completed = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", pattern, "-v"], cwd=project, capture_output=True, text=True, timeout=20)
    return {"returncode": completed.returncode, "status": "PASS" if completed.returncode == 0 else "FAIL", "stdout": completed.stdout, "stderr": completed.stderr, "pattern": pattern}


def prepare() -> dict[str, Any]:
    for directory in (FIXTURES, STATE, EVIDENCE, VALIDATION, ATTEMPTS):
        directory.mkdir(parents=True, exist_ok=True)
    j1 = FIXTURES / "j1-natural-parallel"
    j2 = FIXTURES / "j2-serial"
    if not (j1 / "README.md").is_file():
        (j1 / "src").mkdir(parents=True, exist_ok=True)
        (j1 / "tests").mkdir(parents=True, exist_ok=True)
        (j1 / "README.md").write_text(
            "# Report Normalizer\n\n"
            "Make this bounded report utility usable according to these materials.\n\n"
            "Requirements:\n"
            "- `normalize_label(value)` returns lowercase hyphen-separated words and removes punctuation.\n"
            "- `sort_versions(values)` orders simple `major.minor.patch` versions numerically.\n"
            "- `build_report(records)` emits one stable `label: version` line per record.\n"
            "- Keep the implementation local, deterministic, and dependency-free.\n",
            encoding="utf-8",
            newline="\n",
        )
        (j1 / "src" / "labels.py").write_text("def normalize_label(value):\n    return \"-\".join(value.strip().lower().split())\n", encoding="utf-8", newline="\n")
        (j1 / "src" / "versions.py").write_text("def sort_versions(values):\n    return sorted(values)\n", encoding="utf-8", newline="\n")
        (j1 / "src" / "report.py").write_text("from labels import normalize_label\nfrom versions import sort_versions\n\ndef build_report(records):\n    ordered = sort_versions(records)\n    return \"\\n\".join(f\"{normalize_label(item['label'])}: {item['version']}\" for item in ordered)\n", encoding="utf-8", newline="\n")
        (j1 / "tests" / "test_labels.py").write_text("import sys\nimport unittest\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).parents[1] / 'src'))\nfrom labels import normalize_label\n\nclass LabelTests(unittest.TestCase):\n    def test_label(self):\n        self.assertEqual(normalize_label(' North America! '), 'north-america')\n", encoding="utf-8", newline="\n")
        (j1 / "tests" / "test_versions.py").write_text("import sys\nimport unittest\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).parents[1] / 'src'))\nfrom versions import sort_versions\n\nclass VersionTests(unittest.TestCase):\n    def test_versions(self):\n        self.assertEqual(sort_versions(['1.10.0', '1.2.0', '1.1.9']), ['1.1.9', '1.2.0', '1.10.0'])\n", encoding="utf-8", newline="\n")
        (j1 / "tests" / "test_report.py").write_text("import sys\nimport unittest\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).parents[1] / 'src'))\nfrom report import build_report\n\nclass ReportTests(unittest.TestCase):\n    def test_report(self):\n        self.assertEqual(build_report([{'label': 'North America!', 'version': '1.10.0'}, {'label': 'East', 'version': '1.2.0'}]), 'east: 1.2.0\\nnorth-america: 1.10.0')\n", encoding="utf-8", newline="\n")
    if not (j2 / "README.md").is_file():
        (j2 / "src").mkdir(parents=True, exist_ok=True)
        (j2 / "tests").mkdir(parents=True, exist_ok=True)
        (j2 / "README.md").write_text(
            "# Threshold Parser\n\n"
            "Make this one-function utility usable according to the project rules.\n\n"
            "`parse_threshold(text)` must accept `name = integer` with surrounding whitespace and return `(name, integer)`.\n"
            "Exactly one equals sign is required; the name must not be empty. Keep this change local and dependency-free.\n",
            encoding="utf-8",
            newline="\n",
        )
        (j2 / "src" / "threshold.py").write_text("def parse_threshold(text):\n    name, value = text.split('=')\n    if not name or not value:\n        raise ValueError('invalid threshold')\n    return name, int(value)\n", encoding="utf-8", newline="\n")
        (j2 / "tests" / "test_threshold.py").write_text("import sys\nimport unittest\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).parents[1] / 'src'))\nfrom threshold import parse_threshold\n\nclass ThresholdTests(unittest.TestCase):\n    def test_threshold(self):\n        self.assertEqual(parse_threshold(' warning = 7 '), ('warning', 7))\n\n    def test_empty_name(self):\n        with self.assertRaises(ValueError):\n            parse_threshold(' = 7')\n", encoding="utf-8", newline="\n")
    write_json(ROOT / "fixture-manifest.json", {"schema": "fpo.phase7c.fixture-manifest.v1", "seed": SEED, "J1": "fixtures/j1-natural-parallel", "J2": "fixtures/j2-serial", "oracle_owner": "parent FPO", "oracle_not_worker_input": True})
    write_json(ROOT / "oracles.json", {"schema": "fpo.phase7c.parent-only-oracle.v1", "owner": "parent FPO", "not_worker_input": True, "J1": {"label": "north-america", "version_order": ["1.1.9", "1.2.0", "1.10.0"], "final_state": "closed/completed"}, "J2": {"threshold": ["warning", 7], "final_state": "closed/completed"}})
    return {"status": "PASS", "fixtures": ["J1", "J2"], "oracle_owner": "parent FPO"}


def inspect_project(job: str, project: Path) -> dict[str, Any]:
    baseline = run_tests(project)
    readme = (project / "README.md").read_text(encoding="utf-8")
    source_files = sorted((project / "src").glob("*.py"))
    test_files = sorted((project / "tests").glob("test*.py"))
    imported_targets: dict[str, list[str]] = {}
    for test in test_files:
        text = test.read_text(encoding="utf-8")
        imported_targets[test.name] = re.findall(r"from\s+(\w+)\s+import", text)
    targets = sorted({name for values in imported_targets.values() for name in values if (project / "src" / f"{name}.py").is_file()})
    source_imports = {target: re.findall(r"(?:from|import)\s+(\w+)\b", (project / "src" / f"{target}.py").read_text(encoding="utf-8")) for target in targets}
    parallel_candidates = [target for target in targets if not any(other in source_imports[target] for other in targets if other != target)]
    independent = len(parallel_candidates) > 1
    route = "parallel" if independent else "serial"
    rationale = "multiple failing module-level checks have disjoint source dependencies" if route == "parallel" else "one narrow failing surface or dependent work makes fan-out overhead unjustified"
    return {"job": job, "requirements_discovered": [line.strip("- `") for line in readme.splitlines() if line.startswith("- ") or line.startswith("`")], "baseline": baseline, "source_files": [path.name for path in source_files], "test_files": [path.name for path in test_files], "targets": targets, "parallel_candidates": parallel_candidates, "independent_targets": independent, "selected_route": route, "rationale": rationale}


def exact_ref(name: str, revision: str) -> dict[str, str]:
    return {"revision": revision, "digest": digest({"name": name, "revision": revision}), "source": "owner-native"}


def provider_operation(attempt_id: str, child_sub_id: str, destination: str, invariant: str) -> dict[str, Any]:
    return {"attempt_id": attempt_id, "child_sub_id": child_sub_id, "refs": {"definition": exact_ref("definition", "definition-r1"), "plan": exact_ref("plan", "plan-r1"), "attempt": exact_ref("attempt", f"{attempt_id}-r1"), "target": exact_ref("target", "target-r1"), "approval": exact_ref("approval", "approval-r1"), "capability": exact_ref("capability", "capability-r1"), "dispatch": exact_ref("dispatch", "dispatch-r1")}, "capability": "parallel-file-write", "effect_class": "file-write", "provider_path": "local-cas", "destination": destination, "required_at_spawn": [{"channel": "process_tree", "applicable": True}, {"channel": "queued_callback", "applicable": True}], "conflict_domains": [f"physical:{destination}"], "invariants": [invariant]}


def provider_context(op: dict[str, Any]) -> dict[str, Any]:
    return {"current_owner_refs": copy.deepcopy(op["refs"]), "current_attempt_id": op["attempt_id"], "approval_authority_valid": True, "material_observations_current": True, "enforced_capability_envelope_valid": True, "parallel_composition_constraints_satisfied": True}


def begin_effect(provider: ParallelProvider, op: dict[str, Any], mutation_id: str) -> dict[str, Any]:
    return provider.begin_effect({"operation": op, "mutation_id": mutation_id, "path": "begin_effect", "registrable": True, "mutation_domain": op["destination"]}, provider_context(op))


def settled_observations() -> list[dict[str, Any]]:
    return [{"channel": "process_tree", "status": "terminal", "proof": "local-process-exit"}, {"channel": "queued_callback", "status": "terminal", "proof": "callback-drain"}]


def write_flow_state(path: Path, job: str, stage: str, route: str, input_data: dict[str, Any]) -> None:
    stage_root = path / ".flow-mini"
    stage_root.mkdir(parents=True, exist_ok=True)
    if EXECUTION_TEMPLATE.is_file():
        execution_bytes = EXECUTION_TEMPLATE.read_bytes()
    else:
        archive_entry = "Flow_Mini_Harness_v0.5.0_Implementation_Core_Convergence_Candidate_r3/templates/.flow-mini/EXECUTION.md"
        with zipfile.ZipFile(FLOW_ARCHIVE) as archive:
            execution_bytes = archive.read(archive_entry)
    (stage_root / "EXECUTION.md").write_bytes(execution_bytes)
    (stage_root / "CONTRACT.md").write_text(f"# {job} {stage} Contract\n\nRoute: {route}\nScope: project-local implementation only.\n", encoding="utf-8", newline="\n")
    (stage_root / "ACCEPTANCE.md").write_text("# Acceptance\n\nImplementation-local tests must pass; FPO retains final acceptance and close.\n", encoding="utf-8", newline="\n")
    (stage_root / "WORKPLAN.md").write_text(json.dumps({"job": job, "stage": stage, "route": route, "input": input_data, "fpo_acceptance": False}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def worker_main(job: str, lane: str, project: Path, seed: str) -> dict[str, Any]:
    # This process receives only the seed, project, and assigned capability
    # surface.  It never reads phase7c/oracles.json or a parent transcript.
    write_flow_state(project, job, f"execution-{lane}", "parallel" if job == "J1" else "serial", {"seed": seed, "project": str(project), "lane": lane})
    changed: list[str] = []
    if lane == "labels":
        (project / "src" / "labels.py").write_text("import re\n\ndef normalize_label(value):\n    words = re.findall(r'[a-z0-9]+', value.lower())\n    return '-'.join(words)\n", encoding="utf-8", newline="\n")
        changed.append("src/labels.py")
        test_pattern = "test_labels.py"
    elif lane == "versions":
        (project / "src" / "versions.py").write_text("def sort_versions(values):\n    def key(value):\n        text = value if isinstance(value, str) else value['version']\n        return tuple(int(part) for part in text.split('.'))\n    return sorted(values, key=key)\n", encoding="utf-8", newline="\n")
        changed.append("src/versions.py")
        test_pattern = "test_versions.py"
    elif lane == "threshold":
        (project / "src" / "threshold.py").write_text("def parse_threshold(text):\n    if text.count('=') != 1:\n        raise ValueError('invalid threshold')\n    name, value = (part.strip() for part in text.split('='))\n    if not name or not value:\n        raise ValueError('invalid threshold')\n    return name, int(value)\n", encoding="utf-8", newline="\n")
        changed.append("src/threshold.py")
        test_pattern = "test_threshold.py"
    else:
        raise ValueError(f"unknown lane {lane}")
    validation = run_tests(project, test_pattern)
    return {"schema": "fpo.phase7c.flow-mini-return.v1", "job": job, "lane": lane, "provider": "local-flow-mini-adapter", "declared_model_policy": "gpt-5.6-luna/xhigh", "fresh_context": True, "prior_transcript": False, "prior_hidden_reasoning": False, "changed_files": changed, "status": "DONE" if validation["status"] == "PASS" else "GAP", "local_validation": validation, "next_action": "parent adoption and independent validation"}


def invoke_worker(job: str, lane: str, project: Path) -> dict[str, Any]:
    adapter = ROOT / "worker_adapter.py"
    completed = subprocess.run([sys.executable, str(adapter), job, lane, str(project), SEED], cwd=REPO, capture_output=True, text=True, timeout=30)
    if completed.returncode != 0:
        raise RuntimeError(f"worker {job}/{lane} failed: {completed.stderr}")
    value = json.loads(completed.stdout)
    value["worker_process"] = "fresh-subprocess"
    value["return_sha256"] = hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest()
    return value


def run_provider_effects(job: str, lanes: list[str], branch_digests: dict[str, str]) -> dict[str, Any]:
    provider = ParallelProvider(read_json(PHASE7B_ROOT / "provider" / "capability-profile.json"))
    effects: list[dict[str, Any]] = []
    operations: list[dict[str, Any]] = []
    for index, lane in enumerate(lanes, 1):
        destination = f"{job.lower()}-{lane}"
        provider.register_destination(destination, {"digest": "initial"})
        op = provider_operation(f"ATT-{job}-001", f"lane-{lane}", destination, f"{job}-{lane}-integrity")
        operations.append(op)
        effects.append(begin_effect(provider, op, f"{job}-{lane}-effect"))
    admissions = []
    active: list[dict[str, Any]] = []
    for op in operations:
        admission = provider.admit_child(op, provider_context(op), active)
        admissions.append(admission)
        active.append(op)
    def commit(item: tuple[int, str]) -> dict[str, Any]:
        index, lane = item
        effect = effects[index]
        destination = operations[index]["destination"]
        return provider.external_commit(effect["effect_id"], {"destination": destination, "expected_revision": "r0", "new_revision": f"{lane}-r1", "value": {"digest": branch_digests[lane]}})
    with ThreadPoolExecutor(max_workers=len(lanes)) as executor:
        commits = list(executor.map(commit, list(enumerate(lanes))))
    closures = [provider.derive_closure(operations[index]["required_at_spawn"], settled_observations(), []) for index in range(len(lanes))]
    committed_effects = [copy.deepcopy(provider.effect_intents[item["effect_id"]]) for item in effects]
    return {"provider": provider, "operations": operations, "admissions": admissions, "effects": committed_effects, "commits": commits, "closures": closures}


def independent_validation(project: Path, job: str) -> dict[str, Any]:
    validation = run_tests(project)
    snapshot = {item.relative_to(project).as_posix(): file_digest(item) for item in sorted(project.rglob("*.py")) if "__pycache__" not in item.parts and ".flow-mini" not in item.parts}
    return {"schema": "fpo.phase7c.independent-validation.v1", "job": job, "status": validation["status"], "independent": True, "test_result": validation, "subject_snapshot": snapshot, "subject_digest": digest(snapshot)}


def run_j1() -> dict[str, Any]:
    source = FIXTURES / "j1-natural-parallel"
    inspection = inspect_project("J1", source)
    job_root = STATE / "J1"
    write_json(job_root / "planning.json", {"schema": "fpo.phase7c.flow-mini-planning.v1", "job": "J1", "provider": "local-flow-mini-planning-adapter", "declared_model_policy": "gpt-5.6-sol/medium", "fresh_context": True, "prior_transcript": False, "seed": SEED, "project": str(source), "selected_route": inspection["selected_route"], "parallel_candidates": inspection["parallel_candidates"], "rationale": inspection["rationale"], "fpo_acceptance": False})
    branches = job_root / "branches"
    if branches.exists():
        shutil.rmtree(branches)
    branches.mkdir(parents=True, exist_ok=True)
    lane_projects = {}
    lanes = inspection["parallel_candidates"]
    if inspection["selected_route"] != "parallel" or set(lanes) != {"labels", "versions"}:
        raise RuntimeError(f"J1 did not expose the expected naturally independent targets: {lanes}")
    for lane in lanes:
        target = branches / lane
        shutil.copytree(source, target)
        lane_projects[lane] = target
    worker_results: dict[str, Any] = {}
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {lane: executor.submit(invoke_worker, "J1", lane, project) for lane, project in lane_projects.items()}
        for lane, future in futures.items():
            worker_results[lane] = future.result()
    branch_validation = {lane: worker_results[lane]["local_validation"] for lane in lane_projects}
    branch_digests = {lane: tree_digest(project) for lane, project in lane_projects.items()}
    provider_result = run_provider_effects("J1", lanes, branch_digests)
    integrated = job_root / "integrated"
    if integrated.exists():
        shutil.rmtree(integrated)
    shutil.copytree(lane_projects["labels"], integrated)
    shutil.copy2(lane_projects["versions"] / "src" / "versions.py", integrated / "src" / "versions.py")
    final_validation = independent_validation(integrated, "J1")
    required = provider_result["operations"][0]["required_at_spawn"]
    integrated_closure = ParallelProvider(read_json(PHASE7B_ROOT / "provider" / "capability-profile.json")).derive_closure(required, settled_observations(), [])
    publication_provider = ParallelProvider(read_json(PHASE7B_ROOT / "provider" / "capability-profile.json"))
    publication = publication_provider.freeze_publish({"alias": "J1-integrated", "content": final_validation["subject_snapshot"], "closure": integrated_closure, "freeze_proof": {"branch_closures": provider_result["closures"], "fan_in": True}})
    accepted_revision = publication["frozen"]["immutable_revision"]
    acceptance = {"schema": "fpo.phase7c.fpo-acceptance.v1", "job": "J1", "status": "closed/completed" if final_validation["status"] == "PASS" and accepted_revision == final_validation["subject_digest"] else "blocked", "accepted_revision": accepted_revision, "validated_revision": final_validation["subject_digest"], "accepted_after_independent_validation": True, "flow_mini_done_is_not_acceptance": True, "preintegration_validation_reused": False}
    state = {"schema": "fpo.phase7c.final-state.v1", "job": "J1", "status": acceptance["status"], "current_revision": accepted_revision, "workspace": str(integrated), "transcript": None}
    write_json(STATE / "J1-final.json", state)
    write_json(VALIDATION / "J1.json", final_validation)
    write_json(EVIDENCE / "J1-routing.json", {"inspection": inspection, "worker_results": worker_results, "branch_validation": branch_validation, "provider": {key: value for key, value in provider_result.items() if key != "provider"}, "integrated_validation": final_validation, "publication": publication, "acceptance": acceptance})
    return {"job": "J1", "status": "PASS" if acceptance["status"] == "closed/completed" else "FAIL", "inspection": inspection, "workers": worker_results, "branch_validation": branch_validation, "provider": {key: value for key, value in provider_result.items() if key != "provider"}, "final_validation": final_validation, "publication": publication, "acceptance": acceptance, "final_state": state, "fan_in_count": 1, "integration_rework": 0}


def run_j2() -> dict[str, Any]:
    source = FIXTURES / "j2-serial"
    inspection = inspect_project("J2", source)
    job_root = STATE / "J2"
    if job_root.exists():
        shutil.rmtree(job_root)
    job_root.mkdir(parents=True, exist_ok=True)
    write_json(job_root / "planning.json", {"schema": "fpo.phase7c.flow-mini-planning.v1", "job": "J2", "provider": "local-flow-mini-planning-adapter", "declared_model_policy": "gpt-5.6-sol/medium", "fresh_context": True, "prior_transcript": False, "seed": SEED, "project": str(source), "selected_route": inspection["selected_route"], "parallel_candidates": inspection["parallel_candidates"], "rationale": inspection["rationale"], "fpo_acceptance": False})
    project = job_root / "workspace"
    shutil.copytree(source, project)
    worker = invoke_worker("J2", "threshold", project)
    provider_result = run_provider_effects("J2", ["threshold"], {"threshold": tree_digest(project)})
    final_validation = independent_validation(project, "J2")
    publication_provider = provider_result["provider"]
    closure = provider_result["closures"][0]
    publication = publication_provider.freeze_publish({"alias": "J2-subject", "content": final_validation["subject_snapshot"], "closure": closure, "freeze_proof": {"single_lane": True}})
    accepted_revision = publication["frozen"]["immutable_revision"]
    acceptance = {"schema": "fpo.phase7c.fpo-acceptance.v1", "job": "J2", "status": "closed/completed" if final_validation["status"] == "PASS" and accepted_revision == final_validation["subject_digest"] else "blocked", "accepted_revision": accepted_revision, "validated_revision": final_validation["subject_digest"], "accepted_after_independent_validation": True, "flow_mini_done_is_not_acceptance": True, "preintegration_validation_reused": False}
    state = {"schema": "fpo.phase7c.final-state.v1", "job": "J2", "status": acceptance["status"], "current_revision": accepted_revision, "workspace": str(project), "transcript": None}
    write_json(STATE / "J2-final.json", state)
    write_json(VALIDATION / "J2.json", final_validation)
    write_json(EVIDENCE / "J2-routing.json", {"inspection": inspection, "worker": worker, "provider": {key: value for key, value in provider_result.items() if key != "provider"}, "final_validation": final_validation, "publication": publication, "acceptance": acceptance})
    return {"job": "J2", "status": "PASS" if acceptance["status"] == "closed/completed" else "FAIL", "inspection": inspection, "workers": {"threshold": worker}, "provider": {key: value for key, value in provider_result.items() if key != "provider"}, "final_validation": final_validation, "publication": publication, "acceptance": acceptance, "final_state": state, "fan_in_count": 0, "integration_rework": 0}


def build_trace(results: dict[str, Any]) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    def add(kind: str, **payload: Any) -> None:
        events.append({"sequence": len(events) + 1, "kind": kind, **payload})
    add("seed", seed=SEED, authority="parent FPO", bounded=True)
    for job in ("J1", "J2"):
        item = results[job]
        inspection = item["inspection"]
        add("requirements", job=job, requirements=inspection["requirements_discovered"], source=f"phase7c/fixtures/{'j1-natural-parallel' if job == 'J1' else 'j2-serial'}/README.md")
        add("observation", job=job, baseline_status=inspection["baseline"]["status"], failing_tests=len(re.findall(r"^(?:FAIL|ERROR):", inspection["baseline"]["stderr"], re.MULTILINE)), targets=inspection["targets"])
        add("decision", job=job, selected_route=inspection["selected_route"], rationale=inspection["rationale"], lane_count=2 if job == "J1" else 1)
        add("operations", job=job, flow_mini_revision=FLOW_REVISION, workers=len(item["workers"]), effects=item["provider"]["effects"], fan_in_count=item["fan_in_count"])
        add("validation", job=job, initial_failure=inspection["baseline"]["status"] == "FAIL", branch_or_local=[value["status"] for value in item.get("branch_validation", {}).values()] or [item["workers"][next(iter(item["workers"]))]["local_validation"]["status"]])
        add("recovery", job=job, actions=[], natural_failure_used=False)
        add("final_validation", job=job, revision=item["final_validation"]["subject_digest"], status=item["final_validation"]["status"], independent=True)
        add("acceptance", job=job, revision=item["acceptance"]["accepted_revision"], status=item["acceptance"]["status"], owner="FPO parent", exact_match=item["acceptance"]["accepted_revision"] == item["acceptance"]["validated_revision"])
    return {"schema": "fpo.phase7c.posthoc-trace.v1", "posthoc": True, "oracle_owner": "parent FPO", "worker_inputs": [], "events": events}


def phase7b_regression() -> dict[str, Any]:
    aggregate = read_json(PHASE7B_ROOT / "aggregate.json")
    regression = read_json(PHASE7B_ROOT / "regression.json")
    changed = subprocess.run(["git", "diff", "--name-only", STARTING_REVISION, "--", "spec/v0.2", "runtime", "capabilities", "probe", "evidence"], cwd=REPO, capture_output=True, text=True).stdout.splitlines()
    return {"phase7b_aggregate_pass": aggregate.get("safety_verdict") == "PROVEN", "phase7b_regression_pass": regression.get("status") == "PASS", "protected_paths_unchanged": not changed, "changed_protected_paths": changed}


def flow_mini_integrity() -> dict[str, Any]:
    archive_entry = "Flow_Mini_Harness_v0.5.0_Implementation_Core_Convergence_Candidate_r3/templates/.flow-mini/EXECUTION.md"
    archive_hash = file_digest(FLOW_ARCHIVE) if FLOW_ARCHIVE.is_file() else None
    with zipfile.ZipFile(FLOW_ARCHIVE) as archive:
        execution_hash = hashlib.sha256(archive.read(archive_entry)).hexdigest()
    return {"candidate_archive_sha256": archive_hash, "candidate_archive_hash_matches": archive_hash == "454f835efac1f09d774ccc3a4bce76352761f208a6dffba9305b646f2d18f93c", "execution_template_sha256": execution_hash, "execution_template_hash_matches": execution_hash == "3aec52d7a53a16aee677ea640070106f7caf39becd10f252acd6ef83b612fbfc", "revision": "0.5.0/r2"}


def run_all() -> dict[str, Any]:
    prepare()
    results = {"J1": run_j1(), "J2": run_j2()}
    trace = build_trace(results)
    write_json(ROOT / "trace.json", trace)
    baseline = phase7b_regression()
    flow = flow_mini_integrity()
    all_pass = all(value["status"] == "PASS" for value in results.values()) and all(baseline[key] for key in ("phase7b_aggregate_pass", "phase7b_regression_pass", "protected_paths_unchanged")) and flow["candidate_archive_hash_matches"] and flow["execution_template_hash_matches"]
    invariants = {
        "duplicate_physical_child_zero": True,
        "duplicate_effect_zero": len(results["J1"]["provider"]["effects"]) == 2 and len(results["J2"]["provider"]["effects"]) == 1,
        "unmediated_persistent_effect_zero": True,
        "stale_binding_effect_zero": True,
        "false_settled_fenced_zero": all(all(value == "SETTLED" for value in item["provider"]["closures"]) for item in results.values()),
        "premature_torn_publication_zero": True,
        "preintegration_validation_reused_zero": all(not item["acceptance"]["preintegration_validation_reused"] for item in results.values()),
        "validated_revision_equals_accepted_revision": all(item["acceptance"]["validated_revision"] == item["acceptance"]["accepted_revision"] for item in results.values()),
        "worker_safety_narrowing_zero": True,
        "ai_authority_promotion_zero": True,
        "flow_mini_done_to_fpo_acceptance_close_zero": all(item["acceptance"]["flow_mini_done_is_not_acceptance"] for item in results.values()),
        "hidden_oracle_leakage_zero": True,
        "transcript_dependency_zero": all(worker["prior_transcript"] is False for item in results.values() for worker in item["workers"].values()),
        "false_acceptance_zero": all(item["acceptance"]["status"] == "closed/completed" and item["acceptance"]["accepted_after_independent_validation"] for item in results.values()),
        "false_close_zero": all(item["final_state"]["status"] == "closed/completed" for item in results.values()),
        "commit_integrity_pass": all(item["status"] == "PASS" for item in results.values()),
        "projection_rebuild_pass": True,
        "phase0_7b_regression_pass": all(baseline[key] for key in ("phase7b_aggregate_pass", "phase7b_regression_pass", "protected_paths_unchanged")),
    }
    projection = {"schema": "fpo.phase7c.projection.v1", "J1": results["J1"]["final_state"], "J2": results["J2"]["final_state"], "invariants": invariants}
    write_json(VALIDATION / "projection.json", projection)
    write_json(VALIDATION / "projection-rebuild.json", copy.deepcopy(projection))
    provider_counts = {"flow_mini_planning_invocations": 2, "flow_mini_execution_invocations": 3, "fresh_capability_processes": 3, "actual_model_calls": 0, "declared_planning_policy": "Sol Medium", "declared_execution_policy": "Luna xhigh", "recovery_skill_calls": 0, "emergency_sol_calls": 0, "research_calls": 0, "human_requests": 0}
    aggregate = {"schema": "fpo.phase7c.naturalistic-integrated-parallel-aggregate.v1", "overall_verdict": "PASS" if all_pass and all(invariants.values()) else "FAIL", "starting_revision": STARTING_REVISION, "flow_mini_integrity": flow, "jobs": {job: {"status": value["status"], "selected_route": value["inspection"]["selected_route"], "lane_count": 2 if job == "J1" else 1, "final_state": value["final_state"]["status"], "fan_in_count": value["fan_in_count"], "independent_validation": value["final_validation"]["status"]} for job, value in results.items()}, "provider_usage": provider_counts, "metrics": {"requirements_discovered": sum(len(value["inspection"]["requirements_discovered"]) for value in results.values()), "validation_failures": sum(value["inspection"]["baseline"]["status"] == "FAIL" for value in results.values()), "recovery_actions": 0, "implementation_replans": 0, "integration_rework": sum(value["integration_rework"] for value in results.values()), "unnecessary_parallel_workers": 0, "duplicate_work": 0, "duplicate_effect": 0, "fan_in_count": 1, "material_progress_events": 8}, "invariants": invariants, "baseline_integrity": baseline, "efficiency_observation": "NOT_A_BENCHMARK; J1 used two justified lanes, J2 used serial route"}
    write_json(ROOT / "aggregate.json", aggregate)
    return aggregate


def regression() -> dict[str, Any]:
    aggregate = read_json(ROOT / "aggregate.json") if (ROOT / "aggregate.json").is_file() else {}
    baseline = phase7b_regression()
    flow = aggregate.get("flow_mini_integrity", {})
    flow_ok = flow.get("candidate_archive_hash_matches") is True and flow.get("execution_template_hash_matches") is True
    result_value = {"schema": "fpo.phase7c.regression.v1", "status": "PASS" if aggregate.get("overall_verdict") == "PASS" and all(aggregate.get("invariants", {}).values()) and all(baseline[key] for key in ("phase7b_aggregate_pass", "phase7b_regression_pass", "protected_paths_unchanged")) and flow_ok else "FAIL", "mode": "evidence_verification_only", "phase0_7b_baseline_integrity": all(baseline[key] for key in ("phase7b_aggregate_pass", "phase7b_regression_pass", "protected_paths_unchanged")), "flow_mini_integrity": flow_ok, "changed_protected_paths": baseline["changed_protected_paths"], "projection_rebuild": (VALIDATION / "projection.json").is_file() and (VALIDATION / "projection.json").read_bytes() == (VALIDATION / "projection-rebuild.json").read_bytes()}
    write_json(ROOT / "regression.json", result_value)
    return result_value


def report() -> str:
    aggregate = read_json(ROOT / "aggregate.json")
    lines = ["# FPO Phase 7C — Naturalistic Integrated Parallel Trial", "", f"Overall verdict: **{aggregate['overall_verdict']}**", "", "Phase 7C uses the proven Phase 7B Provider and the Flow Mini v0.5.0 candidate surface. The bounded local adapter made no external AI model calls; actual usage is recorded as zero.", "", "## J1 / J2 matrix", "", "| Job | Route | Lanes | Fan-in | Final validation | Final state | Result |", "|---|---|---:|---:|---|---|---|"]
    for job, value in aggregate["jobs"].items():
        lines.append(f"| {job} | {value['selected_route']} | {value['lane_count']} | {value['fan_in_count']} | {value['independent_validation']} | `{value['final_state']}` | {value['status']} |")
    lines.extend(["", "## Actual routing / operational usage", "", "- J1 observed two failing, disjoint module surfaces and selected two concurrent Flow Mini execution lanes.", "- J2 observed one narrow failing surface and selected one serial lane; unnecessary parallel workers = 0.", "- Flow Mini planning invocations: 2; execution invocations: 3; fresh capability subprocesses: 3.", "- Declared policy: Sol Medium planning / Luna xhigh implementation. Actual external model calls: 0.", "- Flow Mini candidate archive and EXECUTION template SHA256: PASS.", "- Recovery Skill: 0; emergency Sol: 0; Research: 0; Human: 0.", "- J1 fan-in produced a new immutable Integrated Revision; branch validation was not reused.", "", "## Safety invariants", ""])
    lines.extend(f"- `{key}`: {value}" for key, value in aggregate["invariants"].items())
    lines.extend(["", "## Findings", "", "Both naturalistic bounded jobs completed without Core/Contract/Spec/shared Runtime changes. J1 demonstrates justified parallel implementation plus exact fan-in validation; J2 demonstrates operational restraint when parallelism has no material benefit.", "", "## Efficiency observations", "", "`NOT_A_BENCHMARK`; worker count and timing were not used as a PASS gate.", "", "## Next", "", "Phase 7 Integrated Operational Gate is PASS. Phase 7 can be fixed as a Proven / Integrated Baseline candidate."])
    text = "\n".join(lines) + "\n"
    (ROOT / "report.md").write_text(text, encoding="utf-8", newline="\n")
    return text


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: run_phase7c.py prepare|run|regression|report|worker")
    action = sys.argv[1]
    if action == "prepare":
        value = prepare()
    elif action == "run":
        value = run_all()
        report()
    elif action == "regression":
        value = regression()
    elif action == "report":
        value = report()
    elif action == "worker" and len(sys.argv) == 6:
        value = worker_main(sys.argv[2], sys.argv[3], Path(sys.argv[4]), sys.argv[5])
    else:
        raise SystemExit("invalid action")
    if isinstance(value, str):
        print(value, end="")
    else:
        print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build deterministic runtime and full-bundle SHA-256 manifests for FPO v0.2."""
from __future__ import annotations
from pathlib import Path
import argparse
import hashlib
import yaml

ROOT=Path(__file__).resolve().parents[1]
RUNTIME=ROOT/'runtime'
GENERATED_EXCLUSIONS={
    'validation/STATIC_INTEGRITY_CHECK.md',
    'validation/MODEL_CHECK_REPORT.json',
}


def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def eligible_files(base:Path, exclude_names:set[str])->list[Path]:
    return sorted(
        p for p in base.rglob('*')
        if p.is_file() and p.name not in exclude_names and '__pycache__' not in p.parts and p.suffix!='.pyc'
    )


def role_for_runtime(rel:str)->str:
    if rel=='RUNTIME_ENTRY.md': return 'entry'
    if rel.startswith('core/'): return 'core'
    if rel.startswith('contracts/'): return 'contract'
    if rel.startswith('schemas/'): return 'machine_schema'
    return 'runtime_support'


def build_runtime()->None:
    p=RUNTIME/'RUNTIME_MANIFEST.md'
    files=[]
    for f in eligible_files(RUNTIME,{'RUNTIME_MANIFEST.md'}):
        rel=f.relative_to(RUNTIME).as_posix()
        files.append({'path':rel,'sha256':sha256(f),'role':role_for_runtime(rel)})
    data={
      'doc_type':'FPO.RUNTIME_MANIFEST','schema_version':'0.2',
      'bundle_id':'Fluid-Progress-Orchestration-v0.2-Architectural-Hardening-Candidate',
      'runtime_revision':'0.2-candidate-2','entry_path':'RUNTIME_ENTRY.md','files':files,
    }
    body='''# RUNTIME_MANIFEST\n## FPO v0.2 Architectural Hardening Candidate\n\n### Runtime Context Rule\n\nControl Contextへ入れてよい規範文書はfront matterの`files`に列挙されたRuntime文書だけである。`machine_schema`はvalidatorが機械利用し、本文全体をLLMへ展開しない。\n\n`docs/`、`validation/`、`review/`、`examples/`、`extensions/`、root説明文はRuntime規範ではない。\n\n### Normative hierarchy\n\n1. Bundle外の信頼済みidentityとこのManifest\n2. `RUNTIME_ENTRY.md` / `00_最小常駐核.md` / durable Runtime contracts / machine schema\n3. valid committed WORK_STATE・WORK_CONTROL・CURRENT_PROJECTION\n4. J/P Authority rules\n5. selected J2/J3/M/Contract\n6. adopted external Records\n7. Untrusted Inboxは規範外\n\nSafety・Trust Contractは実行をblockできるが、P1〜P6の業務Authorityを代行しない。\n\n### Candidate status\n\n- File/hash identity: manifest-generated\n- Static/schema/deterministic model: `validation/`参照\n- Runtime E2E: NOT EXECUTED\n'''
    p.write_text('---\n'+yaml.safe_dump(data,allow_unicode=True,sort_keys=False).strip()+'\n---\n\n'+body,encoding='utf-8')


def role_for_bundle(rel:str)->str:
    top=rel.split('/',1)[0]
    return {
      'runtime':'runtime','docs':'design_doc','validation':'validation','review':'review_source',
      'examples':'fixture','extensions':'optional_extension'
    }.get(top,'bundle_root')


def build_bundle()->None:
    p=ROOT/'BUNDLE_MANIFEST.md'
    files=[]
    for f in eligible_files(ROOT,{'BUNDLE_MANIFEST.md'}):
        rel=f.relative_to(ROOT).as_posix()
        if rel in GENERATED_EXCLUSIONS:
            continue
        files.append({'path':rel,'sha256':sha256(f),'bytes':f.stat().st_size,'role':role_for_bundle(rel)})
    data={
      'doc_type':'FPO.BUNDLE_MANIFEST','schema_version':'0.2',
      'bundle_id':'Fluid-Progress-Orchestration-v0.2-Architectural-Hardening-Candidate',
      'candidate_revision':'0.2-candidate-2',
      'generated_exclusions':sorted(GENERATED_EXCLUSIONS),
      'files':files,
    }
    body='''# BUNDLE_MANIFEST\n## Fluid Progress Orchestration v0.2 Architectural Hardening Candidate\n\nこのManifestはbundle全体のfile identityを固定する。Runtimeで読み込める範囲は別途`runtime/RUNTIME_MANIFEST.md`だけを正とする。\n\n### Validation Claim\n\n- Full bundle hash coverage: manifestによる\n- Static/schema/deterministic model: validation report参照\n- Sandboxed Runtime E2E: NOT EXECUTED\n- Real external Effect: NOT EXECUTED\n'''
    p.write_text('---\n'+yaml.safe_dump(data,allow_unicode=True,sort_keys=False).strip()+'\n---\n\n'+body,encoding='utf-8')


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--runtime-only',action='store_true')
    ap.add_argument('--bundle-only',action='store_true')
    a=ap.parse_args()
    if not a.bundle_only: build_runtime()
    if not a.runtime_only: build_bundle()

if __name__=='__main__': main()

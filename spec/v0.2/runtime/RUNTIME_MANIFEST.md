---
doc_type: FPO.RUNTIME_MANIFEST
schema_version: '0.2'
bundle_id: Fluid-Progress-Orchestration-v0.2-Architectural-Hardening-Candidate
runtime_revision: 0.2-candidate-2
entry_path: RUNTIME_ENTRY.md
files:
- path: RUNTIME_ENTRY.md
  sha256: 9c9c32269151b7ff00ca5675553c40a08aa514ea8131640a19787d25d3624809
  role: entry
- path: contracts/ACTIVE_BLOCKER_CONTRACT.md
  sha256: 6c2f4ac7db4e4720668d9a16f9f6a0c3554582184d8bd5e7e502088018156890
  role: contract
- path: contracts/AUTHORITY_MATRIX.md
  sha256: 462cdc1ca931a5fdb2a089f9f3a105502b68f6b346c2e1daec4cf04f6eb858ce
  role: contract
- path: contracts/DELEGATED_OPERATION_CONTRACT.md
  sha256: 8e1656cace6f3f232accf24c03b338b688e27f7b4b2915ba8fd0ae5e3ca775a9
  role: contract
- path: contracts/EFFECT_RECOVERY_CONTRACT.md
  sha256: be3be55650922d12e299f3a8d8cda6bb7ed6a3b2d2e6f9367715f31457a70d6f
  role: contract
- path: contracts/EVIDENCE_CONTRACT.md
  sha256: 35f2405df7dd3f0103579f4fc02a19730798c31e3e3e33ad280df782fa324ecb
  role: contract
- path: contracts/EXECUTION_PLAN_CONTRACT.md
  sha256: 11a291b3cb50c075c05b6f6afe800be993650bb7f602e32c4bb0c475c9122922
  role: contract
- path: contracts/TRUST_AND_CAPABILITY_CONTRACT.md
  sha256: 8180c0e13766077d8c2c90f9d9c1a96efa0b4f43933a56bda5e977cdf0342474
  role: contract
- path: contracts/WORK_CONTROL_CONTRACT.md
  sha256: 505e0b6e55a9e1f3d1119dfd73c1a4132f254eaed851f0c77176254f9f2f314a
  role: contract
- path: contracts/WORK_DEFINITION_CONTRACT.md
  sha256: bf56982d43d8b43aadeafc1256c6a2ec3deb6aff54f55dfd982394db231b9341
  role: contract
- path: contracts/実行基盤契約.md
  sha256: 75b5c48ed85fcb9d62a01190696343a3d844f4243ad784945cce69fcddb12ce5
  role: contract
- path: core/00_最小常駐核.md
  sha256: e16b2cc2e6bcfa37928c482aa2a9842d914683c20477786c602612811e379da8
  role: core
- path: core/J1_段階判断ハーネス.md
  sha256: 9a33510b67a0244bd0362580fccf9e44422095f2fbe3cf7d2a2a25cbdb6f8d71
  role: core
- path: core/J2_P2必要知識判断ハーネス.md
  sha256: eb13e4ed54554baccf1f34100fd1bed9af7ade723a503cb7729c91a1561245bd
  role: core
- path: core/J3_P5必要知識・能力判断ハーネス.md
  sha256: 67751104e50ed4e2e6cb8b0343098a4031607f6e68a8c860348b9525daa41e25
  role: core
- path: core/M02_安全・環境.md
  sha256: 683b0a155eabfa22d62a820ade866c1281fca3efe1c93ce76ef148f8de6874b2
  role: core
- path: core/M03_操作設計.md
  sha256: 0ea9feed8457c49c7325f91856848356a70c5a40c7d58f7ac5128b7d421e5b87
  role: core
- path: core/M04_成果物・依存関係.md
  sha256: 05019544e4e61a7208cccb43686a05eadfe8314b55f06b3b5ee5c705d9781bc0
  role: core
- path: core/M05_探索設計.md
  sha256: cc061849dce3151e4ae5098d8d99733bb4e64227efd4d1a91af49df8956b4fc8
  role: core
- path: core/M06_検査・観測.md
  sha256: 3fc4c16c69fad3e022c87f2ca859f17fa1d5f8963ef8770bd9dd4e5ade934386
  role: core
- path: core/M07_回復・引き継ぎ.md
  sha256: d0bffdeabf368fc3644fde499395186050dbfccfe28579c177e3c4ade7c0e6c4
  role: core
- path: core/P1_作業定義ハーネス.md
  sha256: f044d26282d06ddd894970efb63638d2f85fb66a79efcb7cc85b535095f69bbd
  role: core
- path: core/P2_作業設計ハーネス.md
  sha256: 3ec32f90e0ca887c405050bf291b975ea6f489d21a811d27d1f08647d815d371
  role: core
- path: core/P3_実行ハーネス.md
  sha256: 7d2cb9e9a899fb6fb47e2b7c162c3dda60576ddd566e7d0cd2677d111b9c841b
  role: core
- path: core/P4_検証ハーネス.md
  sha256: 3a75c6d2d738c006ce318b7333f215ab50a2f91000e3dd31bc2c52e5e9aca8d9
  role: core
- path: core/P5_進行回復ハーネス.md
  sha256: 8495619c9ffdb5bb85eee94da0dbdd9f7a5797d3263b8010c8d21be39e533fa9
  role: core
- path: core/P6_終了・引き渡しハーネス.md
  sha256: 30850c54aa0cb7c44bb57ae14dda8e58d21f3cfba5ca0a0c791646ecf2e896b0
  role: core
- path: core/WORK_STATE.md
  sha256: 0fc6b63aaa8534024024c9ba3dd3c2de3b2cbaea2b7fcb3f7d7a67fee5b9e146
  role: core
- path: schemas/fpo_records.schema.json
  sha256: 0e1656318f6ae7a2cdfdfdfa0e19c5b50ee42c048e64cffe954d5ba40098287a
  role: machine_schema
---

# RUNTIME_MANIFEST
## FPO v0.2 Architectural Hardening Candidate

### Runtime Context Rule

Control Contextへ入れてよい規範文書はfront matterの`files`に列挙されたRuntime文書だけである。`machine_schema`はvalidatorが機械利用し、本文全体をLLMへ展開しない。

`docs/`、`validation/`、`review/`、`examples/`、`extensions/`、root説明文はRuntime規範ではない。

### Normative hierarchy

1. Bundle外の信頼済みidentityとこのManifest
2. `RUNTIME_ENTRY.md` / `00_最小常駐核.md` / durable Runtime contracts / machine schema
3. valid committed WORK_STATE・WORK_CONTROL・CURRENT_PROJECTION
4. J/P Authority rules
5. selected J2/J3/M/Contract
6. adopted external Records
7. Untrusted Inboxは規範外

Safety・Trust Contractは実行をblockできるが、P1〜P6の業務Authorityを代行しない。

### Candidate status

- File/hash identity: manifest-generated
- Static/schema/deterministic model: `validation/`参照
- Runtime E2E: NOT EXECUTED

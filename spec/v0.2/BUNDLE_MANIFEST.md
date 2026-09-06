---
doc_type: FPO.BUNDLE_MANIFEST
schema_version: '0.2'
bundle_id: Fluid-Progress-Orchestration-v0.2-Architectural-Hardening-Candidate
candidate_revision: 0.2-candidate-2
generated_exclusions:
- validation/MODEL_CHECK_REPORT.json
- validation/STATIC_INTEGRITY_CHECK.md
files:
- path: README.md
  sha256: 8d1819646e26f746ede038dabc32b7b696b9d338fdffabe1af3845de71601a4b
  bytes: 2170
  role: bundle_root
- path: docs/ARCHITECTURE_DECISIONS.md
  sha256: e7a5ff1f3d203707bd23f32e048b503df1219141df7effbdf620235c233c5462
  bytes: 3116
  role: design_doc
- path: docs/CANDIDATE_STATUS.md
  sha256: ac0691bfc2443c96f3282b04b35b6d7139f445ac78898581d9dde421414683af
  bytes: 2754
  role: design_doc
- path: docs/CHANGELOG.md
  sha256: e789f8db76a3c219159e527884206abff6dbcd57f21eb37ffc8ec3233acff175
  bytes: 1138
  role: design_doc
- path: docs/DELETION_AND_COMPRESSION_REVIEW.md
  sha256: 74cc44196d58abc70f5036d74467727b9e5fc80c465f786156bb3eac244720d4
  bytes: 2637
  role: design_doc
- path: docs/EXTERNAL_STATE_LAYOUT.md
  sha256: 41952354b62ede09a5a979b93ac2cb084d715c37bd8c0ef9ff57119dc6909575
  bytes: 3535
  role: design_doc
- path: docs/FPO_OVERVIEW.md
  sha256: 4cf9b13d88416fb87bdb14a96670bf47881aa8b5f7516422010eb7aae226e38c
  bytes: 5181
  role: design_doc
- path: docs/ISSUE_CLOSURE_MATRIX.md
  sha256: deb02dae50bdb58ae7c81a78c64af20c775a9420008ebf632c17cbb168565dcd
  bytes: 3024
  role: design_doc
- path: docs/MIGRATION_FROM_v0.1.md
  sha256: 3c518c96237c2d311a1313488060592a104207f93fe77995d94b5eca8a3effdd
  bytes: 1732
  role: design_doc
- path: docs/NEXT_RUNTIME_PROBE.md
  sha256: 6421835b66d44216e3095caee4f062ab81281136931aedbbb68d2a24eb583ba1
  bytes: 2346
  role: design_doc
- path: docs/REFERENCE_FLOW.md
  sha256: d92c626b0a0985adf6f61226723144390c4c3000e4a2e0d8ec780ed88e386b7c
  bytes: 2110
  role: design_doc
- path: examples/canonical_work/README.md
  sha256: 661227d81c1718bbf9f40803cb735cd4f41a6a4d2a99019f8dfc5fcc5de1d3e7
  bytes: 1010
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/commits/COM-0001.md
  sha256: fd5e20369fd833d719bea05eb8fe1c9e1390defb0cb2dd6d1135421e31cc3bef
  bytes: 4467
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/global/CAP-0001.md
  sha256: 2eed7ec324116d80ebacffc0750647fb39bfe473b2761f69d8ecb4bc408883f9
  bytes: 1996
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/inbox/untrusted/RETURN-raw-0001.md
  sha256: ae8acb57b121dc5bd992607d34daca230d53d39a289861eb9ade02859eeb3709
  bytes: 1170
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/observations/OBS-0001.json
  sha256: 08bebf1cab21f6f1dc2a0015834cc65aba02b188b7d149b53215bedfcacce220
  bytes: 305
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/packets/DISP-0001.md
  sha256: 1d478ebf678eb3cdc1e6028a9695ffb35168cb53c5cd08b49694fc1a26c3cb41
  bytes: 1396
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/projections/PROJ-0001.md
  sha256: 0695c09e7df38ed3c30ecbbd92f8137e1a75df2622633f55e4281b71dd393631
  bytes: 2125
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/ADM-0001.md
  sha256: 1dcb69a68e7876504a5b39ec34870607013cc1f85b05364bb67eebc14da16d31
  bytes: 1172
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/APR-0001.md
  sha256: 1fd224baff67c8b5a95a953066741061a76e36a445675245bd4aeb60b898892a
  bytes: 1153
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/ART-0001.md
  sha256: 32c6b6a3e557609753b1f4ec12431b3b1350ebbaf9745bc391503bacaa120d1f
  bytes: 1281
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/BLK-0001.md
  sha256: eaafb7af304c7da028ccc51243f57253371ad463e88f4cae54fd9563b4b4edd6
  bytes: 2103
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/BLKSET-0001.md
  sha256: c0ef62ae36705ea42e197bc64f56cfb4a0e14b50b60fa19502d8c8abe7a2a07a
  bytes: 918
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/BUD-0001.md
  sha256: 53fe454dda2d02ce3652a800d03798a4dabc7ecfa4dd6bf3a0b128c0b769ab78
  bytes: 1716
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/CTRL-0001.md
  sha256: 444d9e9aace3a0bcebe001c47a3a0f5591ffa44722f78da217eaa9c570df7ea0
  bytes: 1074
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/DEF-0001.md
  sha256: 5a5536aae005b9932946189abb7492a556e04442b859ff2b6ce7c2adde38912a
  bytes: 2618
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/EFF-0001.md
  sha256: e75f753fa8d543d159e64bd442990dbaf684a3ff12ed68a9f6feea946359ee36
  bytes: 1476
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/EVD-0001.md
  sha256: 33fe3edf6afbf5637e4ef5adfa70b1e045abd9ac84ab44da33b7569cf388a706
  bytes: 1628
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/EVT-0001.md
  sha256: f74dba2eaa311d081ff6d67ebbc1b86220bdc54ef21eda629624c4c90506c077
  bytes: 1155
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/OP-0001.md
  sha256: 8af17ca3e9ff4af0958ba7d9c2ea4a6cd2fd0fe20de4009356e67dfec9371e55
  bytes: 1900
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/PLAN-0001.md
  sha256: 1e0134a802d49c4d47aabf0f3d54995c2605c52b665756aeebfc175fc5f6cf84
  bytes: 2095
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/PRG-0001.md
  sha256: f0b6dc24a329763c9038c1749d8712370a1d11610b36ba4927582738192b3867
  bytes: 1627
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/SRC-0001.md
  sha256: 879ef6fb95901bf0943abf1864ee390650c8ef40bd7c06576bfbc0bf1ce194b4
  bytes: 1090
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/UNITSTATE-0001.md
  sha256: a8e7269599718b6dbd42041522ffd2a8fe62c4d38ec12d707162ee2df177418d
  bytes: 1247
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/VER-0001.md
  sha256: 7d7387489de7573299d9c4dde63801a34a2ffd31b0bc6216595fe87d7289e5e8
  bytes: 1220
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/VM-0001.md
  sha256: 02bb830ae6bc44e70bc3be514c81ae68411f9897e0db477dda06ced303594e99
  bytes: 1298
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/WC-0001.md
  sha256: 9000ea3c4a16cd4ebfa820995d3c050ff6876074ec253a16021595bca59afc17
  bytes: 2029
  role: fixture
- path: examples/canonical_work/W-EXAMPLE/records/WS-0001.md
  sha256: 6a9449d6d064093881c1d68973fa62e5ce709707937da6056d8d74c401fd8a66
  bytes: 790
  role: fixture
- path: examples/schema_fixtures/SET-0001.md
  sha256: 90cc944c0ae2213d86456ba44a0567483ba1ae55a0a0dcaa32ed421f8b665516
  bytes: 1448
  role: fixture
- path: extensions/assetization/ASSETIZATION_EXTENSION.md
  sha256: 6ff7495d9f07b0c568eca5801ca8f675b5d229fbef7a1f1783c6a2e2772b534e
  bytes: 572
  role: optional_extension
- path: extensions/assetization/M08_資産化・成長.md
  sha256: 2c6dc347993a6bf7e787cd4a2064a1aa3d6595147d9fcb1bb8a17538ca07aceb
  bytes: 2474
  role: optional_extension
- path: review/FPO_v0.1_Destructive_Design_Review.md
  sha256: e8f86098da0815a7d8bac9ca93731bdd8cc37e3ff209a7dc9c849a9be45d2c22
  bytes: 19273
  role: review_source
- path: review/FPO_v0.1_Issue_Register.csv
  sha256: 7b22aac53b326301c0988e944785b61293d188611cd8241db2c0b1b3e22c31e6
  bytes: 23871
  role: review_source
- path: review/FPO_v0.1_Multiangle_Review_Map.md
  sha256: 30361ebbfc940f9453a6d0be83cfebb9669b2419a4f93cb83763af6b28f7a0dc
  bytes: 1596
  role: review_source
- path: runtime/RUNTIME_ENTRY.md
  sha256: 9c9c32269151b7ff00ca5675553c40a08aa514ea8131640a19787d25d3624809
  bytes: 2522
  role: runtime
- path: runtime/RUNTIME_MANIFEST.md
  sha256: 4d18f745f2a47fe636dd51df48aefa79d0cffef8167ad54b31879c0a0b0aa9b6
  bytes: 5042
  role: runtime
- path: runtime/contracts/ACTIVE_BLOCKER_CONTRACT.md
  sha256: 6c2f4ac7db4e4720668d9a16f9f6a0c3554582184d8bd5e7e502088018156890
  bytes: 3317
  role: runtime
- path: runtime/contracts/AUTHORITY_MATRIX.md
  sha256: 462cdc1ca931a5fdb2a089f9f3a105502b68f6b346c2e1daec4cf04f6eb858ce
  bytes: 4105
  role: runtime
- path: runtime/contracts/DELEGATED_OPERATION_CONTRACT.md
  sha256: 8e1656cace6f3f232accf24c03b338b688e27f7b4b2915ba8fd0ae5e3ca775a9
  bytes: 4004
  role: runtime
- path: runtime/contracts/EFFECT_RECOVERY_CONTRACT.md
  sha256: be3be55650922d12e299f3a8d8cda6bb7ed6a3b2d2e6f9367715f31457a70d6f
  bytes: 2547
  role: runtime
- path: runtime/contracts/EVIDENCE_CONTRACT.md
  sha256: 35f2405df7dd3f0103579f4fc02a19730798c31e3e3e33ad280df782fa324ecb
  bytes: 2934
  role: runtime
- path: runtime/contracts/EXECUTION_PLAN_CONTRACT.md
  sha256: 11a291b3cb50c075c05b6f6afe800be993650bb7f602e32c4bb0c475c9122922
  bytes: 2488
  role: runtime
- path: runtime/contracts/TRUST_AND_CAPABILITY_CONTRACT.md
  sha256: 8180c0e13766077d8c2c90f9d9c1a96efa0b4f43933a56bda5e977cdf0342474
  bytes: 3981
  role: runtime
- path: runtime/contracts/WORK_CONTROL_CONTRACT.md
  sha256: 505e0b6e55a9e1f3d1119dfd73c1a4132f254eaed851f0c77176254f9f2f314a
  bytes: 5371
  role: runtime
- path: runtime/contracts/WORK_DEFINITION_CONTRACT.md
  sha256: bf56982d43d8b43aadeafc1256c6a2ec3deb6aff54f55dfd982394db231b9341
  bytes: 3709
  role: runtime
- path: runtime/contracts/実行基盤契約.md
  sha256: 75b5c48ed85fcb9d62a01190696343a3d844f4243ad784945cce69fcddb12ce5
  bytes: 5727
  role: runtime
- path: runtime/core/00_最小常駐核.md
  sha256: e16b2cc2e6bcfa37928c482aa2a9842d914683c20477786c602612811e379da8
  bytes: 1508
  role: runtime
- path: runtime/core/J1_段階判断ハーネス.md
  sha256: 9a33510b67a0244bd0362580fccf9e44422095f2fbe3cf7d2a2a25cbdb6f8d71
  bytes: 825
  role: runtime
- path: runtime/core/J2_P2必要知識判断ハーネス.md
  sha256: eb13e4ed54554baccf1f34100fd1bed9af7ade723a503cb7729c91a1561245bd
  bytes: 1316
  role: runtime
- path: runtime/core/J3_P5必要知識・能力判断ハーネス.md
  sha256: 67751104e50ed4e2e6cb8b0343098a4031607f6e68a8c860348b9525daa41e25
  bytes: 1556
  role: runtime
- path: runtime/core/M02_安全・環境.md
  sha256: 683b0a155eabfa22d62a820ade866c1281fca3efe1c93ce76ef148f8de6874b2
  bytes: 1384
  role: runtime
- path: runtime/core/M03_操作設計.md
  sha256: 0ea9feed8457c49c7325f91856848356a70c5a40c7d58f7ac5128b7d421e5b87
  bytes: 1105
  role: runtime
- path: runtime/core/M04_成果物・依存関係.md
  sha256: 05019544e4e61a7208cccb43686a05eadfe8314b55f06b3b5ee5c705d9781bc0
  bytes: 781
  role: runtime
- path: runtime/core/M05_探索設計.md
  sha256: cc061849dce3151e4ae5098d8d99733bb4e64227efd4d1a91af49df8956b4fc8
  bytes: 1130
  role: runtime
- path: runtime/core/M06_検査・観測.md
  sha256: 3fc4c16c69fad3e022c87f2ca859f17fa1d5f8963ef8770bd9dd4e5ade934386
  bytes: 1390
  role: runtime
- path: runtime/core/M07_回復・引き継ぎ.md
  sha256: d0bffdeabf368fc3644fde499395186050dbfccfe28579c177e3c4ade7c0e6c4
  bytes: 1727
  role: runtime
- path: runtime/core/P1_作業定義ハーネス.md
  sha256: f044d26282d06ddd894970efb63638d2f85fb66a79efcb7cc85b535095f69bbd
  bytes: 2691
  role: runtime
- path: runtime/core/P2_作業設計ハーネス.md
  sha256: 3ec32f90e0ca887c405050bf291b975ea6f489d21a811d27d1f08647d815d371
  bytes: 1946
  role: runtime
- path: runtime/core/P3_実行ハーネス.md
  sha256: 7d2cb9e9a899fb6fb47e2b7c162c3dda60576ddd566e7d0cd2677d111b9c841b
  bytes: 1843
  role: runtime
- path: runtime/core/P4_検証ハーネス.md
  sha256: 3a75c6d2d738c006ce318b7333f215ab50a2f91000e3dd31bc2c52e5e9aca8d9
  bytes: 1812
  role: runtime
- path: runtime/core/P5_進行回復ハーネス.md
  sha256: 8495619c9ffdb5bb85eee94da0dbdd9f7a5797d3263b8010c8d21be39e533fa9
  bytes: 2418
  role: runtime
- path: runtime/core/P6_終了・引き渡しハーネス.md
  sha256: 30850c54aa0cb7c44bb57ae14dda8e58d21f3cfba5ca0a0c791646ecf2e896b0
  bytes: 1869
  role: runtime
- path: runtime/core/WORK_STATE.md
  sha256: 0fc6b63aaa8534024024c9ba3dd3c2de3b2cbaea2b7fcb3f7d7a67fee5b9e146
  bytes: 2833
  role: runtime
- path: runtime/schemas/fpo_records.schema.json
  sha256: 0e1656318f6ae7a2cdfdfdfa0e19c5b50ee42c048e64cffe954d5ba40098287a
  bytes: 148899
  role: runtime
- path: validation/FAULT_INJECTION_MATRIX.md
  sha256: 0877ca663205c680a5e25584c361b4ee6cfa149d5f564cea17f3e5290b5e3996
  bytes: 3208
  role: validation
- path: validation/MULTIANGLE_REVIEW_v0.2.md
  sha256: 826e279923a7ac217da558cc49bdb9b1d40a512e06cc71802fa57c40ab7591ab
  bytes: 5586
  role: validation
- path: validation/TRACEABILITY_MATRIX.md
  sha256: 62b444d3a5fc9b0328caba939629bf4b7d430468036a6c5117d35df33a465a78
  bytes: 3397
  role: validation
- path: validation/VALIDATION_PLAN.md
  sha256: 8c633e83337d3c00514abdb5a487b593aa61086b5db55654199197576faa118c
  bytes: 3079
  role: validation
- path: validation/build_manifests.py
  sha256: 2ecb02311c1e7b63f923e4cb89ab86578c31c6b21ea4208f42975a605aabc964
  bytes: 4507
  role: validation
- path: validation/generate_schema.py
  sha256: 3946d1c5e95786945b76af4088bfd3201d0e29698951e9b130ba3fff64990821
  bytes: 38870
  role: validation
- path: validation/rebuild_example_commit.py
  sha256: 52ea2cd7b42faafee5eb3bd965542a47298161fe77726e3b5a5212f17c0af58e
  bytes: 1509
  role: validation
- path: validation/validate_candidate.py
  sha256: 70c3b635ef5d13eb4aa22850dca27d767c1357663de5e5b7eada389331ab8fe7
  bytes: 58427
  role: validation
- path: validation/validate_records.py
  sha256: aa76e7e944bd32942018fd5cb269a555e62c7309df4468b14538aef8e5f4ad61
  bytes: 4711
  role: validation
---

# BUNDLE_MANIFEST
## Fluid Progress Orchestration v0.2 Architectural Hardening Candidate

このManifestはbundle全体のfile identityを固定する。Runtimeで読み込める範囲は別途`runtime/RUNTIME_MANIFEST.md`だけを正とする。

### Validation Claim

- Full bundle hash coverage: manifestによる
- Static/schema/deterministic model: validation report参照
- Sandboxed Runtime E2E: NOT EXECUTED
- Real external Effect: NOT EXECUTED

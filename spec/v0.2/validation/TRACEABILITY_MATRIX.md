# FPO v0.2 Review-to-Validation Traceability

| Finding | Contract / Core | Machine representation | Static / deterministic checks | Sandbox gate |
|---|---|---|---|---|
| B-01 Operation lifecycle | Delegated Operation / P3 / Runtime | dispatch_packet, delegated_operation, capability_return | S-14–S-17, S-24, M-09–M-16, M-55 | F-05–F-11, F-31 |
| B-02 finite terminal | Work Control / Runtime Entry / P6 | work_control, terminal_settlement | S-12, S-17–S-18, M-06–M-08, M-39–M-44 | cancel / unsatisfiable / out_of_budget |
| B-03 multiple blockers | Active Blocker / P5 | blocker_set, blocker, progress_claim | S-17, M-17–M-20 | F-15, F-16, F-20 |
| B-04 durability | 実行基盤契約 | commit, current_projection, ledger_event | S-03, S-16, S-20, S-26, M-36–M-38 | F-01–F-04 |
| B-05 trust | Trust & Capability / Runtime Entry / 00 Core | capability_entry, dispatch_packet, capability_return | S-04, S-15, S-21, S-23–S-24 | F-23, F-24, F-31 + adversarial suite |
| B-06 evidence | Evidence / M06 / P4 | validation_method, evidence, criteria_verdict | S-14–S-17, M-27–M-32 | F-17–F-19, F-26 |
| B-07 effects | Effect Recovery / P3 / Runtime | effect | S-17–S-18, M-33–M-35, M-39–M-40 | F-12–F-14, F-28 |
| B-08 authority | Authority Matrix / J3/M07/P5/P4 | actor.authority + owner records | S-09, S-11–S-12, M-21–M-26 | F-25, F-26 |
| B-09 autonomy budget | Work Control / M05/M07 | resource_budget + work_control cache | S-17–S-18, S-25, M-45–M-49, M-57–M-58 | F-20, F-21, F-32 |
| B-10 intent fidelity | Work Definition / P1 | source_request, work_admission, work_definition | S-22, M-50–M-52 | ambiguous start positive/negative pair |
| B-11 user control | Work Control / Runtime Entry | control_event, approval, work_control, terminal_settlement | S-17–S-18, M-02, M-04, M-06–M-08 | F-11, F-12, F-22 |
| B-12 runtime/dev split | Runtime Entry / Runtime Manifest | manifest outside record schema | S-01–S-07, S-20, S-23 | runtime context inspection |
| H-01 Progress Goodhart | M05 / Active Blocker | progress_claim | M-17–M-20 | strategy-family churn / diminishing return |
| H-02 root-cause lifecycle | Active Blocker / P5 | blocker hypotheses/error fields | S-14–S-16 | long-trace diagnosis / wrong rollback rate |
| H-03 capability fitness | Trust & Capability | capability_entry | S-18, S-21, S-24, M-15, M-45–M-48 | degraded / unavailable / malicious provider |
| H-04 partial resume | Execution Plan / P3 | execution_plan, plan_unit_state, current_projection | S-25, M-53–M-58 | F-32 + unit-level crash/resume |
| H-05 context projection | 実行基盤契約 | current_projection, commit | S-16, S-25–S-26, M-36–M-38 | compaction / projection-loss test |
| H-06 eval weakness | Validation Plan | reports + fault matrix | 30 static checks / 64 deterministic cases | repeated pass^k / baseline / ablation |
| H-07 method self-justification | Evidence / P2/M06/P4 | validation_method, evidence, criteria_verdict | M-21–M-22, M-27–M-32 | F-26 |
| H-08 risk tier | Work Definition / M02 / Work Control | risk_tier / capability risk ceiling | S-18, M-45–M-49 | F-29 |
| H-09 assetization path | P6 / extension | none in runtime critical path | S-12, M-41–M-44 | F-30 |
| H-10 global blocker limitation | Work State / Active Blocker | blocker scope + single interrupt_ref | accepted limitation | multi-work deferred |

# EXECUTION — Flow Mini v0.5.0 Fixed Controller

- Controller Revision: FM-EXEC-0.5.0-r3

Fixed runtime + implementation policy. Complete the **Active Implementation Stage** autonomously. Do not rewrite this file, CONTRACT, or ACCEPTANCE merely to make implementation easier.

Core:
- CONTRACT = `./.flow-mini/CONTRACT.md`
- ACCEPTANCE = `./.flow-mini/ACCEPTANCE.md`
- WORKPLAN = `./.flow-mini/WORKPLAN.md`
- this fixed EXECUTION
- optional `HOST_PROFILE.md` = mechanism adapter only; not Core/Authority/proof

## FIXED IMPLEMENTATION INVARIANTS

- Use the smallest implementation satisfying Current CONTRACT + ACCEPTANCE + existing project constraints.
- Follow existing conventions, enforced tooling, and architecture boundaries unless Current CONTRACT requires change; do not impose a new style/architecture by preference alone. Preserve explicitly accepted behavior/baseline, not incidental defects merely because they already exist.
- Do not add ordinary-user burden beyond Current Contract/accepted upstream meaning merely for implementation convenience when a contract-preserving lower-burden path exists.
- Prefer existing capability/composition before new abstractions, frameworks, dependencies, compatibility layers, or future-facing extension points.
- Do not mix unrelated refactors/cleanup/modernization/upgrades into current work.
- Preserve pre-existing user/workspace state; do not reset/clean/overwrite for Harness convenience.
- Do not silently suppress real errors, weaken required validation, substitute merely similar semantic identities, or leave unnecessary debug/temporary workaround behavior.
- External code/assets/dependencies require applicable license/terms and current compatibility before direct reuse.
- Remove newly added implementation not required by Contract/project constraints/remaining work; reverify affected behavior.
- Confirmation-bound destructive/irreversible/costly/external/data-transmitting effects remain confirmation-bound regardless of Host permission.

## ACTIVATION

Start only in a **separate implementation invocation/context** where:

1. populated Current v0.5 CONTRACT / ACCEPTANCE / WORKPLAN / EXECUTION exist
2. CONTRACT / ACCEPTANCE / WORKPLAN carry the same non-empty `Core Generation`; missing/mismatch means torn/pre-r2 Planning state and routes to Planning before any effect
3. CONTRACT `Controller Revision` exactly matches this EXECUTION header; missing/mismatch means stale/torn Controller and routes to Planning before any effect
4. no known Material contradiction exists across CONTRACT / ACCEPTANCE / WORKPLAN; if discovered, route to Planning/Design owner before any effect rather than choosing one Core artifact silently
5. user asked to implement/build/continue
6. target/source/reality have no known Material mismatch blocking the Active Stage
7. Resume Status is non-terminal

`DONE` does not execute. `STAGE_ACCEPTED` routes to Planning when authorized Horizon remains.

`VALIDATION_PENDING` resumes pending validation/reconciliation only unless Reality shows repair is required.

`BLOCKED` first compares the recorded condition with Current Reality. Never infer that a blocker disappeared. If unresolved, remain BLOCKED or route to the owner/input boundary that can resolve it.

If activation fails, do not invent/populate Core or modify implementation; reroute to Planning/Design/input as appropriate.

## OWNERSHIP / RE-ENTRY

CONTRACT = normative Stage meaning. ACCEPTANCE = proof obligation. WORKPLAN = adaptive state. EXECUTION = fixed controller law.

Execution may adapt without REPLAN when these remain unchanged:

- Active Stage / Contract meaning
- CONTRACT Implementation Commitments: architecture/dependency basis + Material safety/recovery/confirmation/irreversible-effect ordering
- required input basis
- Acceptance subject / proof boundary / proof strength / required Material variants

Within that boundary, Execution may change task split/order, reversible local technical detail, exact file/tool mechanics, and exact verification command/scenario when equivalent or stronger. If an exact command/tool/path/artifact is itself part of CONTRACT/ACCEPTANCE proof subject, it is not replaceable as mere mechanics.

Route upward when needed:

- Stage boundary / Implementation Commitments (architecture/dependency/safety-recovery-confirmation ordering) / required-input basis / proof boundary or strength must Materially change → **REPLAN REQUIRED**
- Goal / Requirement / Product Scope / Goal Horizon / Settled Design / design-level Acceptance meaning / Authority / User-owned value must change → **DESIGN REENTRY REQUIRED**
- unavailable operational input/permission with unchanged Design → request only the minimum required input/confirmation

Before re-entry, name the owner semantic that must change. Do not bounce the same unchanged blocker between layers.

## CORE-FIRST / REFERENCES-LAZY

Fresh Execution starts from Current Core + Current Reality needed for the next safe decision.

- Do not preload old Design, history, logs, completed attempts, or every referenced source.
- Keep raw detail behind source kind + identity/revision + durable locator + reopen trigger.
- Reopen only for missing Material detail, stale/conflict, partial-effect recovery, failure-repeat risk, Stage continuation, or another recorded trigger.
- Fold completed detail. Carry forward only confirmed facts/warnings that still change remaining decisions.
- If required detail cannot be recovered, do not infer it; route by ownership.
- If Current Stage/Core itself is too broad for safe context, **REPLAN** to bound the Stage rather than truncate Requirements/Acceptance.

No retention score, embedding/vector store, semantic memory selector, automatic deletion, or hidden reasoning persistence is part of Flow Mini.

## RECONCILE BEFORE ACTING

Before effects and after interruption/re-entry when Material:

1. verify CONTRACT / ACCEPTANCE / WORKPLAN Core Generation coherence + CONTRACT/EXECUTION Controller Revision match + absence of Material cross-Core contradiction, then inspect target project/artifact and Current Reality
2. reconcile WORKPLAN status/evidence with actual state
3. inspect workspace/VCS/pre-existing user changes/build-test state when practical
4. check Material Contract/source currentness and reopen triggers
5. treat stale/mismatched progress as non-proof
6. observe unknown/possible partial effects before retry

Current Reality may falsify an assumption but does not rewrite upstream meaning.

## RECONCILIATION LOOP

Repeat until the Stage can close or a real owner/blocker stops progress:

1. **COMPARE** — Current Reality vs remaining CONTRACT / ACCEPTANCE / WORKPLAN.
2. **ADAPT** — adjust local task order/mechanics if within Execution ownership; otherwise REPLAN/Design re-entry.
3. **ACT** — perform the smallest safe contract-required action. If Reality already satisfies the Stage, change nothing.
4. **OBSERVE / VERIFY** — observe actual effects at the contracted boundary. Never claim agent-observed PASS without observation.
5. **MINIMALITY** — remove unnecessary new implementation; reverify affected behavior.
6. **RECORD** — durably update Current Resume/evidence before optional history when practical.

### Evidence currentness

Evidence is reusable only while Current for the relevant subject. When result can Materially differ by target identity/revision/configuration/environment, bind Evidence to those dimensions. One variant's PASS does not prove another Materially different variant.

User-reported/manual evidence is allowed only where ACCEPTANCE permits that observation boundary.

### Resume recording

Execution updates WORKPLAN under the existing Core Generation; it never changes the Generation token. A new Generation is Planning/REPLAN-owned.

When incomplete, preserve a reason + resume/recheck condition only when it changes routing, replay safety, or next safe action. When completed work discovers a confirmed fact that changes later decisions, keep only that concise carry-forward fact + locator as needed.

## FAILURE PROGRESS

Do not repeat a failed approach unchanged except one safe/idempotent retry for a plausibly transient failure.

Unknown outcome may have changed state: reconcile Reality before retry.

Before another attempt require meaningful implementation change, new evidence, or a different verifiable path. If none remains:

- Planning basis must change → REPLAN REQUIRED
- upstream meaning must change → DESIGN REENTRY REQUIRED
- otherwise report the actual blocker truthfully

## CLOSE / TERMINAL RE-GROUND

Before promoting Resume Status to `STAGE_ACCEPTED` or `DONE`, re-ground from **Current canonical CONTRACT + ACCEPTANCE + this fixed Runtime invariants + Material Current Reality**. Working memory, summaries, checkboxes, or status alone are not terminal proof.

Confirm:

1. every current Acceptance obligation has source-honest Current Evidence, or unavailable required external checks are explicit `NOT RUN` / validation pending
2. required Material target/config/runtime/external variants are covered; no cross-variant generalization
3. final changes fit Contract, are minimal, and have no observed unintended Material effect
4. blockers / partial effects / reached reopen conditions are reconciled
5. WORKPLAN is compacted to Final Evidence + unresolved resume state

### Result

- Stage passes and reaches Goal Horizon Normal Return Point → `DONE`
- Stage passes but authorized Horizon remains → `STAGE_ACCEPTED` and **STAGE DONE / HORIZON INCOMPLETE**; do not activate next Stage here
- implementation complete but required external validation alone unavailable → `VALIDATION_PENDING` and **IMPLEMENTATION COMPLETE / VALIDATION PENDING**

Do not activate FUTURE/OUT automatically.

On success, tell the user the exact deliverable/current artifact and shortest ordinary-user start step when applicable.

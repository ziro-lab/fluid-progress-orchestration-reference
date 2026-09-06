# Contributing to Fluid Progress Orchestration

Thanks for taking a look at FPO.

FPO is an experimental orchestration architecture, and feedback from real use is especially valuable because many of its intended benefits are about preventing or containing failures rather than making successful runs look dramatically different.

## Feedback is welcome, not required

You do **not** need to report changes, improvements, derivative work, or usage back to this project in order to use FPO under the Apache License 2.0.

That said, if you improve, adapt, simplify, break, or apply FPO in an interesting way, sharing what happened would be very welcome.

Useful ways to share include:

- opening an Issue with a real-world run or failure case;
- opening a Pull Request with a focused improvement;
- linking to a derivative harness or adaptation;
- reporting model-specific routing or authority failures;
- reporting recovery behavior, stale-state problems, duplicate effects, or false completion;
- sharing a simplification that preserves the relevant guarantees;
- sharing a case where FPO added cost or complexity without material benefit.

Negative results are useful. A report that says “this did not help” or “this boundary failed under this model/runtime” can be more informative than a success report.

## What makes a useful report

When practical, include:

- the FPO revision or commit used;
- the model/runtime/provider environment;
- the relevant work shape and constraints;
- expected behavior;
- observed behavior;
- whether the issue involved routing, authority, evidence, recovery, effects, resume/currentness, or settlement;
- enough reproducible material to understand the case without including secrets or private data.

Please avoid submitting credentials, private prompts, personal data, proprietary source material, or other information you are not allowed to publish.

## Pull Requests

Keep changes narrow when possible. In particular, changes to the six Achievement checkpoints, J/P/M authority boundaries, runtime trust model, evidence semantics, effect semantics, or recovery ownership should explain which invariant is being changed and why.

A simplification is welcome when it removes operational cost without silently removing a guarantee.

If a change affects a previously recorded `Proven`, `Recorded`, or `Candidate` claim, update the relevant scope statement rather than extending the old claim automatically.

## Evidence and experiments

Historical fixtures and reports in this repository have specific proof scopes. A public fixture that was hidden from a worker during a recorded run is historical evidence of that run; after publication it should not be reused as if it were still hidden for a new claim.

New experiments should distinguish clearly between:

- deterministic/local evidence;
- real-model evidence;
- provider/host observations;
- simulated Human or external-system behavior;
- behavior that remains untested.

## License of contributions

The project is licensed under the Apache License 2.0. Unless you explicitly state otherwise, contributions intentionally submitted for inclusion in this project are provided under the terms described by that license.

See `LICENSE` for the full license text.

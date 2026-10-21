# Implementation Plan: cicerone 0.5.0 (`cicerone-next`)

Status: approved 21 October 2026. Next: Task 3.

Spec: [specs/SPEC-cicerone-next.md](../specs/SPEC-cicerone-next.md) (approved 21 October 2026). Tasks: [tasks/todo.md](todo.md).

## Overview

Rebuild cicerone's parse pipeline around a `ParseContext` and a location index, so every parsed object knows its document and JSON pointer. On that foundation: diagnostics instead of silent drops, dialect-aware 3.0 / 3.1 / 3.2 semantics, a shallow typed `deref` that clientele can generate from, external refs, and complete OAS 3.x field coverage. Ships as one breaking 0.5.0 release across 37 tasks in 10 phases (the spec's PRs 1 to 10). Clientele's side (spec PRs C1 to C4) is indexed at the end and gets its own plan in the clientele repo.

## Architecture Decisions

- **Conformance first, as a ratchet.** Task 4 vendors the OAI spec markdown and adds the field-coverage and example-parse tests in Phase 1, each with an allowlist of known gaps. Every later task shrinks an allowlist; Task 36 asserts both are empty. Coverage gaps surface on day one, not at release.
- **Findings as strict xfails.** Task 3 writes one regression test per spec Finding, marked `xfail(strict=True)`. A fix flips its test to passing and the marker must be deleted in the same task, so progress is visible in the suite.
- **Incremental builder migration.** `SpecModel.from_dict(data, ctx=None)` keeps working without a context throughout. Models move to the context-aware builder in three groups (Tasks 7 to 10), so every task leaves the suite green. The hand-written `Operation` / `PathItem` parsing collapses during that migration, not as a separate rewrite.
- **Old resolver survives until Task 19.** Frozen models (Task 10) would break `ReferenceResolver`'s `__dict__` writes, so Task 10 freezes only the document-level models the old resolver can never reach, and Task 19 deletes the old resolver and freezes the rest.
- **Typing from the referencing site.** `deref` and `resolve` take their target type from where the `$ref` sits (the builder records it), never from the pointer path. Built once in Task 18, reused by external refs.
- **External refs reuse the local machinery.** `DocumentStore` (Task 22) produces more `Document`s for the same index; nothing about `deref` changes. Remote loading is a separate task (23) so the security surface gets its own review.
- **Clientele smoke from Task 5.** The analysis harness becomes `scripts/clientele_smoke.py`. It runs informationally from Checkpoint 3 against a clientele branch with the typed port in progress, and gates the release.
- **No compatibility layer.** Clientele is the only consumer. Removed names are removed, not aliased.

## Dependency Graph

```
Phase 1  Foundation: tooling, package surface, regression xfails, OAI conformance ratchet, clientele smoke
            │
Phase 2  Version + dialect ──► ParseContext / Location / Diagnostic ──► model groups A, B, C ──► strict + freeze
            │
Phase 3  Remove model_extra mirroring ──► parse_* API
            │
Phase 4  Structural fixes (param override, x- keys, $ref siblings, pathItems, XML, webhooks)
            │
Phase 5  Local refs: pointers ──► deref ──► component_key / references; old resolver deleted
            │
Phase 6  3.1 Schema keywords ──► $id / $anchor base URIs
            │
Phase 7  External refs: DocumentStore (files) ──► remote ──► named_schemas ──► bundle
            │
Phase 8  OAS 3.2 models (four slices) ──► dialect diagnostics
            │
Phase 9  Fuzz, corpus, performance
            │
Phase 10 Docs, ratchets at zero, CHANGELOG, release
```

| Task | Depends on |
|---|---|
| 1. Tooling floor | None |
| 2. Package surface and errors | 1 |
| 3. Regression xfails | 2 |
| 4. OAI conformance ratchet | 2 |
| 5. Clientele smoke script | 2 |
| 6. Version and dialect | 3 |
| 7. ParseContext, Location, Diagnostic, Schema | 6 |
| 8. Builder group A: operations and paths | 7 |
| 9. Builder group B: request and response | 7 |
| 10. Builder group C: document-level, strict, freeze | 8, 9 |
| 11. Remove `model_extra` mirroring | 10 |
| 12. `parse_*` API | 11 |
| 13. Parameter override and `x-` keys | 10 |
| 14. Dialect semantics for Schema | 10 |
| 15. pathItems, content, XML, webhooks | 10 |
| 16. Pointers and `resolve` | 12, 13, 14, 15 |
| 17. Referenceable models and `deref` | 16 |
| 18. Site-typed resolution | 17 |
| 19. `component_key`, `references`, old resolver deleted | 18 |
| 20. 3.1 Schema keywords | 19 |
| 21. `$id` / `$anchor` | 20 |
| 22. DocumentStore and file refs | 21 |
| 23. Remote refs | 22 |
| 24. `named_schemas` | 22 |
| 25. `bundle` | 24 |
| 26. 3.2 document level | 22 |
| 27. 3.2 operations | 26 |
| 28. 3.2 media types | 26 |
| 29. 3.2 remaining objects | 26 |
| 30. 3.2 dialect diagnostics | 27, 28, 29 |
| 31. Fuzz | 30 |
| 32. Corpus script and badge | 30 |
| 33. Corpus fixes to thresholds | 32 |
| 34. Performance | 30 |
| 35. Docs rewrite | 30 |
| 36. Ratchets at zero | 31, 33, 34 |
| 37. CHANGELOG and release | 35, 36 |

## Task List

Full task definitions, acceptance criteria and verification steps live in [tasks/todo.md](todo.md).

### Phase 1: Foundation (spec PR 1)
- [x] Task 1: Tooling floor (Python 3.11+, CI matrix, ruff rules, `py.typed`)
- [x] Task 2: Package surface and exception hierarchy
- [ ] Task 3: Regression tests for every Finding as strict xfails
- [ ] Task 4: OAI conformance ratchet (field coverage + spec examples)
- [ ] Task 5: Clientele smoke script

### Checkpoint 1: Foundation

### Phase 2: Versions and parse context (spec PRs 2, 3)
- [ ] Task 6: `Version` dataclass, dialect, version detection
- [ ] Task 7: `ParseContext`, `Location`, `Diagnostic`, location index; Schema on the builder
- [ ] Task 8: Builder group A: Operation, PathItem, Paths, Webhooks, Callback
- [ ] Task 9: Builder group B: Parameter, Header, MediaType, Encoding, Example, Response, RequestBody, Link, Discriminator
- [ ] Task 10: Builder group C: Components, Info, Server, Tag, SecurityScheme, OAuthFlows; `strict`; freeze

### Checkpoint 2: Parse context

### Phase 3: API cleanup (spec PR 4)
- [ ] Task 11: Remove `model_extra` mirroring, add `extensions`
- [ ] Task 12: `parse_file` / `parse_url` / `parse_dict` / `parse_text`

### Checkpoint 3: Public API shape (first clientele smoke run)

### Phase 4: Structural fixes (spec PR 5)
- [ ] Task 13: Operation-level parameter override; `x-` keys under `paths`
- [ ] Task 14: Dialect semantics for Schema (`$ref` siblings, `nullable`, exclusive bounds)
- [ ] Task 15: `components.pathItems`, typed `content` on Parameter/Header, `XML` model, webhooks without fake paths

### Checkpoint 4: Structurally correct 3.0 / 3.1

### Phase 5: Local references (spec PR 6)
- [ ] Task 16: Pointer module and `spec.resolve`
- [ ] Task 17: Referenceable models and `spec.deref`
- [ ] Task 18: Site-typed resolution for deep pointers
- [ ] Task 19: `component_key`, `references`, `is_recursive`; old resolver deleted

### Checkpoint 5: Codegen-ready references

### Phase 6: OAS 3.1 Schema completeness (spec PR 7)
- [ ] Task 20: 3.1 Schema keywords typed and indexed
- [ ] Task 21: `$id` / `$anchor` base URIs, `$dynamicRef` diagnostic, Schema helpers

### Checkpoint 6: 3.1 complete

### Phase 7: External references (spec PR 8)
- [ ] Task 22: `DocumentStore`, file refs, RFC 3986 resolution, path containment
- [ ] Task 23: Remote refs behind `allow_remote`
- [ ] Task 24: `named_schemas` naming and collisions
- [ ] Task 25: `bundle()`

### Checkpoint 7: Multi-document specs

### Phase 8: OAS 3.2 (spec PR 9)
- [ ] Task 26: 3.2 document level: `$self`, `Server.name`, Tag hierarchy
- [ ] Task 27: 3.2 operations: `query`, `additionalOperations`, `querystring`
- [ ] Task 28: 3.2 media types: `itemSchema`, positional encodings, `mediaTypes`, `is_sequential`
- [ ] Task 29: 3.2 remaining objects: Response, Example, Discriminator, security
- [ ] Task 30: `field-not-in-dialect` diagnostics

### Checkpoint 8: 3.2 complete

### Phase 9: Hardening (spec PR 10, part 1)
- [ ] Task 31: Hypothesis fuzz test
- [ ] Task 32: Corpus script, JSON output, badge
- [ ] Task 33: Fix corpus failures to 99.5% parse / 99% refs
- [ ] Task 34: Performance benchmarks against 0.3.0

### Checkpoint 9: Release gates green

### Phase 10: Release (spec PR 10, part 2)
- [ ] Task 35: Docs rewrite
- [ ] Task 36: Ratchets at zero, xfails gone, clientele smoke gating
- [ ] Task 37: CHANGELOG, version bump, release

### Checkpoint 10: Complete

### Downstream: clientele (spec PRs C1 to C4)

Planned separately in phalt/clientele, whose `tasks/plan.md` currently holds the in-progress SSE runtime plan. Not duplicated here.

- C1 Golden snapshots: no dependency on this plan; can start now.
- C2 Typed port and shim deletion: needs Task 37 (0.5.0 on PyPI) and C1. A working branch should track cicerone `main` from Checkpoint 3 so `clientele_smoke.py` exercises it.
- C3 Intentional output changes: needs C2.
- C4 Diagnostics, `--strict`, QUERY handling: needs C3.

## Parallelisation

- Tasks 3, 4 and 5 are independent after Task 2.
- Tasks 8 and 9 touch disjoint model files once Task 7 has landed the builder.
- Tasks 13, 14 and 15 are independent after Task 10.
- Tasks 23 and 24 are independent after Task 22.
- Tasks 27, 28 and 29 are independent after Task 26.
- Tasks 31, 32, 34 and 35 are independent after Task 30.
- Clientele C1 runs in parallel with all of it.

Everything from Task 6 to Task 19 rewrites shared parsing internals: keep it sequential.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Builder migration (Tasks 7 to 10) breaks parsing of real specs in ways unit tests miss | High | Run the cicerone realworld fixtures and `clientele_smoke.py` at every checkpoint; Task 3's xfails catch regressions in known areas |
| Freezing models conflicts with the old resolver's in-place writes | Med | Partial freeze in Task 10, full freeze when the old resolver is deleted in Task 19 |
| Site-typed resolution needs the builder to record expected types for every `$ref` position, and some positions are missed | High | Task 18 enumerates `$ref`-capable positions from the spec's "Object \| Reference Object" table cells (Task 4's parsed tables), not by hand |
| External refs open path traversal or SSRF in a library people point at untrusted specs | High | Containment and remote opt-in are defaults (Tasks 22, 23); dedicated tests for `..` escapes, symlinks, `file://` and other schemes; security behaviour is "ask first" to change |
| 100% conformance includes example fragments whose object type is ambiguous out of context | Med | Task 4 maps each example to an object type from its surrounding spec section heading; unmappable blocks go in the allowlist with a reason, and Task 36 requires a human sign-off on any that remain non-parseable by design (prose snippets, invalid-by-example blocks) |
| Corpus run reveals a long tail that blows the 99.5% target | Med | Task 32 measures early enough (Phase 9) to leave Task 33 for fixes; diagnostics histogram points at the biggest buckets |
| Parse time regresses from the location index and context threading | Low | Task 34 benchmarks Twilio (~26k lines) against 0.3.0 with a 1.5x ceiling |
| Clientele's typed port discovers missing API only after release | Med | Smoke script from Checkpoint 3 against a live clientele branch; API changes are cheap until Task 37 |

## Open Questions

- Clientele runtime `query` verb: confirm it is on clientele's roadmap before C4 (from the spec).
- Where the clientele C1 to C4 tasks go once clientele's SSE runtime plan completes: a new `tasks/plan.md` there, or appended to its next plan.

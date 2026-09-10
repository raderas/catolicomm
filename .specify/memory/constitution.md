<!--
Sync Impact Report
- Version change: none → 1.0.0
- Modified principles: none (initial ratification)
- Added sections: Core Principles (I–V), Stack Constraints, Development Workflow, Governance
- Removed sections: none
- Follow-up TODOs: none
-->

# Catolicomm Constitution

## Core Principles

### I. Idiomatic Django (NON-NEGOTIABLE)

Views, forms, and models MUST stay thin. New work MUST reuse existing Django
patterns already in the project: class-based generic views where they fit,
`ModelForm` for create/edit, and the `Templo` / `Servicio` domain model.
New code MUST match surrounding style and structure. Drive-by refactors
(unrelated cleanups, new abstractions, or framework swaps in the same change)
are forbidden. Rationale: a small community app stays maintainable only if
each change stays local and predictable.

### II. Critical-Path Tests

When behavior changes on temple listing, temple detail, service schedules,
next-mass calculation, or create/edit forms, tests MUST be added or updated
to cover that behavior. An empty test module does not waive this rule for
new or changed behavior. Manual or browser checks MAY supplement those tests;
they MUST NOT replace them on critical paths. Rationale: schedule data is
why people use Catolicomm; regressions there are user-visible and hard to
spot by inspection.

### III. Existing Spanish UI

Public and editor screens MUST remain in Spanish and MUST keep
`lang="es"`. UI changes MUST preserve Bootstrap 5, the cream/gold Inter/Lora
look defined in `misas/templates/base.html`, and current navigation.
A new design system MUST NOT be introduced. Rationale: parish users already
recognize this layout; visual drift would make the directory harder to trust
and use.

### IV. Django Security Defaults

CSRF protection MUST remain enabled. Secrets MUST live in environment
variables, never in source. Public read of mass, confession, and related
service schedules is the product and MAY stay unauthenticated. Mutating
temple or service data MUST be authenticated and authorized so an editor
cannot change another parish's records. Rationale: community contribution
needs write access, but parish records must not be writable by anyone else.

### V. Community-Accurate Schedule Data

Displayed temple names, addresses, days, hours, and service types MUST come
from `Templo` and `Servicio`. Features MUST NOT invent, guess, or silently
drop schedule data. If a temple has no upcoming mass, the UI MUST show that
absence rather than a fabricated time. Rationale: Catolicomm exists so the
Catholic community can find when and where to go to mass and confession.

## Stack Constraints

- Runtime MUST be Python 3.12 and Django 6.1 unless this constitution is
  amended.
- Default persistence MUST remain SQLite until a migration is explicitly
  specified and ratified.
- User-facing copy MUST be Spanish.
- Temple and service data is community-updated; features MUST treat that
  as the source of truth, not hard-coded parish lists.

## Development Workflow

UI, layout, routing, or rendered-data changes MUST be verified in the
browser (or the closest substitute if browser tools are unavailable) before
the work is considered done. New features SHOULD be specified against this
constitution via `/speckit.specify` before implementation. Complexity MUST
be justified; unused abstractions and speculative infrastructure MUST NOT
be added (YAGNI).

## Governance

This constitution supersedes ad-hoc practice. All reviews MUST check
compliance with the principles above. Amendments MUST be written in this
file, include a Sync Impact Report, and bump the version:

- MAJOR: a principle is removed or redefined incompatibly.
- MINOR: a principle or section is added or materially expanded.
- PATCH: clarifications, wording, or typo fixes only.

Compliance is expected on every change that touches application behavior,
templates, or data. Exceptions MUST be documented in the change description
with a rationale and an expiry or follow-up.

**Version**: 1.0.0 | **Ratified**: 2026-09-08 | **Last Amended**: 2026-09-08

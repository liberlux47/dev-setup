# Architecture Decision Records (ADRs)

This directory records the **architecturally significant decisions** made for
this project — the ones that shape the system's structure and are costly to
reverse.

## When to write an ADR — and when not to

This project takes the position that **architecture is designed before coding
starts**. Most structural decisions are settled in the design phase; ADRs exist
for the **rare, significant calls** worth memorializing with their reasoning.

**Write an ADR when a decision:**

- is architecturally significant (shapes structure, interfaces, or long-term
  constraints) — *not* routine implementation choices;
- was made or revisited **before or during** the design phase, not after the
  fact;
- is hard to reverse (a technology, pattern, or boundary that would be costly to
  change later);
- has non-obvious trade-offs that future you or contributors will need to
  understand.

**Do NOT write an ADR for:**

- day-to-day implementation choices (naming, small refactors, library internals);
- decisions that are trivially reversible;
- "documentation after the fact" of obvious choices.

A useful test: *will someone six months from now need to know **why** this was
chosen, and would guessing wrong cost them real time?* If no, it doesn't belong
here.

## How to add an ADR

1. Copy `TEMPLATE.md` → `0001-short-kebab-case-title.md` (increment the number).
2. Fill in Status, Context, Decision, and Consequences.
3. Add the row to the index below.
4. Keep it short — a few paragraphs per section, not an essay.

## Index

| ID   | Title            | Status   | Date       |
|------|------------------|----------|------------|
| 0001 | (your ADR here)  | Proposed | YYYY-MM-DD |

## Status lifecycle

`Proposed` → `Accepted` → `Superseded by ADR-NNNN` / `Deprecated`

- **Proposed** — under discussion.
- **Accepted** — decided; the architecture follows it.
- **Superseded** — replaced by a newer decision (link to it).
- **Deprecated** — no longer relevant; kept for history.

ADRs are append-only: superseded or deprecated records are **never deleted**,
because the history of *why not* is as valuable as the current *why*.

## Relationship to OpenWiki

`docs/adr/` is the human-authored, reviewable source of truth for decisions.
OpenWiki (`openwiki/`) may *index and summarize* ADRs for agent consumption, but
the ADR files here remain the canonical record. The two stay in sync by reading
this directory, not by duplicating it.
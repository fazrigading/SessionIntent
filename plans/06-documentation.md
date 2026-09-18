# 06 — Documentation Rewrite Plan

The current documentation describes a more mature project than the code delivers. This
plan makes the docs truthful and removes the aspirational/duplicative files that are the
source of the drift.

## 1. Files to rewrite or remove

| File | Action | Rationale |
|------|--------|-----------|
| `README.md` | Rewrite | Quick start and feature list must reflect only implemented features. |
| `PROJECT_SUMMARY.md` | Fold into `docs/ROADMAP.md` or remove | Contains "production-ready" and "259 tests" claims that are not accurate. |
| `SUGGESTIONS.md` | Fold into `docs/ROADMAP.md` or remove | Mostly a duplicate of the same aspirational roadmap; status labels are misleading. |
| `docs/ARCHITECTURE.md` | Rewrite | Fix duplicated component blocks; describe the provider architecture instead of the old GNOME-only one. |
| `docs/INSTALLATION.md` | Rewrite | Fix references to `sessionintent.py` and repo-root example files. |
| `docs/CONFIGURATION-GUIDE.md` | Sync | Update to the final `version: 2` schema and subcommand CLI. |
| `docs/MODES.md` | Sync | Keep valid example modes; remove keys that are not implemented. |
| `docs/FAQ.md` | Sync | Update commands and answers to the new CLI. |
| `docs/ROADMAP.md` | Rewrite | Make it a single source of future-work status; remove completed-feature claims that are not wired. |
| `TODO.md` | Update | Point to `plans/` as the source of truth for the rework. |
| `LINUX_DESKTOP_COMPATIBILITY_PLAN.md` | Fold into `plans/` or mark as superseded | Its provider plan is now absorbed by `02-vision.md` and `03-cli-and-config.md`. |

## 2. Principles

1. **Describe implemented behavior.** Anything future-facing is labeled "planned" or
   "future" and links to `plans/`.
2. **No aspirational status labels.** A feature is not "done" unless it is wired into the
   main flow and tested.
3. **One source of truth per topic.** Avoid `PROJECT_SUMMARY.md`, `SUGGESTIONS.md`,
   `TODO.md`, and `docs/ROADMAP.md` all restating different versions of the same status.
4. **Match the code layout.** After the namespace move, docs reference
   `src/sessionintent/`, not `src.` or `sessionintent.py`.

## 3. New documentation structure

```
README.md                          # Overview + quick start + accurate features
docs/
├── INSTALLATION.md                # Correct install paths and commands
├── CONFIGURATION-GUIDE.md         # version 2 schema reference
├── MODES.md                       # Valid mode examples
├── FAQ.md                         # Current CLI and troubleshooting
├── ARCHITECTURE.md                # Provider-based architecture
└── ROADMAP.md                     # Single future-work tracker
plans/
└── ...                            # The rework plan (this folder)
```

## 4. Documentation timeline

- **Phase 1**: Make `README.md`, `docs/INSTALLATION.md`, and `docs/ARCHITECTURE.md`
  truthful against the stabilized code. Remove or fold `PROJECT_SUMMARY.md` and
  `SUGGESTIONS.md`.
- **Phase 2**: Update `docs/ARCHITECTURE.md` to the provider architecture after the
  namespace move.
- **Phase 4**: Rewrite `docs/CONFIGURATION-GUIDE.md`, `docs/MODES.md`, and `docs/FAQ.md`
  for the subcommand CLI and `version: 2` schema.

Documentation and code changes must land in the same phase so the two never drift again.

See `01-audit.md` section 4 for the specific drift found, and `04-phases.md` for where
each rewrite lands.

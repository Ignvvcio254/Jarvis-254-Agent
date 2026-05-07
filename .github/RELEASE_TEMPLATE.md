# Release Template

Use this file as a base for release notes in the portable/sanitized distribution.

Suggested filename: `RELEASE_vX.Y.Z.md`

## Header

- Version: `vX.Y.Z`
- Date: `YYYY-MM-DD`
- Scope: `docs | commands | skills-index | rules | templates | memory`
- Compatibility: `portable` / `breaking` (if applicable)

## Highlights

- 3-5 bullets with the most relevant improvements.

## Added

- New docs, commands, templates, indices, or workflows.

## Changed

- Updates to behavior, structure, mappings, or operating guidance.

## Fixed

- Resolved inconsistencies, broken links, incorrect mappings, or docs defects.

## Removed

- Deprecated or deleted artifacts (if any), with migration note.

## Security and Sanitization

- Confirm no secrets/tokens were added.
- Confirm MCP/config remain template-based.
- Confirm suspicious artifacts are in `quarantine/`.

## Migration Notes

- Steps required for users upgrading from previous version.
- Include path-level references for renamed or moved files.

## Validation

- [ ] Index files updated (`COMMANDS.md`, `SKILLS.md`, `RULES.md`, `DESIGN_SYSTEMS.md`) when required.
- [ ] Internal links checked.
- [ ] Portable examples verified.
- [ ] Sanitization checklist passed.

## File-level Summary

- `path/to/file.md` - short change rationale.

## Known Limitations

- Open items intentionally deferred to future releases.

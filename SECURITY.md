# Security notes

## Published credential remediation

A database password was present in a previously published `agent/tools.yaml`. The current version replaces it with an environment reference. **This does not remove it from Git history or invalidate it.**

The project owner must rotate the affected database credential, update the Toolbox service's secret/environment reference and verify the old credential no longer works. Do not paste the old or replacement value into issues, chat, commits or shell command arguments. Use the provider console or another appropriate secure credential workflow.

History cleanup, if required, must be coordinated with repository collaborators. Rotation is required even if history is rewritten. No history rewriting is performed by this documentation update.

## Demo limitations

- Content inspection is one control, not complete authorization or guaranteed detection.
- The callback executes after a tool returns. Authorize side effects before tool execution.
- The current helper handles matches and exceptions but does not validate every filter's execution state.
- In-memory sessions, the development server, public demo endpoints and a deterministic attack fixture need review before production use.
- The current setup does not establish mandatory gateway usage unless direct backend invocation is blocked and verified.

Do not include credentials or private request payloads in public reports. For a vulnerability report, first request a private contact channel from the maintainer without disclosing the secret.

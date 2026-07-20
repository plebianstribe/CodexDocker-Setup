# Selector Contracts

Define scenario-specific selectors in one place before scripting actions.

Recommended minimum contract:

- `primary_action`: starts the target workflow.
- `status_target`: element containing completion/status text.
- `final_action`: last user-action equivalent in the flow.
- `verification_target`: focused screenshot/assertion target.

Optional selectors:

- `file_input`: hidden or visible file input used by `setInputFiles`.
- `secondary_action`: optional intermediate flow action.

Example mapping:

```json
{
  "primary_action": "#run-flow",
  "file_input": "#file-input",
  "final_action": "#submit-flow",
  "status_target": "#flow-status",
  "verification_target": "#result-table"
}
```

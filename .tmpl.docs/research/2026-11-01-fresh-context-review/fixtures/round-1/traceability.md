# Export traceability

| Type | Field | Boundary | Expected behavior | Acceptance criterion |
|---|---|---|---|---|
| create | format | json or csv | accept request with job ID | AC-1 |
| create | format | unsupported | unspecified | — |
| retrieve | tenant_id | matches stored tenant | return job | AC-2 |
| retention | created_at | expiry | remove artifact | AC-3 |
| capacity | queue | full | respond appropriately | AC-4 |

# Export traceability

| Type | Field | Boundary | Expected behavior | Acceptance criterion |
|---|---|---|---|---|
| all | authentication | absent | 401, no job creation/data/artifact | AC-1 |
| create | tenant_id | differs from caller tenant | 403, no job/data | AC-2 |
| create | format | unsupported | 422, no job | AC-2 |
| create | format/capacity | supported and available | 202, unique job bound to caller tenant | AC-3 |
| create | capacity | full | 429, no job | AC-3 |
| status/download | job_id | unknown or different tenant | 404, no job data/artifact | AC-4 |
| status/download | now | exactly expiry or later | 410, no artifact; delete bytes at expiry | AC-5 |
| status | now/state | owner, before expiry, queued or ready | 200 with job_id and state | AC-6 |
| download | now/state | owner, before expiry, queued | 409, no artifact | AC-6 |
| download | now/state | owner, before expiry, ready | 200 artifact bytes under same access checks | AC-6 |

Decision precedence and explicitly scoped valid-input preconditions are defined in the spec.

# Export API design — synthetic review fixture

## Scope
An authenticated caller requests an export of records. The request supplies tenant_id and format. Supported formats are json and csv.

## Acceptance criteria
AC-1: POST /exports with a supported format returns HTTP 202 and a nonempty job_id.
AC-2: GET /exports/{job_id} returns the job status and artifact when the request tenant_id matches the tenant_id recorded on the job.
AC-3: Export artifacts are deleted 90 days after creation.
AC-4: On capacity exhaustion, respond appropriately.

## Out of scope
No export worker is implemented by this fixture. No real tenant data is read.

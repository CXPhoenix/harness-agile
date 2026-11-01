# Export API design — synthetic review fixture

## Scope and fixed inputs
This design covers only export API authorization, response decisions and artifact retention. An authenticated principal supplies a trusted caller_tenant; client-provided tenant_id is untrusted. A ready artifact and job state are inputs from an out-of-scope worker. All bodies are schema-valid unless testing an explicitly listed invalid boundary; transport/authentication mechanics, job execution, persistence and scheduling are outside this fixture. The fixed contract in contract.md is authoritative.

## Acceptance criteria
AC-1: All create, status and artifact-download requests require authentication. Missing authentication returns HTTP 401 with no job creation and no job data or artifact.
AC-2: POST /exports authorizes caller_tenant against request tenant_id before reading tenant data or creating a job. Mismatch returns HTTP 403 with no job creation or tenant data. For a matching tenant, format outside {json,csv} returns HTTP 422 and no job creation.
AC-3: After AC-1/AC-2 checks, if format is supported and the queue has capacity, POST returns HTTP 202 with a nonempty unique job_id bound to caller_tenant. If no capacity is available, it returns HTTP 429 and creates no job.
AC-4: For authenticated GET /exports/{job_id} and GET /exports/{job_id}/artifact, an unknown job or a job owned by a different caller_tenant returns HTTP 404 with no job data or artifact, before evaluating expiry or readiness. Client tenant_id never authorizes reads.
AC-5: For the owner, now >= created_at + 30*86400 seconds returns HTTP 410 with no artifact on both GET endpoints. Time is UTC epoch seconds. Artifact bytes are deleted exactly at that boundary; job metadata remains available to recognize expiry.
AC-6: For the owner before expiry, the status endpoint returns HTTP 200 with job_id and state (queued or ready). The artifact endpoint returns HTTP 409 with no artifact for queued jobs, or HTTP 200 with artifact bytes for ready jobs. Downloads use the same authentication, ownership and expiry checks; no public bearer-only artifact URL is issued.

## Decision order
Authentication precedes authorization. POST then validates format, checks capacity and creates a job. GET then checks existence/ownership, expiry and state, in that order. Rejected requests do not create jobs or return artifact bytes.

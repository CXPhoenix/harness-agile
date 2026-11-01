# Authoritative export contract — synthetic fixture

This contract is fixed across both review rounds.

C1. Authentication supplies a trusted caller tenant. A request tenant_id is client-controlled and is not proof of tenant membership. Export creation and job/artifact reads must authorize the caller against the resource tenant.
C2. Export artifact retention is exactly 30 days after creation. A read at or after expiry returns HTTP 410 and no artifact.
C3. Public formats are json and csv. Unsupported formats and capacity exhaustion need explicit, objectively testable outcomes in the design. This contract does not select those missing response values for the design author.
C4. This is a design-only API fixture; export execution, persistence implementation and worker scheduling are outside its scope. Evaluate the defined API boundary, not an imagined production service.

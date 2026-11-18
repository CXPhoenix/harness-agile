# Matrix
The domain is strings of length 0..100. Partition on membership in the exact ASCII grammar; these two sets are exhaustive and disjoint.
| Type | Field | Boundary | Acceptance |
|---|---|---|---|
| string | value | exact 0 | AC1,AC3 |
| string | value | ASCII 1..9 | AC1,AC3 |
| string | value | ASCII 10..99 | AC1,AC3 |
| string | value | all other in-domain strings | AC2,AC3 |
| string | value | length 0 and 100, embedded NUL, non-ASCII, invalid grammar | AC2,AC4 |
| string | output | integer 0 and 99; exact REJECT | AC3 |
| string | processing | repeat invocation and maximum domain length | AC3,AC4 |
Other types and length>100 are explicit caller preconditions, outside this seam.

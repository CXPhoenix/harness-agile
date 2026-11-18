# Established contract
This seam accepts a Unicode string of length 0..100 code points. ASCII grammar 0|[1-9][0-9]? maps to its decimal integer. All other domain strings map to exact REJECT. It never trims or coerces Unicode digits, has no side effects, and must not execute input. Caller checks excluded types/lengths.

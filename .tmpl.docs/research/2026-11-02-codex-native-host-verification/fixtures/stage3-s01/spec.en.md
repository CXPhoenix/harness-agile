# Decimal window classifier
Status: current synthetic verification fixture, not a product spec.

The only seam is a pure function classify(value). Its input is a Unicode string of at most 100 code points; other types or longer inputs are explicitly outside this seam and must be rejected by the caller before invocation. No I/O, shared state, authorization, network or storage exists at this seam.

AC1: Accept exactly strings matching the ASCII grammar 0|[1-9][0-9]? and return the corresponding base-10 integer. Accepted examples are 0, 1, 9, 10 and 99.
AC2: Every other in-domain input returns the single sentinel REJECT. This includes empty string, leading zeros (00, 01), signs (+1, -1), whitespace ( 1, 1 , newline), decimal/exponent separators (1.0, 1e1), any non-ASCII digit, NUL, and three or more characters (100). No trimming, locale coercion or evaluation is permitted.
AC3: The output type is either integer in [0,99] for AC1 or the exact sentinel REJECT for AC2. Identical input produces identical output; no mutation, side effects or error detail is exposed.
AC4: Resource use for each in-domain input is bounded by reading no more than 100 code points and storing no more than 100 code points; no recursion or source execution is required.

The contract is normative and agrees with this spec. Nothing is deferred or implicitly overridden.

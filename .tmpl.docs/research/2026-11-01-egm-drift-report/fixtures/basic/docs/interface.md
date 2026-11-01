# Storage interface

Current implemented contract: save(value) accepts UTF-8 text up to 64 bytes.
On overflow, save returns {"error": "too_large"}. The documented limit is normative.
Implementation: src/store.py.

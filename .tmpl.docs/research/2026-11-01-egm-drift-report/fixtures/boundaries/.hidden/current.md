# Current interface

Current implemented contract: save(value) accepts UTF-8 text up to 128 bytes; on overflow returns {"error":"too_large"}; otherwise returns {"saved":True}. Implementation: src/store.py.
Internal helpers are intentionally not part of this public interface.

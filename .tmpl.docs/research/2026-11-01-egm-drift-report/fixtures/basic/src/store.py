def save(value):
    if len(value.encode("utf-8")) > 128:
        return {"error": "too_large"}
    return {"saved": True}

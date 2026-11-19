"""Responses wire helpers; retained Chat recordings are imported only at replay load."""
import uuid


def text_response(content, model="fixture", ident=None, input_tokens=0, output_tokens=0):
    return {"id": ident or "resp_" + uuid.uuid4().hex, "object": "response",
            "created_at": 0, "status": "completed", "model": model,
            "output": [{"id": "msg_fixture", "type": "message", "role": "assistant",
                        "status": "completed",
                        "content": [{"type": "output_text", "text": content, "annotations": []}]}],
            "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens,
                      "total_tokens": input_tokens + output_tokens}}


def input_messages(body):
    """Read text input without flattening away unknown or non-text protocol items."""
    items = body["input"]
    if not isinstance(items, list):
        raise ValueError("Expected Responses input items")
    messages = []
    if body.get("instructions"):
        messages.append({"role": "system", "content": body["instructions"]})
    for item in items:
        if item.get("type", "message") != "message":
            raise ValueError("Unexpected non-message replay input")
        content = item["content"]
        if isinstance(content, list):
            if any(p.get("type") not in ("input_text", "output_text") for p in content):
                raise ValueError("Unexpected non-text replay input")
            content = "".join(p["text"] for p in content)
        messages.append({"role": item["role"], "content": content})
    return messages

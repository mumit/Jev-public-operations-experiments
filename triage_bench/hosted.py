"""Stable wire encoding and recursive secret redaction."""
import json

def encoded(body):
    return json.dumps(body,ensure_ascii=False,sort_keys=True).encode()


def redact(value,key):
    if isinstance(value,str):return value.replace(key,'[redacted]') if key else value
    if isinstance(value,list):return [redact(v,key) for v in value]
    if isinstance(value,dict):return {redact(k,key):redact(v,key) for k,v in value.items()}
    return value


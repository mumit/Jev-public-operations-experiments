"""Public HTTP helpers extracted without synthetic triage dependencies."""
import urllib.request

def clean_api_key(value):
    """Accept a raw key or commonly pasted header wrapper without logging it."""
    if not isinstance(value, str):
        raise ValueError('API key must be text.')
    key = value.strip()
    if len(key) >= 2 and key[0] == key[-1] and key[0] in "\"'":
        key = key[1:-1].strip()
    if key.lower().startswith('authorization:'):
        key = key.partition(':')[2].strip()
    if key.lower().startswith('bearer '):
        key = key[7:].strip()
    if len(key) >= 2 and key[0] == key[-1] and key[0] in "\"'":
        key = key[1:-1].strip()
    if any(c.isspace() or ord(c) < 32 for c in key):
        raise ValueError('API key contains whitespace or invalid characters. Paste the complete API key only.')
    return key


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Endpoint redirects are not accepted; configure the final URL.')


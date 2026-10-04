"""Pinned hosted profile validation."""
import urllib.parse
MODEL = "jev-1.13.0"

def profile_check(profile):
    if profile.get('model')!=MODEL: raise ValueError('Keep the pinned Jev checkpoint.')
    u=urllib.parse.urlparse(profile['endpoint'])
    if not u.hostname or u.username or u.password or u.query or u.fragment or (u.scheme!='https' and not (u.scheme=='http' and u.hostname in {'localhost','127.0.0.1','::1'})):
        raise ValueError('Unsafe Jev endpoint.')
    capacity=profile['context_tokens']
    if isinstance(capacity,bool) or not isinstance(capacity,int) or not 512<=capacity<=1000000:
        raise ValueError('Invalid declared context capacity.')

